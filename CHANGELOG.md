# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] — 2026-05-23

### Breaking

- **`--output` default renamed** from `dashboard.html` to `specs_dashboard.html`. Matches the generator filename for self-consistency, especially when the tool is vendored into a folder named `specs-dashboard/` (where the generic `dashboard.html` artifact sat awkwardly next to the more specific `specs_dashboard.py` script).
- **Migration**: if you have CI / scripts / docs that reference the old `dashboard.html` artifact, either (a) pass `--output dashboard.html` explicitly to preserve the old behavior, or (b) rename your committed output file + update the references to `specs_dashboard.html`. The latter is recommended for new integrations.

### Docs

- README, `example/`, `demo/`, `CONTRIBUTING.md` — all `dashboard.html` references updated to `specs_dashboard.html`.
- `example/dashboard.html` renamed to `example/specs_dashboard.html` and regenerated.

## [1.0.0] — 2026-05-22

Initial public release.

### HTML dashboard

- Single-file output — open in any browser, no server, no build pipeline
- Filter by Status (Shipped / In progress / Draft / Closed / Abandoned / Superseded)
- Search by title or filename
- Sort by title, status, or date
- Click any row to render markdown inline via marked.js (CDN)
- Shipping velocity chart on the landing view

### Terminal CLI

- `specs list [--status X] [--json] [--quiet]` — list specs, optionally filtered by status
- `specs show <filename>` — write a spec's markdown to stdout (pipeable to `glow` / `bat`)
- `specs search <query> [--body]` — substring match against title and filename; add `--body` to also match content
- `specs counts [--json]` — status breakdown
- `specs build` — generate the HTML dashboard

### Convention

- `**Status:**` line below the H1 title declares spec status
- Canonical values: `Shipped <date>`, `In progress`, `Draft`, `Closed <date>`, `Abandoned <date>`, `Superseded by <path>`
- Legacy values (`Completed`, `Live`, `Implemented`, `Pending`, `Planned`) tolerated by default; pass `--no-legacy-aliases` to treat them as `Unknown`
- Autodetect: looks for `docs/specs/` then `specs/`, walking up parent directories from CWD until found or a `.git` boundary is hit (so subfolder invocation works)

### Example project

- `example/` ships with a complete mini-project — 16 sample specs (TodoApp-themed) covering every status bucket, plus `rebuild.sh` and a walkthrough README

### CLI flags

`--input PATH`, `--output PATH`, `--title TEXT`, `--exclude FILENAME` (repeatable), `--no-legacy-aliases`, `--status BUCKET`, `--body`, `--quiet`/`-q`, `--json`
