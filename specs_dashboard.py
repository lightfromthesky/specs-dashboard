#!/usr/bin/env python3
"""
specs-dashboard — browse a directory of markdown spec files, either
as a single-file HTML page (`build`) or directly from the terminal
(`list`, `show`, `search`, `counts`).

Examples:

    # Generate the HTML dashboard
    python3 specs_dashboard.py build --input docs/specs --output dashboard.html

    # Terminal CLI
    python3 specs_dashboard.py list                              # All specs
    python3 specs_dashboard.py list --status shipped             # Filter
    python3 specs_dashboard.py list --status "in progress"       # Multi-word status
    python3 specs_dashboard.py search "auth"                     # Match in title
    python3 specs_dashboard.py show two-factor-auth              # Render to stdout
    python3 specs_dashboard.py counts                            # Status breakdown

`show` writes raw markdown to stdout; pipe through `glow`, `bat -l md`,
or `mdcat` for nicer terminal rendering.

Status convention expected at the top of every spec file:

    # Spec title

    **Status:** Shipped 2026-01-15

Recognised values: Shipped <date>, In progress, Draft, Closed <date>,
Abandoned <date>, Superseded by <path>.

Legacy values (Completed, Live, Implemented, Pending, Planned) are
tolerated by default and mapped to the canonical buckets. Pass
--no-legacy-aliases to treat them as Unknown.

License: MIT.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

STATUS_LINE_RE = re.compile(r"^\s*\*\*Status:\*\*\s*(.+?)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^# (.+?)\s*$", re.MULTILINE)
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def classify_status(raw: str, legacy_aliases: bool) -> tuple[str, str | None]:
    """Map a raw `**Status:**` value to (bucket, date).

    Bucket is one of: Shipped, In progress, Draft, Closed, Abandoned,
    Superseded, Unknown. Date is the first YYYY-MM-DD found in the
    value, or None.
    """
    lower = raw.lower()
    date_match = DATE_RE.search(raw)
    date = date_match.group(1) if date_match else None
    if lower.startswith("shipped"):
        return "Shipped", date
    if lower.startswith("in progress"):
        return "In progress", date
    if lower.startswith("draft"):
        return "Draft", date
    if lower.startswith("closed"):
        return "Closed", date
    if lower.startswith("abandoned"):
        return "Abandoned", date
    if lower.startswith("superseded"):
        return "Superseded", date
    if legacy_aliases:
        if lower.startswith(("completed", "live", "implemented")):
            return "Shipped", date
        if lower.startswith(("pending", "planned")):
            return "Draft", date
    return "Unknown", date


def parse_spec(path: Path, legacy_aliases: bool) -> dict | None:
    text = path.read_text()
    title_match = TITLE_RE.search(text)
    if not title_match:
        return None
    title = title_match.group(1).strip()
    # Only consider Status lines in the first 30 lines so a "Status:"
    # appearing inside a deep Implementation section doesn't shadow
    # the canonical top-of-file value.
    head = "\n".join(text.splitlines()[:30])
    status_match = STATUS_LINE_RE.search(head)
    raw_status = status_match.group(1).strip() if status_match else ""
    bucket, date = classify_status(raw_status, legacy_aliases)
    return {
        "filename": path.name,
        "title": title,
        "raw_status": raw_status,
        "bucket": bucket,
        "date": date or "",
        "body": text,
    }


def build(
    input_dir: Path,
    output: Path,
    title: str,
    excludes: set[str],
    legacy_aliases: bool,
) -> None:
    specs = _load_specs(input_dir, excludes, legacy_aliases)

    counts: dict[str, int] = {}
    for s in specs:
        counts[s["bucket"]] = counts.get(s["bucket"], 0) + 1

    data_json = json.dumps(specs, separators=(",", ":"))
    # Embed-safety for `<script type="application/json">`: escape every
    # `<` to its JSON Unicode form so the HTML parser never sees a
    # `</script>` (or `<!--`) inside the data block. `<` is valid
    # JSON; JSON.parse decodes it back to `<` in the parsed strings.
    data_json_safe = data_json.replace("<", "\\u003c")

    html = HTML_TEMPLATE
    html = html.replace("__TITLE__", title)
    html = html.replace("__DATA__", data_json_safe)
    html = html.replace("__GENERATED_AT__", dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    html = html.replace("__TOTAL__", str(len(specs)))
    html = html.replace("__COUNTS_JSON__", json.dumps(counts))
    html = html.replace("__INPUT_DIR__", str(input_dir))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html)
    size_kb = len(html) // 1024
    print(f"Wrote {output} ({len(specs)} specs, {size_kb:,} KB)")
    for bucket, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {bucket:14} {n}")


# Autodetect order when --input is not explicitly passed. The first
# existing directory wins. `docs/specs/` is the recommended convention
# (specs are documentation; lives under the canonical docs tree);
# `specs/` at the repo root is the alternate for AI-agent-discoverability-
# focused projects that want their specs at eye level.
AUTODETECT_PATHS = (Path("docs/specs"), Path("specs"))


def _resolve_input(input_arg: Path | None) -> Path:
    """Return the resolved input directory or exit with a helpful message.

    Walks up from the current working directory looking for an autodetect
    candidate at each level, so running from a subfolder (e.g.
    `tools/specs-dashboard/`) still finds `docs/specs/` at the repo root.
    Stops at a `.git` boundary (don't escape the current repo) or the
    filesystem root.
    """
    if input_arg is not None:
        if not input_arg.is_dir():
            sys.exit(f"error: --input directory not found: {input_arg}")
        return input_arg
    current = Path.cwd().resolve()
    while True:
        for candidate in AUTODETECT_PATHS:
            full = current / candidate
            if full.is_dir():
                return full
        if (current / ".git").exists() or current.parent == current:
            break
        current = current.parent
    tried = ", ".join(str(p) for p in AUTODETECT_PATHS)
    sys.exit(
        f"error: no specs directory found.\n"
        f"  Tried: {tried} (walked up from {Path.cwd()})\n"
        f"  Either create one of those directories, or pass --input PATH explicitly."
    )


def _load_specs(
    input_dir: Path,
    excludes: set[str],
    legacy_aliases: bool,
) -> list[dict]:
    """Shared loader used by every subcommand."""
    specs: list[dict] = []
    for md in sorted(input_dir.glob("*.md")):
        if md.name in excludes:
            continue
        parsed = parse_spec(md, legacy_aliases)
        if parsed:
            specs.append(parsed)
    return specs


def _normalize_status(status: str) -> str:
    """Lowercase + collapse-whitespace a status string for comparison."""
    return " ".join(status.lower().split())


def cmd_list(args: argparse.Namespace) -> None:
    input_dir = _resolve_input(args.input)
    specs = _load_specs(input_dir, set(args.exclude), args.legacy_aliases)
    if args.status:
        wanted = _normalize_status(args.status)
        specs = [s for s in specs if _normalize_status(s["bucket"]) == wanted]
    specs.sort(key=lambda s: (s["bucket"], s["date"] or "", s["title"]))
    if args.quiet:
        for s in specs:
            print(s["filename"])
        return
    if args.json:
        json.dump([{k: s[k] for k in ("filename", "title", "bucket", "date", "raw_status")} for s in specs], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    # Default tabular output.
    width_title = min(60, max((len(s["title"]) for s in specs), default=0))
    for s in specs:
        date = s["date"] or "—"
        print(f"{s['bucket']:<13}  {date:<10}  {s['title'][:width_title]:<{width_title}}  {s['filename']}")


def cmd_show(args: argparse.Namespace) -> None:
    input_dir = _resolve_input(args.input)
    specs = _load_specs(input_dir, set(args.exclude), args.legacy_aliases)
    name = args.filename
    # Allow either "two-factor-auth" or "two-factor-auth.md".
    candidates = [s for s in specs if s["filename"] == name or s["filename"] == name + ".md"]
    if not candidates:
        sys.exit(f"error: no spec matching {name!r} (try `list` to see filenames)")
    if len(candidates) > 1:
        sys.exit(f"error: multiple specs match {name!r}: {[s['filename'] for s in candidates]}")
    sys.stdout.write(candidates[0]["body"])
    if not candidates[0]["body"].endswith("\n"):
        sys.stdout.write("\n")


def cmd_search(args: argparse.Namespace) -> None:
    input_dir = _resolve_input(args.input)
    specs = _load_specs(input_dir, set(args.exclude), args.legacy_aliases)
    q = args.query.lower()
    fields = ("title", "filename")
    if args.body:
        fields = ("title", "filename", "body")
    matches = [s for s in specs if any(q in s[f].lower() for f in fields)]
    matches.sort(key=lambda s: s["title"])
    if args.quiet:
        for s in matches:
            print(s["filename"])
        return
    for s in matches:
        date = s["date"] or "—"
        print(f"{s['bucket']:<13}  {date:<10}  {s['title']:<60}  {s['filename']}")
    if not matches:
        sys.exit(1)


def cmd_counts(args: argparse.Namespace) -> None:
    input_dir = _resolve_input(args.input)
    specs = _load_specs(input_dir, set(args.exclude), args.legacy_aliases)
    counts: dict[str, int] = {}
    for s in specs:
        counts[s["bucket"]] = counts.get(s["bucket"], 0) + 1
    if args.json:
        json.dump(counts, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    total = sum(counts.values())
    for bucket, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {bucket:<13} {n}")
    print(f"  {'Total':<13} {total}")


def cmd_build(args: argparse.Namespace) -> None:
    input_dir = _resolve_input(args.input)
    build(
        input_dir=input_dir,
        output=args.output,
        title=args.title,
        excludes=set(args.exclude),
        legacy_aliases=args.legacy_aliases,
    )


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Directory containing the *.md spec files. "
        "Autodetected from docs/specs/ then specs/ if not specified.",
    )
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="FILENAME",
        help="Skip this filename (repeatable). Useful for SPEC_TEMPLATE.md.",
    )
    p.add_argument(
        "--no-legacy-aliases",
        dest="legacy_aliases",
        action="store_false",
        help="Treat Completed/Live/Implemented/Pending/Planned as Unknown.",
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Browse a directory of markdown spec files via HTML dashboard or CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", metavar="COMMAND")
    sub.required = True

    # build
    p_build = sub.add_parser("build", help="Generate the HTML dashboard")
    _add_common_args(p_build)
    p_build.add_argument(
        "--output",
        type=Path,
        default=Path("dashboard.html"),
        help="Output HTML path (default: dashboard.html)",
    )
    p_build.add_argument(
        "--title",
        default="Specs dashboard",
        help="Page title (default: 'Specs dashboard')",
    )
    p_build.set_defaults(func=cmd_build)

    # list
    p_list = sub.add_parser("list", help="List specs, optionally filtered by status")
    _add_common_args(p_list)
    p_list.add_argument("--status", help="Filter to one bucket (case-insensitive)")
    p_list.add_argument("--quiet", "-q", action="store_true", help="Filename per line only")
    p_list.add_argument("--json", action="store_true", help="JSON output")
    p_list.set_defaults(func=cmd_list)

    # show
    p_show = sub.add_parser("show", help="Write a spec's markdown to stdout")
    _add_common_args(p_show)
    p_show.add_argument("filename", help="Spec name (with or without .md)")
    p_show.set_defaults(func=cmd_show)

    # search
    p_search = sub.add_parser("search", help="Search specs by title (or body with --body)")
    _add_common_args(p_search)
    p_search.add_argument("query", help="Substring to match (case-insensitive)")
    p_search.add_argument("--body", action="store_true", help="Also match in spec body")
    p_search.add_argument("--quiet", "-q", action="store_true", help="Filename per line only")
    p_search.set_defaults(func=cmd_search)

    # counts
    p_counts = sub.add_parser("counts", help="Print a count per status bucket")
    _add_common_args(p_counts)
    p_counts.add_argument("--json", action="store_true", help="JSON output")
    p_counts.set_defaults(func=cmd_counts)

    args = parser.parse_args(argv)
    args.func(args)


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root {
    --bg: #f7f8fa;
    --panel: #ffffff;
    --border: #e3e6eb;
    --text: #16181d;
    --muted: #6b7280;
    --accent: #2563eb;
    --row-hover: #f0f4ff;
    --chip-bg: #eef2f7;
    --chip-active-bg: #2563eb;
    --chip-active-fg: #ffffff;
    --status-shipped: #10b981;
    --status-in-progress: #f59e0b;
    --status-draft: #6b7280;
    --status-closed: #6366f1;
    --status-abandoned: #ef4444;
    --status-superseded: #8b5cf6;
    --status-unknown: #9ca3af;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    color: var(--text);
    background: var(--bg);
    font-size: 14px;
    line-height: 1.5;
  }
  header {
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    padding: 16px 40px;
  }
  header h1 {
    margin: 0 0 4px 0;
    font-size: 18px;
    font-weight: 600;
  }
  header .meta {
    color: var(--muted);
    font-size: 12px;
  }
  .controls {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 12px 40px;
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
  }
  .chip {
    cursor: pointer;
    padding: 4px 12px;
    border-radius: 16px;
    background: var(--chip-bg);
    color: var(--text);
    font-size: 12px;
    user-select: none;
    transition: background 0.1s;
  }
  .chip:hover { background: #dde4ee; }
  .chip.active {
    background: var(--chip-active-bg);
    color: var(--chip-active-fg);
  }
  .chip .n { opacity: 0.6; margin-left: 4px; }
  .chip.active .n { opacity: 0.8; }
  input[type=search] {
    flex: 1;
    min-width: 200px;
    max-width: 320px;
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font: inherit;
    margin-left: auto;
  }
  .layout {
    display: grid;
    grid-template-columns: minmax(300px, 1fr) minmax(400px, 2fr);
    gap: 0;
    height: calc(100vh - 100px);
  }
  .list-pane {
    overflow-y: auto;
    border-right: 1px solid var(--border);
    background: var(--panel);
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    text-align: left;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
  }
  th:first-child, td:first-child { padding-left: 40px; }
  th:last-child, td:last-child { padding-right: 40px; }
  th {
    position: sticky;
    top: 0;
    background: var(--panel);
    z-index: 1;
    cursor: pointer;
    user-select: none;
    font-weight: 600;
  }
  th:hover { background: #f0f4ff; }
  tbody tr { cursor: pointer; }
  tbody tr:hover { background: var(--row-hover); }
  tbody tr.selected { background: #dbe6ff; }
  .status-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    color: white;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
  }
  .status-Shipped { background: var(--status-shipped); }
  .status-Inprogress { background: var(--status-in-progress); }
  .status-Draft { background: var(--status-draft); }
  .status-Closed { background: var(--status-closed); }
  .status-Abandoned { background: var(--status-abandoned); }
  .status-Superseded { background: var(--status-superseded); }
  .status-Unknown { background: var(--status-unknown); }
  .reader-pane {
    overflow-y: auto;
    padding: 24px 40px;
    background: var(--panel);
  }
  .reader-pane .placeholder {
    color: var(--muted);
    text-align: center;
    margin-top: 80px;
  }
  .velocity-section {
    margin: 120px 0 0;
    text-align: left;
  }
  .velocity-heading {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    margin-bottom: 12px;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--border);
  }
  .velocity-chart {
    display: flex;
    gap: 8px;
    align-items: stretch;
  }
  .velocity-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    min-width: 0;
  }
  .velocity-count {
    font-size: 12px;
    color: var(--text);
    text-align: center;
    height: 18px;
    line-height: 18px;
    font-weight: 500;
  }
  .velocity-stem {
    display: flex;
    align-items: flex-end;
    height: 240px;
  }
  .velocity-fill {
    width: 100%;
    background: var(--status-shipped);
    border-radius: 2px 2px 0 0;
    min-height: 1px;
  }
  .velocity-col[data-empty="1"] .velocity-fill { background: var(--border); }
  .velocity-label {
    font-size: 11px;
    color: var(--muted);
    text-align: center;
    margin-top: 6px;
    white-space: nowrap;
  }
  .reader-pane h1, .reader-pane h2, .reader-pane h3, .reader-pane h4 {
    margin-top: 1.4em;
    margin-bottom: 0.4em;
    font-weight: 600;
  }
  .reader-pane h1 { font-size: 22px; }
  .reader-pane h2 { font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 4px; }
  .reader-pane h3 { font-size: 15px; }
  .reader-pane code {
    background: #f0f2f5;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 12px;
    font-family: "SF Mono", Menlo, Consolas, monospace;
  }
  .reader-pane pre {
    background: #f6f8fa;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: "SF Mono", Menlo, Consolas, monospace;
    font-size: 12px;
  }
  .reader-pane pre code { background: none; padding: 0; }
  .reader-pane table { margin: 8px 0; }
  .reader-pane th, .reader-pane td { border: 1px solid var(--border); }
  .reader-pane blockquote {
    border-left: 3px solid var(--border);
    margin-left: 0;
    padding-left: 12px;
    color: var(--muted);
  }
  .reader-pane a { color: var(--accent); text-decoration: none; }
  .reader-pane a:hover { text-decoration: underline; }
  .reader-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
  }
  .reader-header .file {
    color: var(--muted);
    font-size: 12px;
    font-family: "SF Mono", Menlo, Consolas, monospace;
  }
  .empty-row {
    color: var(--muted);
    text-align: center;
    padding: 40px 0;
  }
</style>
</head>
<body>

<header>
  <h1>__TITLE__</h1>
  <div class="meta">
    <span id="meta-total"></span>
    · from <code>__INPUT_DIR__</code>
    · generated <span id="meta-gen">__GENERATED_AT__</span>
  </div>
</header>

<div class="controls">
  <span class="chip active" data-bucket="">All<span class="n" id="n-all"></span></span>
  <span class="chip" data-bucket="Shipped">Shipped<span class="n" id="n-Shipped"></span></span>
  <span class="chip" data-bucket="In progress">In progress<span class="n" id="n-Inprogress"></span></span>
  <span class="chip" data-bucket="Draft">Draft<span class="n" id="n-Draft"></span></span>
  <span class="chip" data-bucket="Closed">Closed<span class="n" id="n-Closed"></span></span>
  <span class="chip" data-bucket="Abandoned">Abandoned<span class="n" id="n-Abandoned"></span></span>
  <span class="chip" data-bucket="Superseded">Superseded<span class="n" id="n-Superseded"></span></span>
  <span class="chip" data-bucket="Unknown">Unknown<span class="n" id="n-Unknown"></span></span>
  <input id="search" type="search" placeholder="Filter by title…" autocomplete="off">
</div>

<div class="layout">
  <div class="list-pane">
    <table>
      <thead>
        <tr>
          <th data-sort="title">Spec</th>
          <th data-sort="bucket">Status</th>
          <th data-sort="date">Date</th>
        </tr>
      </thead>
      <tbody id="rows"></tbody>
    </table>
  </div>
  <div class="reader-pane">
    <div id="reader" class="placeholder">
      <div>📄 Pick a spec to read it here.</div>
      <div class="velocity-section">
        <div class="velocity-heading">Shipping velocity</div>
        <div id="velocity-chart" class="velocity-chart"></div>
      </div>
    </div>
  </div>
</div>

<script id="specs-data" type="application/json">__DATA__</script>
<script src="https://cdn.jsdelivr.net/npm/marked@13.0.3/marked.min.js"></script>
<script>
  const SPECS = JSON.parse(document.getElementById('specs-data').textContent);
  const COUNTS = __COUNTS_JSON__;
  const TOTAL = __TOTAL__;

  document.getElementById('n-all').textContent = ` ${TOTAL}`;
  for (const [bucket, n] of Object.entries(COUNTS)) {
    const id = `n-${bucket.replace(/\s+/g, '')}`;
    const el = document.getElementById(id);
    if (el) el.textContent = ` ${n}`;
  }
  document.getElementById('meta-total').textContent = `${TOTAL} specs`;

  let filterBucket = '';
  let searchQ = '';
  let sortKey = 'date';
  let sortDir = -1;
  let selectedFile = null;

  const rowsEl = document.getElementById('rows');
  const readerEl = document.getElementById('reader');

  function render() {
    let list = SPECS.slice();
    if (filterBucket) list = list.filter(s => s.bucket === filterBucket);
    if (searchQ) {
      const q = searchQ.toLowerCase();
      list = list.filter(s =>
        s.title.toLowerCase().includes(q) ||
        s.filename.toLowerCase().includes(q)
      );
    }
    list.sort((a, b) => {
      const av = a[sortKey] || '';
      const bv = b[sortKey] || '';
      if (av < bv) return -1 * sortDir;
      if (av > bv) return 1 * sortDir;
      return 0;
    });

    if (!list.length) {
      rowsEl.innerHTML = '<tr><td colspan="3" class="empty-row">No specs match.</td></tr>';
      return;
    }
    rowsEl.innerHTML = list.map(s => `
      <tr data-file="${escapeHtml(s.filename)}" class="${s.filename === selectedFile ? 'selected' : ''}">
        <td>${escapeHtml(s.title)}</td>
        <td><span class="status-badge status-${s.bucket.replace(/\s+/g, '')}">${escapeHtml(s.bucket)}${s.date ? ' ' + s.date : ''}</span></td>
        <td>${escapeHtml(s.date || '—')}</td>
      </tr>
    `).join('');

    for (const tr of rowsEl.querySelectorAll('tr')) {
      tr.addEventListener('click', () => selectSpec(tr.dataset.file));
    }
  }

  function selectSpec(filename) {
    selectedFile = filename;
    const spec = SPECS.find(s => s.filename === filename);
    if (!spec) return;
    readerEl.classList.remove('placeholder');
    readerEl.innerHTML = `
      <div class="reader-header">
        <span class="status-badge status-${spec.bucket.replace(/\s+/g, '')}">${escapeHtml(spec.bucket)}${spec.date ? ' ' + spec.date : ''}</span>
        <span class="file">${escapeHtml(spec.filename)}</span>
      </div>
      <div id="rendered"></div>
    `;
    document.getElementById('rendered').innerHTML = marked.parse(spec.body);
    render();
    document.querySelector('.reader-pane').scrollTop = 0;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  for (const chip of document.querySelectorAll('.chip')) {
    chip.addEventListener('click', () => {
      for (const c of document.querySelectorAll('.chip')) c.classList.remove('active');
      chip.classList.add('active');
      filterBucket = chip.dataset.bucket;
      render();
    });
  }

  document.getElementById('search').addEventListener('input', e => {
    searchQ = e.target.value;
    render();
  });

  for (const th of document.querySelectorAll('th[data-sort]')) {
    th.addEventListener('click', () => {
      const key = th.dataset.sort;
      if (sortKey === key) sortDir = -sortDir;
      else { sortKey = key; sortDir = key === 'date' ? -1 : 1; }
      render();
    });
  }

  function renderVelocity() {
    const chart = document.getElementById('velocity-chart');
    if (!chart) return;
    const now = new Date();
    const months = [];
    for (let i = 11; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const ym = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      months.push({ ym, label: d.toLocaleString('en', { month: 'short' }), count: 0 });
    }
    for (const s of SPECS) {
      if (s.bucket !== 'Shipped' || !s.date) continue;
      const m = months.find(x => x.ym === s.date.slice(0, 7));
      if (m) m.count++;
    }
    const max = Math.max(1, ...months.map(m => m.count));
    chart.innerHTML = months.map(m => `
      <div class="velocity-col" data-empty="${m.count ? 0 : 1}" title="${m.ym}: ${m.count} shipped">
        <div class="velocity-count">${m.count || ''}</div>
        <div class="velocity-stem"><div class="velocity-fill" style="height: ${m.count ? (m.count / max * 100) : 6}%"></div></div>
        <div class="velocity-label">${m.label}</div>
      </div>
    `).join('');
  }

  render();
  renderVelocity();
</script>

</body>
</html>
"""


if __name__ == "__main__":
    main()
