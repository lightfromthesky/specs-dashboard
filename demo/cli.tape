# vhs tape for the CLI demo GIF.
#
# Regenerate locally with:
#     brew install vhs
#     cd demo && ./regenerate.sh
# (or `vhs cli.tape` directly from this directory).
#
# Output: demo/cli.gif

Output cli.gif

Set FontSize 16
Set Width 1280
Set Height 720
Set Theme "Dracula"
Set TypingSpeed 60ms
Set Padding 12

# Setup — run from this directory; cd into the example project so the
# autodetect picks up its docs/specs/. Clear the screen so the first
# visible frame is a clean prompt.
Hide
Type "cd ../example"
Enter
Sleep 200ms
Type "clear"
Enter
Show

Sleep 800ms

# 1) counts — status breakdown
Type "python3 ../specs_dashboard.py counts"
Sleep 300ms
Enter
Sleep 4000ms

# 2) list filtered by status
Type "python3 ../specs_dashboard.py list --status 'in progress'"
Sleep 300ms
Enter
Sleep 2500ms

# 3) show a spec body — piped to head for brevity
Type "python3 ../specs_dashboard.py show realtime-sync | head -15"
Sleep 300ms
Enter
Sleep 4500ms

# 4) build the HTML dashboard
Type "python3 ../specs_dashboard.py build --title 'TodoApp specs'"
Sleep 300ms
Enter
Sleep 3000ms
