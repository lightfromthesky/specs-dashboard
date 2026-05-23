# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] — 2026-05-22

Initial public release.

### HTML dashboard

- Single-file output — open in any browser, no server, no build pipeline
- Filter by Status (Shipped / In progress / Draft / Planned / Closed / Abandoned / Superseded)
- Search by title or filename
- Sort by title, status, or date
- Click any row to render markdown inline via marked.js (CDN)
- Shipping velocity chart on the landing view

### Terminal CLI

- `specs list [--status X] [--json] [--quiet]` — list specs, optionally filtered by status
- `specs show <filename>` — write a spec's markdown to stdout (pipeable to `glow` / `bat`)
- `specs search <query> [--body]` — substring match against title and filename; add `--body` to also match content
- `specs counts [--json]` — status breakdown
- `specs build` — generate a self-contained HTML dashboard snapshot
- `specs serve` — run a local HTTP server that reads specs at request time (live mode, no regen step); idle-timeout watchdog auto-shuts the server down after a configurable window with no requests

### Convention

- `**Status:**` line below the H1 title declares spec status
- Canonical values: `Shipped <date>`, `In progress`, `Draft`, `Planned`, `Closed <date>`, `Abandoned <date>`, `Superseded by <path>`
- Legacy values (`Completed`, `Live`, `Implemented`, `Pending`) tolerated by default; pass `--no-legacy-aliases` to treat them as `Unknown`
- Autodetect: looks for `docs/specs/` then `specs/`, walking up parent directories from CWD until found or a `.git` boundary is hit (so subfolder invocation works)

### Example project

- `example/` ships with a complete mini-project — 16 sample specs (TodoApp-themed) covering every status bucket, plus `rebuild.sh` and a walkthrough README

### CLI flags

`--input PATH`, `--output PATH` (default: `specs_dashboard.html`), `--title TEXT`, `--exclude FILENAME` (repeatable), `--no-legacy-aliases`, `--port PORT` (default: 8080), `--idle-timeout SECONDS` (default: 3600), `--no-idle-timeout`, `--no-browser`, `--status BUCKET`, `--body`, `--quiet`/`-q`, `--json`
