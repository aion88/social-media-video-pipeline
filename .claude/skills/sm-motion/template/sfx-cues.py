"""Bruitages, un par contact. Ne lit QUE le bloc #beats de index.html : mêmes temps que l'image.
Lancer depuis motion/ : python3 sfx-cues.py > sfx-cues.json, puis sfx_mix.py sfx-cues.json assets/sfx.wav
Clés lues dans #beats (toutes optionnelles sauf total, dot, cam) :
  dot    [arrivée, durée, x, y]       clic à chaque arrivée, souffle court sur les trajets >= 0,5 s
  cam    [t, durée, x, y, zoom, ease] bruit rose à chaque changement de zone (saut > 400 px)
  blocks [nom, t]                     un tic par lettre du nom qui tombe
  cmts   [t, texte]                   un grattement par note à la main
  drops  [t, nb_lettres, pas, vol?]   un tic par lettre de chaque `drop()` de l'animation
  typing [t, nb_lettres, durée]       une frappe toutes les 2 lettres
  sfx    [t, son, vol]                les gestes à la main (traits, impacts, coche)
  end    t                            la fin (le mot de clôture) : souffle, impact, scintillement
"""

import json, re

html = open("index.html").read()
B = json.loads(
    re.search(
        r'<script type="application/json" id="beats">(.*?)</script>', html, re.S
    ).group(1)
)
C = []


def add(t, sfx, vol):
    C.append({"t": round(t, 3), "sfx": sfx, "vol": vol})


def ticks(at, n, st, vol=0.07):
    for k in range(n):
        add(at + k * st + 0.12, "click-soft", vol)


for arrive, d, x, y in B["dot"]:
    add(arrive, "click-soft", 0.16)
    if d >= 0.5:
        add(arrive - d, "whoosh-short", 0.10)
prev = (B["cam"][0][2], B["cam"][0][3])
for at, d, x, y, z, ease in B["cam"]:
    if ease != "none" and abs(x - prev[0]) + abs(y - prev[1]) > 400:
        add(at, "noise", 0.18)
    prev = (x, y)
for name, at in B.get("blocks", []):
    ticks(at, len(name.replace(" ", "")), 0.025)
for at, text in B.get("cmts", []):
    if text:
        add(at, "typing", 0.05)
for d in B.get("drops", []):
    ticks(*d)
for at, n, dur in B.get("typing", []):
    for k in range(0, n, 2):
        add(at + dur * k / max(n, 1), "key-press", 0.05)
for at, sfx, vol in B.get("sfx", []):
    add(at, sfx, vol)
if "end" in B:
    e = B["end"]
    add(e, "whoosh", 0.18)
    add(e + 0.29, "impact-bass-2", 0.28)
    add(e + 0.35, "sparkle", 0.10)

T = B["total"]
C = [c for c in C if 0 <= c["t"] < T]
print(
    json.dumps(
        {
            "total": T,
            "master": 0.55,
            "cues": sorted(C, key=lambda c: (c["t"], c["sfx"])),
        },
        ensure_ascii=False,
        indent=0,
    )
)
