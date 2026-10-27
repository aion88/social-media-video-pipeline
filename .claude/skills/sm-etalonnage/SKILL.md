---
name: sm-etalonnage
description: "Étalonnage de la vidéo montée : une planche de 4 looks (A neutre, B Kodak 2383, C Fuji 3513, D 2383 léger), tu choisis une lettre, le look est fixé une fois pour toutes. Sans DaVinci Resolve (gratuit), seul A neutre est proposé. Triggers: /sm-etalonnage, étalonne ma vidéo, étalonnage, choisis un look, planche de looks, color grading."
---

# /sm-etalonnage <STEM>

Étape « étalonnage » de la chaîne (clé `look` dans `ETAT.json`). Elle encapsule `outils/look.py`,
sans le réécrire. Le look se fixe UNE fois ; les vidéos suivantes le reprennent.

## Avant

1. `outils/video statut <STEM>`. Le montage doit être exporté : `videos/<STEM>/<STEM>.reel.mp4`
   existe. Sinon : `derush export <STEM>` d'abord.
2. Look déjà fixé ? `outils/looks/LOOK.json` existe : l'étape est FAITE, on l'applique sans te redemander.
   Dire seulement la lettre en une ligne et passer à la suite. La planche ne se refait que si on demande
   explicitement un autre look.

## Faire

1. `outils/look.py planche videos/<STEM>/<STEM>.reel.mp4` : écrit `videos/<STEM>/look/planche.jpg`
   (deux images de la prise, une colonne par look). Les lettres dont le LUT manque sont sautées, et
   la commande le dit sur la sortie d'erreur.
2. Ouvrir la planche : `open videos/<STEM>/look/planche.jpg`.
3. Dire ce qu'il y a dessus, en une phrase :
   - **avec DaVinci Resolve installé** : A neutre, B Kodak 2383, C Fuji 3513, D 2383 léger. Les
     looks B à D lisent les LUT « Film Looks » livrés avec Resolve (gratuit suffit). Autre
     emplacement : `export RESOLVE_FILM_LOOKS=<dossier Film Looks>`.
   - **sans Resolve** : seule A (neutre) est proposée. Aucun look film possible, la vidéo reste
     telle qu'elle est montée. Ne pas inventer de B à D. Installer Resolve (gratuit) ouvre les trois autres.
4. Tu choisis la lettre. Puis `outils/look.py fixe <lettre>` (`--force 0.6` pour atténuer le look,
   de 0 à 1). Écrit `outils/looks/look.cube` et `outils/looks/LOOK.json`. Une lettre dont le LUT manque est
   refusée avec la raison, pas d'erreur Python.
   Si DaVinci Resolve est installé, `fixe` copie aussi `look.cube` dans le dossier LUT de Resolve
   (`LUT/Perso/look.cube`), pour l'avoir dans Resolve. Le dire à la personne.
4b. Pour un essai sans rien fixer : `outils/look.py cube <lettre> videos/<STEM>/look/essai-<lettre>.cube`.

## S'arrêter

Tu valides la lettre. Rien d'autre à écrire : `outils/video statut <STEM>` lit `outils/looks/LOOK.json`
et marque l'étalonnage fait. Suite : `/sm-motion <STEM>` si tu le veux, sinon `/sm-soustitres <STEM>`.

`"look": null` dans `overlays.json` = aucun look, seulement si tu le dis.
