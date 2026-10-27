#!/usr/bin/env python3
"""cues.json -> une seule piste de bruitages (wav 48 kHz stéréo), calée à la milliseconde.

cues.json = {"total": 64, "cues": [{"t": 1.2, "sfx": "click-soft", "vol": 0.1}, ...]}
  sfx = le nom (sans extension) d'un fichier de TA banque de sons, le dossier $SFX_DIR
        (.mp3 .wav .ogg .flac), ou "noise" : une bouffée de bruit rose filtré, 0,4 s, pour les
        changements de scène. Aucune banque n'est livrée avec ce dépôt (licences).
  vol = gain linéaire. Repère : 0,35 = sous une voix, 0,1 = tic de lettre.
  master (optionnel) = gain de toute la piste, pour la caler sous la voix normalisée (-14 LUFS) :
  viser une piste ~12 dB sous la voix, la mesurer (ebur128) au lieu de deviner.

Une seule piste plutôt que N balises <audio> : un fichier à écouter seul, un seul élément dans
la composition, et la voix reste sur la vidéo.

Sans $SFX_DIR (non défini, vide ou inexistant) : AUCUN son de la banque n'est cherché, seul
"noise" est mixé, et si le résultat est vide la piste est un silence de la durée voulue. La
composition reste valide (elle référence toujours assets/sfx.wav), le motion sort sans
bruitages. Un nom absent de la banque est signalé sur stderr et sauté, jamais fatal.

Usage : sfx_mix.py <cues.json> <sortie.wav>
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Banque : $SFX_DIR, un dossier à toi. Absent ou vide : pas de bruitages (voir l'en-tête).
_d = os.environ.get("SFX_DIR", "").strip()
BANK = Path(_d).expanduser() if _d else None
EXTS = (".mp3", ".wav", ".ogg", ".flac")


def find_sound(name):
    if BANK is None or not BANK.is_dir():
        return None
    for ext in EXTS:
        p = BANK / f"{name}{ext}"
        if p.exists():
            return p
    return None


def silence(total, out):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", str(total),
         "-i", "anullsrc=r=48000:cl=stereo", "-c:a", "pcm_s16le", out],
        check=True,
    )


def noise_file(tmp):
    p = Path(tmp) / "noise.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anoisesrc=d=0.4:c=pink:a=0.6:r=48000",
            "-af",
            "highpass=f=700,lowpass=f=9000,afade=t=in:d=0.12,afade=t=out:st=0.14:d=0.26",
            "-ac",
            "2",
            str(p),
        ],
        check=True,
    )
    return p


def main():
    cfg = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    total, cues = float(cfg["total"]), cfg["cues"]
    with tempfile.TemporaryDirectory() as tmp:
        noise = noise_file(tmp)
        args = [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-t",
            str(total),
            "-i",
            "anullsrc=r=48000:cl=stereo",
        ]
        chains, n, sautes = [], 0, set()
        for c in cues:
            src = noise if c["sfx"] == "noise" else find_sound(c["sfx"])
            if src is None:
                sautes.add(c["sfx"])
                continue
            if not 0 <= c["t"] < total:
                sys.exit(f"cue hors durée : {c}")
            n += 1
            args += ["-i", str(src)]
            ms = int(round(c["t"] * 1000))
            chains.append(
                f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,"
                f"volume={c.get('vol', 0.35)},adelay={ms}|{ms}[c{n}]"
            )
        if sautes:
            raison = "SFX_DIR non défini" if BANK is None else f"absents de {BANK}"
            print(f"sons sautés ({raison}) : {', '.join(sorted(sautes))}", file=sys.stderr)
        if n == 0:
            silence(total, out)
            print(f"aucun son -> piste silencieuse {out} ({total} s)")
            return
        mix = "".join(f"[c{i}]" for i in range(1, n + 1))
        graph = ";".join(chains) + (
            f";[0:a]{mix}amix=inputs={n + 1}:normalize=0:duration=first,"
        f"volume={cfg.get('master', 1.0)},"
            "alimiter=limit=0.89[out]"
        )
        subprocess.run(
            args
            + [
                "-filter_complex",
                graph,
                "-map",
                "[out]",
                "-t",
                str(total),
                "-c:a",
                "pcm_s16le",
                out,
            ],
            check=True,
        )
    print(f"{n} sons -> {out} ({total} s)")


if __name__ == "__main__":
    main()
