---
name: sm-soustitres
description: "Sous-titres dynamiques de la vidéo : l'accroche au début, puis une idée par phrase avec les mots clés surlignés, calée sur la voix (ta voix, mot à mot). Écrit overlays.json, fait l'essai, rend la vidéo. Triggers: /sm-soustitres, sous-titres, mets les sous-titres, overlays texte, habille ma vidéo avec du texte."
---

# /sm-soustitres <STEM>

Étape « sous-titres » de la chaîne (clé `overlays` dans `ETAT.json`). Prérequis : le montage est
exporté (`<STEM>.reel.mp4`) et le look est fixé (`/sm-etalonnage`, sinon le rendu refuse).

Réglages par défaut de `outils/overlays.py` (à ajuster dans `overlays.json`) :

- l'accroche au début seulement, environ 5 s, jamais un titre qui reste ;
- pas chaque mot : une idée par phrase utile, avec TES mots, les mots clés surlignés ;
- surlignage discret (couleur `SURLIGNE` dans `overlays.py`), texte encre ;
- entrée en fondu avec 10 px de montée, sortie en fondu sur place : pas de parallaxe, pas de
  sortie par le haut, une seule idée à l'écran ;
- sous le menton (centre y 1300), jamais collé au visage ;
- Inter Display Medium et Light (OFL, `outils/fonts/`) ; ta propre police via `polices`.

## Faire

1. `outils/overlays.py texte <STEM>` : les phrases datées. La première fois, il transcrit la
   vidéo (environ 1 min). La vidéo par défaut est `<STEM>.reel.mp4`.
2. Écrire `videos/<STEM>/overlays/overlays.json`, en copiant la forme de `example/overlays.json`
   (le format est aussi dans `outils/overlays.py` lancé sans argument).
   - `accroche` : 2 ou 3 lignes (light 86, medium 140, light italique 46), `fin` environ 5 s.
     La 3e ligne en italique est une petite note : son `*` de tête s'affiche tel quel, l'enlever
     si tu n'en veux pas.
   - `idees` : `["texte affiché", "phrase dite"]`. Le texte affiché fait 2 à 6 mots pris dans ce
     que tu dis, avec 1 à 3 `**mots clés**`. ` / ` coupe la ligne en deux. `"3|mes photos"`
     marque un chapitre. La phrase dite reprend les mots exacts du transcript : c'est elle qui cale
     l'entrée.
   - Sauter le remplissage (« euh », « ça c'est important »). Une idée de moins de 0,6 s se
     fusionne avec sa voisine. Un nom mal transcrit se corrige dans le texte affiché, puis on te
     le signale.
   - Le look : sans clé `look`, c'est `outils/looks/look.cube` s'il est fixé. S'il ne l'est pas,
     le rendu refuse : lancer `/sm-etalonnage <STEM>`. En attendant ton choix, un essai :
     `outils/look.py cube D videos/<STEM>/overlays/essai-D.cube` et
     `"look": "overlays/essai-D.cube"`. `"look": null` = aucun look, seulement si tu le dis.
     (`look.py` lit les LUT « Film Looks » de DaVinci Resolve, gratuit suffit ; sans Resolve,
     `"look": null`.)
3. `outils/overlays.py essai <STEM>` : aucune phrase introuvable, aucun TROP LARGE. COURT
   seulement si c'est voulu.
4. `outils/overlays.py <STEM>` : rendu en 1 min environ. Regarder `overlays/check.jpg`, puis
   ouvrir `videos/<STEM>/<STEM>.overlays.mp4`.
5. Tu valides, puis `outils/video valide <STEM> overlays`. Retouche : changer `overlays.json`,
   puis refaire 3 et 4.

S'arrêter ici : ouvrir la vidéo et `overlays/check.jpg`, attendre la validation. Suite : `/sm-caption <STEM>`.
