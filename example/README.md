# Example (no media)

A neutral, invented example of the text files the pipeline produces and reads, for a fictional
60 s video "Three habits that keep my notes useful". No video, audio or image is included.

| File | Step | What it shows |
|---|---|---|
| `cuts.md` | `/sm-montage` | The derush report: durations, cut layers, false starts, the source-to-output diff you re-read |
| `motion/BRIEF-motion.md` | `/sm-motion` step 3 | A filled brief: inputs, direction, zone structure with times read from `words.txt` |
| `motion/index.html` | `/sm-motion` step 1 | The composition exactly as copied from `.claude/skills/sm-motion/template/` (the 79 s STYLE-EXAMPLE world). Step 5 rewrites its zones and its `#beats` JSON from your own `words.txt` |
| `overlays.json` | `/sm-video` subtitles | The hook plus one idea per sentence, with highlighted `**keywords**` |
| `caption.txt` | `/sm-video` caption | The shape of a finished caption |

Copy a file out of here as a starting point, never edit it in place.
