---
name: sm-video
description: "La commande générale de la chaîne vidéo : lit où en est la vidéo (outils/video statut), enchaîne les étapes dans la même session (recherche, montage, étalonnage, motion si voulu, sous-titres, caption, export) en appelant la skill de chacune, s'arrête à chaque validation, reprend là où la vidéo en est au prochain appel. Triggers: /sm-video, la suite de ma vidéo, finis ma vidéo, enchaîne les étapes, mets les sous-titres, fais la caption, exporte ma vidéo."
---

# /sm-video <STEM>

La chaîne entière, depuis la racine du dépôt. Chaque étape a sa skill ; `/sm-video` les enchaîne
dans la MÊME session et s'arrête à chaque validation. Au prochain appel, il reprend là où la vidéo
en est : l'état vit dans `videos/<STEM>/` et `ETAT.json`, pas dans la session.

## Boucle

1. `outils/video statut <STEM>` (sans STEM : `outils/video statut`, la plus récente en tête).
   Lire « fait », « reste », « attend ton geste » et « suite ».
2. Une étape à valider est en attente (tu n'a pas dit OK) : la lui montrer de nouveau et
   attendre. Ne jamais passer à la suivante sans OK.
3. Sinon, lancer la skill de la PROCHAINE étape (table), montrer le résultat, puis S'ARRÊTER :
   tu valides.
4. Ton OK : `outils/video valide <STEM> <étape>`. Relancer le statut et repartir en 2. Dès que la
   suite demande un geste à toi (filmer, choisir une lettre, publier), le dire et s'arrêter.
5. Terminé quand `statut` dit « à publier ». Publier est ton geste.

## Les étapes, dans l'ordre

| Étape | Skill ou commande | Tu valides |
|---|---|---|
| recherche | `/sm-recherche <sujet>` | les notes, puis tu filmes |
| montage | `/sm-montage <prise>`, puis `derush export <STEM>` (`--from <fichier>` après une retouche DaVinci) | les coupes (rien à valider pour l'export : 1080x1920, 30 i/s, -14 LUFS) |
| étalonnage (clé `look`) | `/sm-etalonnage <STEM>` | la lettre du look |
| motion, OPTIONNEL : le proposer, ne pas l'imposer | `/sm-motion <STEM>` | le motion |
| sous-titres (clé `overlays`) | `/sm-soustitres <STEM>` | la vidéo et `overlays/check.jpg` |
| caption | `/sm-caption <STEM>` | le texte |
| export | `/sm-export <STEM>` | rien : publier = ton geste |

`diag`, `repare` et `medias` existent dans `ETAT.json` mais n'ont aucun outil : étapes OPTIONNELLES,
`statut` les affiche « optionnelle, pas d'outil » et elles ne bloquent jamais la suite. Les ignorer.

Un ancien `ETAT.json` peut marquer l'étalonnage « sautée » (c'était l'état de l'époque). Si
`outils/looks/LOOK.json` n'existe pas, lancer `/sm-etalonnage` quand même, avant les sous-titres.

DaVinci Resolve est OPTIONNEL (gratuit suffit) : il apporte les LUT film de l'étalonnage et la
retouche manuelle des coupes via le `.fcpxml`. Les coupes elles-mêmes sont faites par ffmpeg. Sans
lui, l'étalonnage ne propose que A (neutre).

## Règles

- Rien ne publie tout seul. Rien n'est envoyé à personne.
- Respecter `STYLE.md` (ton, interdits) pour tout texte écrit : sous-titres, caption.
- Ouvrir ce que tu dois voir : `open -a "QuickTime Player" <vidéo>` (macOS ; `xdg-open` sous
  Linux), ou ouvrir `<planche>.jpg`.
- Un outil qui casse : le dire avec l'erreur exacte, ne pas bricoler à la main à sa place.
- Une étape ne se refait que si tu le demandes ou si `statut` la dit périmée (un re-montage périme
  les étapes d'après).
- Contexte lourd : une longue chaîne dans une session grossit vite. Si la session ralentit, finir
  l'étape en cours, écrire où l'on en est, et reprendre dans une session neuve avec `/sm-video <STEM>`.
