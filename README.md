# Social Media Video Pipeline

You talk to the camera and hand the raw take to Claude Code. Claude derushes it (cuts silences, fillers, false starts), lets you validate the cuts, picks a colour look, generates motion graphics with [HyperFrames](https://github.com/heygen-com/hyperframes) (HTML rendered to video) timed word by word on your voice from the effects you wrote in your script, burns dynamic subtitles, writes the caption and exports a vertical 1080x1920 video. Nothing is ever published for you.

Skills and notes are written in French (the pipeline was built for French speech; `--lang en` works for English takes). Un résumé en français est à la fin.

## What is in here

```
.claude/skills/   sm-video (the whole chain), then one skill per step: sm-recherche, sm-montage (+ derush),
                  sm-etalonnage, sm-motion, sm-soustitres, sm-caption, sm-export
.claude/agents/   motion-reviewer (one Sonnet review before render)
outils/           video (status/validate/export), look.py, overlays.py, plafond.py, deband.py, installer.sh, fonts/
videos/           one folder per video (media is gitignored), README.md = the spec
example/          neutral text-only example (cuts report, motion brief, overlays, caption)
STYLE.md          your tone and bans, filled in once; Claude rereads captions against it
```

## Prerequisites

- [Claude Code](https://claude.com/claude-code) (CLI, or the Desktop app "Code" tab), with a Claude plan that includes Claude Code
- The HyperFrames skills, needed by `/sm-motion`: `npx skills add heygen-com/hyperframes --all` (or the plugin: `claude plugin marketplace add heygen-com/hyperframes` then `claude plugin install hyperframes@hyperframes`). HyperFrames itself is fetched by `npx` at the first render, and so is the headless Chrome it renders with: the first render needs internet
- `ffmpeg` + `ffprobe`, `python3` (3.10+), `uv`, `node` 22+ (for `npx hyperframes`)
- [OpenAI Whisper](https://github.com/openai/whisper) on the PATH (`uv tool install openai-whisper`, or `export WHISPER=/path/to/whisper`); `torch` + `torchaudio` for the word alignment
- Python modules: numpy, opencv-python, pillow, soundfile, fonttools (the installer adds them with `uv`)
- Optional: DaVinci Resolve (free is enough). It brings two things: the film-look LUTs read by `outils/look.py` (without it the colour step only offers A, neutral), and hand-editing of the cuts through the `.fcpxml` timeline. The cuts themselves are made by ffmpeg, not by Resolve
- Optional: your own sound folder `SFX_DIR` (see Sounds)
- Tested on macOS (Apple Silicon). Linux should work (`xdg-open` instead of `open`) but has not been tested

## Install

```bash
git clone https://github.com/aion88/social-media-video-pipeline.git && cd social-media-video-pipeline
outils/installer.sh --verifier   # prints OK / MANQUE lines, touches nothing
outils/installer.sh              # installs the light python modules via uv
outils/installer.sh --lier       # optional: link the skills into ~/.claude/skills and derush into ~/.local/bin
```

Open the folder in Claude Code: the skills are loaded from `.claude/skills/`. Then fill in `STYLE.md`.

## Quick start: your first video

1. Film one take, vertical, in one go. Keep your script (with your effects, see below) in a text file.
2. In Claude Code, from the repo folder: `/sm-montage ~/Downloads/my_take.mov`. The take moves to `videos/my_take/`. Its file name without extension, here `my_take`, is the **STEM**: every later command takes it.
3. Give Claude your script: paste it, or save it as `videos/my_take/NOTES-REPRISE.md` (`/sm-recherche` writes this file for you if you start with research).
4. Then just run `/sm-video my_take` and answer when it stops: validate the cuts, pick a look, validate the motion, the subtitles, the caption. At the end, `videos/my_take/final/` holds the video, `caption.txt` and `thumbnail.png`.

`outils/video statut my_take` tells you at any time where the video stands and what comes next.

## Writing the effects in your script

This is the part that makes the motion feel written by you. In your script, next to the sentence, write in plain words what you want to see on screen when you say it:

```
Three habits so your notes are actually useful.   [highlight "useful"]
First: put a date on every note.                  [circle on "date"]
Second: one single place.                         [three words merge into one]
Third: reread on Sunday, ten minutes.             [check mark, "10 min" drops in]
```

`/sm-motion` transcribes your edited video word by word, finds the exact moment you say each word, and builds one zone per idea with the effect you asked for, landing on that word. It shows you the plan of zones (times, words, effect) before building. No bracket syntax is required: any clear note works. A full example is in `example/motion/BRIEF-motion.md`.

## The commands, in order

`/sm-video <STEM>` runs the whole chain. It reads where the video stands (`outils/video statut`), calls the skill of the next step in the same session, stops at every validation, and picks up where the video is at the next call. Each step also works on its own:

| # | Step | Command | Your gesture |
|---|---|---|---|
| 1 | research | `/sm-recherche <topic>`: plain Claude web research (3 to 5 sources, one counterpoint, URLs cited), notes and a teleprompter page | read the notes, film |
| 2 | cuts | `/sm-montage <take>` then `derush export <STEM>`: cuts silences, fillers, false starts; a DaVinci timeline (optional) lets you fix any cut | validate the cuts |
| 3 | colour (look) | `/sm-etalonnage <STEM>`: contact sheet of up to 4 looks, then `outils/look.py fixe <letter>`, once. Without DaVinci Resolve only A (neutral) is offered | pick A, B, C or D |
| 4 | motion, optional | `/sm-motion <STEM>`: HyperFrames motion timed on your words; one `motion-reviewer` pass before render | validate the motion |
| 5 | subtitles | `/sm-soustitres <STEM>`: hook, then one idea per sentence (`outils/overlays.py`) | validate the video |
| 6 | caption | `/sm-caption <STEM>`: written, then reread against the transcript and `STYLE.md` | read the text |
| 7 | export | `/sm-export <STEM>` (`outils/video export`): `videos/<STEM>/final/` (video, caption, thumbnail), contents checked | publish |

`diag`, `repare` and `medias` still exist in `ETAT.json` (old files keep reading) but have no tool: `outils/video statut` shows them as "optionnelle, pas d'outil" and they never block the next step.

Details per step: `videos/README.md` (folders, `ETAT.json`, output spec, platform limits) and each `SKILL.md`.

## Sounds

No sound bank is shipped (licences). `sm-motion` works without one: when `$SFX_DIR` is unset or empty, `sfx_mix.py` skips the sounds and writes a silent track, so the render is just quieter. To add sounds, point `SFX_DIR` at a folder of your own files (`.mp3 .wav .ogg .flac`) named as in `sfx-cues.py` (`pop`, `whoosh`, `impact-bass-1`, ...), or rename the cues in the `#beats` JSON to match yours. Use few sounds, only on strong beats of your voice.

## Fonts

Subtitles and motion use Inter Display, Caveat and JetBrains Mono, all SIL OFL 1.1 (see `outils/fonts/LICENSE.md`). Swap them freely, keep to free-licence fonts if you publish.

## Where it runs

| Environment | Works? |
|---|---|
| Claude Code CLI | Yes (local): ffmpeg, whisper and the render all run on your machine |
| Claude Desktop, "Code" tab | Yes (local), same as the CLI |
| Claude Code on the web | Possible, but you must get the raw video into the cloud sandbox and install ffmpeg, whisper (CPU, slow) and Node there; the look step needs Resolve LUTs, so use `"look": null` |
| claude.ai chat | No: no terminal, no render |

Status of what is verified: the scripts were extracted from a working private setup and checked here for syntax (`bash -n`, `py_compile`) and for `installer.sh --verifier`. An independent end-to-end run from a fresh clone then passed on a synthetic 20 s take (macOS `say` voice): derush, HyperFrames render, `verify_render.sh`, subtitles and export. Not yet tested on Linux.

## En français

Tu parles à la caméra et tu donnes la prise brute à Claude Code. Claude dérushe (silences, euh, faux départs), te laisse valider les coupes, choisit un look, génère un motion HyperFrames calé mot à mot sur ta voix à partir des effets écrits dans ton script, incruste des sous-titres dynamiques, écrit la caption et exporte en 1080x1920. Rien ne se publie tout seul.

Il te faut Claude Code (terminal ou onglet Code de l'app Desktop), ffmpeg, Node 22+, whisper et les skills HyperFrames (`npx skills add heygen-com/hyperframes --all`). Installation : `outils/installer.sh --verifier`, puis `outils/installer.sh`. Premier essai : `/sm-montage ~/Downloads/ma_prise.mov`, puis `/sm-video ma_prise`. Les effets s'écrivent en clair dans ton script, à côté de la phrase (« [cercle sur "date"] ») : `/sm-motion` les cale sur le mot. Point d'entrée : `/sm-video <STEM>`, qui enchaîne toute la chaîne et s'arrête à chaque validation ; chaque étape a aussi sa commande (`/sm-etalonnage`, `/sm-soustitres`, `/sm-caption`, `/sm-export`). DaVinci Resolve est optionnel : il apporte les looks film de l'étalonnage et la retouche manuelle des coupes ; les coupes sont faites par ffmpeg. Remplis `STYLE.md` une fois (ton, interdits) : c'est la seule vérification de voix, Claude y relit chaque caption. Aucune banque de sons n'est livrée : sans `SFX_DIR`, le motion sort sans bruitages.

## Licence

MIT, voir `LICENSE`.
