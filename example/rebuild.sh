#!/bin/sh
# Regenerate specs_dashboard.html from docs/specs/*.md
# Run from this directory: ./rebuild.sh
set -e
python3 ../specs_dashboard.py build --title "TodoApp specs"
