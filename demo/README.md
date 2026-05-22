# Demo GIFs

Two GIFs live here:

- `cli.gif` — scripted recording of the terminal CLI subcommands (`counts`, `list`, `show`, `build`). Reproducible via [`vhs`](https://github.com/charmbracelet/vhs).
- `dashboard.gif` — manual recording of the HTML dashboard in a browser (chip filtering, search, click-to-render). Recorded with [Kap](https://getkap.co/) or any screen recorder, then encoded with ffmpeg.

GitHub-rendered markdown strips `<video>` tags with repo-relative `src`, so we use GIF for inline playback in the top-level README.

## Regenerate the CLI gif

```
brew install vhs
./regenerate.sh
```

`regenerate.sh` runs `vhs cli.tape` and writes `cli.gif` here.

## Record the browser demo

There's no scripted equivalent for the browser. Suggested workflow:

1. Open `../example/dashboard.html` in your browser
2. Launch Kap (`brew install --cask kap`) → Record selected area → frame the browser window
3. Walk through the demo storyboard:
   - Click "In progress" chip → list narrows
   - Click "Draft" → narrows to different specs
   - Click "All" → restored
   - Type `auth` in the search box → list narrows to auth specs
   - Click a row → markdown renders on the right
   - Scroll the right pane to show the body
4. Stop recording, export as `.mov` or `.mp4`.
5. Encode to a compact GIF using a two-pass palette (much smaller than single-pass):

   ```
   ffmpeg -i dashboard.mov -vf "fps=12,scale=800:-1:flags=lanczos,palettegen" -y palette.png
   ffmpeg -i dashboard.mov -i palette.png -filter_complex "fps=12,scale=800:-1:flags=lanczos [x]; [x][1:v] paletteuse" -y dashboard.gif
   ```

   - 12 fps and 800px width keep the file small while staying readable
   - Two-pass palette gives ~5× smaller output than single-pass at the same visual quality

6. Delete the intermediate recording + palette. Commit `dashboard.gif`. Aim for under 5 MB.

The top-level README references `dashboard.gif` via standard markdown image syntax.
