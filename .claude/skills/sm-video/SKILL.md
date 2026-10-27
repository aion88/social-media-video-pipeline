---
name: sm-video
description: "La porte unique de la chaîne vidéo. Lit où en est une vidéo (outils/video statut), lance l'étape suivante (recherche, montage, look, sous-titres dynamiques, caption, export), s'arrête à chaque validation. Triggers: /sm-video, la suite de ma vidéo, finis ma vidéo, mets les sous-titres, mets les overlays texte, fais la caption, exporte ma vidéo."
---

# /sm-video <STEM>

Une étape par session, toujours depuis la racine du dépôt.

1. `outils/video statut <STEM>` (sans STEM : `outils/video statut`, la plus récente en tête).
   Lire « attend ton geste » et « suite ».
2. Faire l'étape suivante (table), montrer le résultat, puis S'ARRÊTER : tu valides.
3. Ton OK : `outils/video valide <STEM> <étape>`. Finir par « suite : /sm-video <STEM> dans une
   session neuve ».

| Étape | Ce qui la fait | Tu valides |
|---|---|---|
| recherche | `/sm-recherche <sujet>` | les notes, puis tu filmes |
| montage | `/sm-montage <prise>` | les coupes (ou ta retouche DaVinci) |
| export du montage | `derush export <STEM>` ; retouché dans DaVinci : `derush export <STEM> --from <fichier>` | rien : 1080x1920, 30 i/s, -14 LUFS |
| look, une fois pour toutes | `outils/look.py planche videos/<STEM>/<STEM>.reel.mp4`, tu choisis, `outils/look.py fixe <lettre>` | la lettre |
| motion, si tu le veux | `/sm-motion <STEM>` | le motion |
| sous-titres | lire `etapes/overlays.md` | la vidéo et `overlays/check.jpg` |
| caption | lire `etapes/caption.md` | le texte |
| export | `outils/video export <STEM> <nom-court>` | publier = ton geste |

## Règles

- Rien ne publie tout seul. Rien n'est envoyé à personne.
- Respecter `STYLE.md` (ton, interdits) pour tout texte écrit : sous-titres, caption.
- Ouvrir ce que tu dois voir : `open -a "QuickTime Player" <vidéo>` (macOS ; `xdg-open` sous
  Linux), ou ouvrir `<planche>.jpg`.
- Un outil qui casse : le dire avec l'erreur exacte, ne pas bricoler à la main à sa place.
- Pas d'outil pour : diagnostic et réparation de la prise, médias dont tu parles ; `statut` les
  marque sautées. Le look : c'est `outils/overlays.py` qui le pose, et il refuse de rendre sans
  look choisi.
