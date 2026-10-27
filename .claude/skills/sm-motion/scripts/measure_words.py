#!/usr/bin/env python3
"""Largeur réelle d'un texte dans une police du projet, en px. Sert à caler un surligneur,
un soulignement ou un cercle sur un mot (map WN de la v3) au lieu de deviner.

Usage : measure_words.py <police.woff2> <taille_px> <letter_spacing_em> "mot 1" "mot 2" ...
  ex. measure_words.py assets/fonts/InterDisplay-Medium.woff2 56 -0.03 Communication Format
Le letter-spacing est celui du CSS, en em (ex. -0.03). Avance seule, sans crénage.
"""

import sys
from fontTools.ttLib import TTFont

font, size, ls = TTFont(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
cmap, hm, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
for t in sys.argv[4:]:
    w = sum(
        hm[cmap.get(ord(c), cmap[32])][0] for c in t
    ) * size / upm + ls * size * len(t)
    print(f"{t}\t{round(w, 1)}")
