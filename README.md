# claude-video-pipeline

You talk to the camera and hand the raw take to Claude Code. Claude derushes it (cuts silences, fillers, false starts), lets you validate the cuts, picks a colour look, generates motion graphics with [HyperFrames](https://github.com/heygen-com/hyperframes) (HTML rendered to video) timed word by word on your voice from the effects you wrote in your script, burns dynamic subtitles, writes the caption and exports a vertical 1080x1920 video. Nothing is ever published for you.

Skills and notes are written in French (the pipeline was built for French speech; `--lang en` works for English takes). Un résumé en français est à la fin.

## What is in here

```
.claude/skills/   sm-video (the door), sm-recherche, sm-montage, derush, sm-motion
.claude/agents/   motion-reviewer (one Sonnet review before render)
outils/           video (status/validate/export), look.py, overlays.py, plafond.py, deband.py, installer.sh, fonts/
videos/           one folder per video (media is gitignored), README.md = the spec
example/          neutral text-only example (cuts report, motion brief, overlays, caption)
STYLE.md          your tone and bans, filled in once; Claude rereads captions against it
```

## Prerequisites

- [Claude Code](https://claude.com/claude-code) (CLI, or the Desktop app "Code" tab)
- `ffmpeg` + `ffprobe`, `python3` (3.10+), `uv`, `node` 22+ (for `npx hyperframes`)
- [OpenAI Whisper](https://github.com/openai/whisper) on the PATH (`uv tool install openai-whisper`, or `export WHISPER=/path/to/whisper`); `torch` + `torchaudio` for the word alignment
- Python modules: numpy, opencv-python, pillow, soundfile, fonttools (the installer adds them with `uv`)
- Optional: DaVinci Resolve (free is enough) for the film-look LUTs read by `outils/look.py` and for hand-editing the cuts via the `.fcpxml` timeline
- Optional: your own sound folder `SFX_DIR` (see Sounds)

## Install

```bash
git clone <this repo> && cd claude-video-pipeline
outils/installer.sh --verifier   # prints OK / MANQUE lines, touches nothing
outils/installer.sh              # installs the light python modules via uv
outils/installer.sh --lier       # optional: link the skills into ~/.claude/skills and derush into ~/.local/bin
```

Open the folder in Claude Code: the skills are loaded from `.claude/skills/`. Then fill in `STYLE.md`.

## The commands, in order

`/sm-video <STEM>` is the entry point: it reads where the video stands (`outils/video statut`), runs the next step and stops when it is your turn to validate. One step per session.

| # | Command | Your gesture |
|---|---|---|
| 1 | `/sm-recherche <topic>` : plain Claude web research (3 to 5 sources, one counterpoint, URLs cited), notes and a teleprompter page | read the notes, film |
| 2 | `/sm-montage <take>` then `derush export <STEM>` : cuts silences, fillers, false starts; a DaVinci timeline lets you fix any cut | validate the cuts |
| 3 | `outils/look.py planche <reel.mp4>` then `outils/look.py fixe <letter>` : colour look, once | pick A, B, C or D |
| 4 | `/sm-motion <STEM>` : HyperFrames motion timed on your words; one `motion-reviewer` pass before render | validate the motion |
| 5 | `/sm-video <STEM>` : dynamic subtitles (`outils/overlays.py`), then the caption, reread against `STYLE.md` | validate the video and the text |
| 6 | `outils/video export <STEM> <name>` : `videos/<STEM>/final/` (video, caption, thumbnail) | publish |

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

Status of what is verified: the scripts were extracted from a working private setup and checked here for syntax (`bash -n`, `py_compile`) and for `installer.sh --verifier`. The derush on a real take and the HyperFrames render were not re-run after the extraction.

## En français

Tu parles à la caméra et tu donnes la prise brute à Claude Code. Claude dérushe (silences, euh, faux départs), te laisse valider les coupes, choisit un look, génère un motion HyperFrames calé mot à mot sur ta voix à partir des effets écrits dans ton script, incruste des sous-titres dynamiques, écrit la caption et exporte en 1080x1920. Rien ne se publie tout seul.

Installation : `outils/installer.sh --verifier`, puis `outils/installer.sh`. Point d'entrée : `/sm-video <STEM>`. Remplis `STYLE.md` une fois (ton, interdits) : c'est la seule vérification de voix, Claude y relit chaque caption. Aucune banque de sons n'est livrée : sans `SFX_DIR`, le motion sort sans bruitages.

## Licence

MIT, voir `LICENSE`.
