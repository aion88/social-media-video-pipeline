# Social Media Video Pipeline

Read `README.md` first. The skills live in `.claude/skills/`; `/sm-video <STEM>` runs the whole chain.

## When the user asks you to install this pipeline

1. If the repo is not on disk yet: `git clone https://github.com/aion88/social-media-video-pipeline.git` and `cd` into it.
2. `outils/installer.sh --verifier`. It prints one line per requirement: `OK`, or `MANQUE` followed by the command that fixes it.
3. For each `MANQUE`, run the command it prints. Say before running anything heavy: `torch` + `torchaudio` (~330 MB) and the Whisper model (1.5 GB, downloaded at the first cut). Use Homebrew on macOS for `ffmpeg` and `node` only if the user agrees.
4. HyperFrames skills: `npx skills add heygen-com/hyperframes --all`.
5. `outils/installer.sh` (light python modules), then `outils/installer.sh --lier` so the `/sm-...` commands work from any folder.
6. `outils/installer.sh --verifier` again: everything must be `OK` except the optional lines (DaVinci Resolve LUTs, `SFX_DIR`).
7. Tell the user what was installed, what is optional and still missing, and how to start: film a vertical take, then `/sm-montage <path to the take>`.

Never publish anything: publishing is the user's gesture.
