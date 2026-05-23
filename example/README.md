# Example: TodoApp specs

A sample project laid out the way a real project using specs-dashboard would look.

## What's here

```
example/
├── README.md          ← this file
├── specs_dashboard.html     ← pre-built, double-click to open
├── docs/
│   └── specs/         ← 18 example specs covering every status bucket
└── rebuild.sh         ← one-liner to regenerate specs_dashboard.html from specs/
```

The 18 specs describe a fictional TodoApp's design history — shipped features, in-flight work, drafts, planned-but-not-started work, an abandoned approach, a closed (shipped-then-reverted) experiment, and a superseded design. They're written to feel like real specs from a small-to-mid engineering team.

## See it work

From this directory:

```
open specs_dashboard.html
```

The browser opens the dashboard with all 18 specs loaded. Click the status chips at the top to filter; click any row to read that spec inline on the right.

> The top-level README says don't commit the generated HTML in your own project — that's right advice for consumer repos. We commit it here in `example/` so anyone browsing this repo can preview the dashboard without cloning or running anything.

## Regenerate after edits

If you edit any spec under `docs/specs/`, regenerate the dashboard:

```
./rebuild.sh
```

Or use the tool directly:

```
python3 ../specs_dashboard.py build --title "Specs Dashboard"
```

(`--input` is autodetected — the tool finds `docs/specs/` in the current directory automatically.)

## Try the CLI

```
python3 ../specs_dashboard.py counts
python3 ../specs_dashboard.py list --status "in progress"
python3 ../specs_dashboard.py show realtime-sync
python3 ../specs_dashboard.py search collaborative
```

## Use this as a starting point

Copy the `docs/specs/` directory structure into your own project, write your own specs following the convention shown in any of the example files, then run `specs_dashboard.py build` from your project root.
