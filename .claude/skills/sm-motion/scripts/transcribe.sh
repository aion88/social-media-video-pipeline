#!/bin/bash
# Transcript mot à mot de la vidéo MONTÉE (celle sur laquelle le motion se cale).
# whisper large-v3-turbo, puis align_words.py (CTC) : whisper seul dérive de 0,1 à 0,4 s par mot.
# Usage : transcribe.sh <video> <dossier_work> [durée_utile_s] [langue, défaut fr]
# Sortie : <dossier_work>/aligned.json et words.txt (une ligne par mot : début fin mot).
set -euo pipefail
V="$1"; W="$2"; T="${3:-}"; L="${4:-fr}"
mkdir -p "$W"
ffmpeg -nostdin -v error -y -i "$V" ${T:+-t "$T"} -vn -ac 1 -ar 16000 "$W/audio.wav"
WHISPER="${WHISPER:-$(command -v whisper || true)}"
[[ -n "$WHISPER" && -x "$WHISPER" ]] || { echo "whisper introuvable : uv tool install openai-whisper, ou export WHISPER=/chemin/whisper" >&2; exit 1; }
"$WHISPER" "$W/audio.wav" --model large-v3-turbo --device cpu --language "$L" \
  --output_format json --output_dir "$W" --word_timestamps True --condition_on_previous_text False \
  --initial_prompt "Euh, alors, hum, je... je voulais, euh, mmh, en fait, bah, voilà." >/dev/null 2>"$W/whisper.err"
_self="${BASH_SOURCE[0]}"
while [[ -L "$_self" ]]; do _t="$(readlink "$_self")"; [[ "$_t" = /* ]] && _self="$_t" || _self="$(dirname "$_self")/$_t"; done
python3 "$(cd "$(dirname "$_self")" && pwd)/../../derush/scripts/align_words.py" "$W/audio.wav" "$W/audio.json" --out "$W/aligned.json"
python3 - "$W/aligned.json" "$W/words.txt" <<'E'
import json, sys
d = json.load(open(sys.argv[1]))
with open(sys.argv[2], "w") as f:
    for s in d["segments"]:
        for w in s.get("words", []):
            f.write(f'{w["start"]:7.2f} {w["end"]:7.2f} {w["word"].strip()}\n')
E
echo "OK $W/aligned.json $W/words.txt"
