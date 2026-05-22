#!/bin/sh
# Regenerate the CLI demo GIF from cli.tape.
# Requires vhs (brew install vhs).
set -e
cd "$(dirname "$0")"

if ! command -v vhs >/dev/null 2>&1; then
  echo "error: vhs not installed."
  echo "Install with: brew install vhs"
  exit 1
fi

vhs cli.tape
echo ""
echo "Wrote $(pwd)/cli.gif"
