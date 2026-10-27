#!/bin/bash
# Contrôle d'un rendu motion, mesuré, pas regardé « à l'œil ».
# Usage : verify_render.sh <rendu.mp4> <voix.mp4 (la vidéo montée)> <sfx.wav> <dossier_sortie>
# Imprime : flux (attendu 1080x1920, 30 fps, 1 piste audio), loudness intégrée (attendu ~-14/-15 LUFS),
# corrélation résidu/sfx (rendu moins la voix ; attendu > 0,8 avec une banque SFX_DIR ;
# sans banque, seuls les souffles "noise" sont mixés et ~0,3 est normal).
# Écrit : sheet.jpg (une image toutes les 5 s) et last.jpg (dernière image). LES REGARDER.
set -euo pipefail
R="$1"; V="$2"; S="$3"; O="$4"
mkdir -p "$O"
ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,duration -of compact "$R"
ffmpeg -hide_banner -nostdin -i "$R" -af ebur128 -f null - 2>&1 | grep -A1 "Integrated" | tail -1
ffmpeg -v error -nostdin -y -i "$R" -vf "fps=1/5,scale=180:320,tile=8x2" -frames:v 1 "$O/sheet.jpg"
ffmpeg -v error -nostdin -y -sseof -0.1 -i "$R" -frames:v 1 -vf scale=270:480 "$O/last.jpg"
ffmpeg -v error -nostdin -y -i "$R" -i "$V" -filter_complex \
  "[0:a]aresample=16000,pan=mono|c0=c0[a];[1:a]aresample=16000,pan=mono|c0=c0,volume=-1[b];[a][b]amix=inputs=2:normalize=0[o]" \
  -map "[o]" -f f32le "$O/res.raw"
ffmpeg -v error -nostdin -y -i "$S" -af "aresample=16000,pan=mono|c0=c0" -f f32le "$O/sfx.raw"
python3 - "$O" <<'E'
import sys, numpy as np
o = sys.argv[1]
r = np.fromfile(f"{o}/res.raw", np.float32); s = np.fromfile(f"{o}/sfx.raw", np.float32)
n = min(len(r), len(s)); w = 1600
e = lambda x: np.sqrt((x[: n // w * w].reshape(-1, w) ** 2).mean(1))
if s.std() < 1e-6:
    print("pas de bruitages (piste sfx silencieuse) : correlation sans objet")
else:
    print("corr residu/sfx (fenetres 100 ms):", round(float(np.corrcoef(e(r), e(s))[0, 1]), 3))
E
rm -f "$O/res.raw" "$O/sfx.raw"
echo "planches : $O/sheet.jpg $O/last.jpg"
