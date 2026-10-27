---
name: sm-export
description: "Exporte la vidéo finie dans videos/<STEM>/final/ (la vidéo, caption.txt, thumbnail.png) et contrôle ce que contient le dossier. Refuse sans caption ou hors -14 LUFS. Rien n'est publié. Triggers: /sm-export, exporte ma vidéo, prépare le paquet à publier, c'est prêt à poster."
---

# /sm-export <STEM>

Dernière étape de la chaîne (clé `export` dans `ETAT.json`). Elle encapsule `outils/video export`.
Publier reste ton geste : rien ne part tout seul, rien n'est envoyé à personne.

## Avant

`outils/video statut <STEM>` : sous-titres validés (ou motion), `caption.txt` validée. Sinon, ne pas
exporter : renvoyer vers `/sm-soustitres` ou `/sm-caption`.

## Faire

1. Un nom court pour le fichier, sans dossier ni espace (`sante-mentale-neurones`).
2. `outils/video export <STEM> <nom-court>`. Il prend la plus finie des vidéos (`.overlays.mp4`, sinon
   `.motion.mp4`, sinon `.reel.mp4`), refuse sans `caption.txt` ou hors -14 LUFS (à 1 LU près), copie
   dans `videos/<STEM>/final/` et écrit `ETAT.json`. Un nom déjà pris qui diffère : un autre nom, ou
   `--force`. Un ancien `.mp4` de `final/` part à la Corbeille.
   L'export REFUSE aussi (gardes du 2026-10-27) : un `.overlays.mp4` qui n'est pas construit sur
   le `.motion.mp4` (il sortirait sans motion), une vignette absente ou plus ancienne que la vidéo,
   un look fixé après la vidéo (`--look-ok` si le look est déjà dans l'image).
3. Contrôler `final/` :
   ```bash
   ls -l videos/<STEM>/final/
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,duration -of csv=p=0 videos/<STEM>/final/<nom-court>.mp4
   cmp videos/<STEM>/caption.txt videos/<STEM>/final/caption.txt
   ```
   Attendu :
   - exactement trois fichiers : `<nom-court>.mp4`, `caption.txt`, `thumbnail.png` ;
   - `1080,1920,30/1,<durée>` ;
   - `cmp` ne dit rien (même caption)
   - la caption relue contre `STYLE.md` (il n'y a pas de contrôle automatique).

   Vignette refusée : `<STEM>.thumbnail.png` vient du rendu des sous-titres (`outils/overlays.py <STEM>`)
   ou, pour un motion, de l'image du titre d'ouverture (`/sm-motion`). La refaire, puis relancer l'export.
4. Ouvrir ce qui part : `open -a "QuickTime Player" videos/<STEM>/final/<nom-court>.mp4`.

## S'arrêter

Dire où est le paquet et le résultat du contrôle, y compris ce qui manque. Tu publies.
