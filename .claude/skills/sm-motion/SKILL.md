---
name: sm-motion
description: "Étape 3 (optionnelle) de la chaîne vidéo : générer le motion graphics de la vidéo MONTÉE avec HyperFrames, en split vertical (motion en haut, toi en bas), calé mot à mot sur ta voix, à partir des effets que tu as écrits dans ton script. Revue unique par un sous-agent (goût + orthographe), rendu vérifié. Triggers: /sm-motion, fais le motion de ma vidéo, crée les overlays, habille ma vidéo."
---

# /sm-motion

Étape optionnelle de la chaîne (`/sm-recherche` → tu tournes → `/sm-montage` → `/sm-motion` si tu le
veux). Après le rendu : `/sm-video <STEM>` pour la caption et l'export. Le motion vient APRÈS le
montage validé : un re-montage après coup oblige à tout recaler.

**Point de départ : `template/`**, une composition complète (caméra qui se déplace dans un monde,
point guide, lettres qui tombent, écriture à la main). Son style est un `STYLE-EXAMPLE` : les
couleurs sont 5 variables CSS en tête de `index.html` (`--noir --beige --bleu --vert --vert-rgb`),
les polices 3 `@font-face` (toutes OFL). Change-les pour changer d'univers. On garde les
fondations, on réécrit les zones et les temps. `example/` montre un brief, une composition et un
`cuts.md` remplis.

## Avant de construire

- Charger `/hyperframes` puis `/hyperframes-core` et `/hyperframes-animation` (skills HyperFrames,
  `npx skills add heygen-com/hyperframes`). CLI épinglée : toute commande
  `npx --yes hyperframes@0.8.140 ...`.
- Entrée : `videos/<STEM>/<STEM>.reel.mp4` (sortie de `derush export`, -14 LUFS, 30 fps). Si tu as
  monté toi-même : ton export, passé par `derush export <STEM> --from <export>`.
  Notes et script : `videos/<STEM>/NOTES-REPRISE.md` (`/sm-montage` étape 0 les y a copiées).
  **Les effets que tu as écrits dans ton script (« ici un cercle sur le mot X », « le chiffre
  arrive », « la liste se construit ») sont la matière première des zones.**
- `STYLE.md` à la racine du dépôt (si tu l'as rempli) fixe ton ton et tes interdits.
- Si tu dis « va jusqu'au bout / ne me demande pas » : aucune pause, rapport à la fin seulement.
  Sinon un seul arrêt : étape 4.
- Variables : `R="<racine du dépôt>/videos/<STEM>"`, `K="<racine du dépôt>/.claude/skills/sm-motion"`
  (ou `~/.claude/skills/sm-motion` si les skills sont liées). Chaque commande dit d'où elle part.

## Étapes

1. **Projet d'abord** (le dossier `motion/` ne doit PAS exister avant, sinon `cp -R` l'imbrique) :
   ```bash
   cp -R "$K/template" "$R/motion"
   ```
2. **Transcript mot à mot de la vidéo montée** :
   `"$K/scripts/transcribe.sh" "$R/<STEM>.reel.mp4" "$R/motion-work" [durée] [langue, défaut fr]`
   (mettre `en` pour une prise en anglais, la même langue qu'au montage)
   (~2 min CPU pour 80 s). Sort `aligned.json` + `words.txt` (`début fin mot`). Tous les temps
   viennent de là, jamais estimés. Durée utile : couper le noir de fin s'il y en a
   (`ffmpeg -i <reel> -af silencedetect=n=-45dB:d=2 -f null -`).
3. **Le brief** : remplir `$R/motion/BRIEF-motion.md` (déjà copié avec le gabarit : inputs,
   direction, structure, build, gotchas, start). La section structure = les zones, chacune avec
   SES mots et leurs temps.
4. **Plan des zones**, en table : zone, temps (lus dans `words.txt`), ce que tu dis, ce qui
   s'affiche (tes mots, 1 à 6), fond, geste de la main (note, cercle, surligneur, flèche, coche),
   et l'effet que tu avais écrit dans ton script. Une zone = une idée, 3 à 10 s. Rien d'inventé,
   aucun chiffre sans source. Texte : ton ton (`STYLE.md`), tutoiement, zéro tiret cadratin. Si
   arrêt prévu : te montrer la table + 4 images fixes, attendre ton go.
5. **Construire**, depuis `$R/motion/` :
   - Visage : zone 1050 à 1920 (1080x870). Recadrer la vidéo montée, yeux vers 35 % de la
     hauteur de la boîte (choisir `Y` sur une image fixe) :
     `ffmpeg -i "$R/<STEM>.reel.mp4" -vf crop=1080:870:0:<Y> -c:a copy assets/face.mp4`.
   - Durée : le gabarit vaut 79.25 s. `sed -i '' 's/79\.25/<total>/g' index.html` (macOS ; sous
     Linux `sed -i` sans `''`) remplace les occurrences d'un coup (`#root`, `#facevid`, `#sfx`,
     `#panel`, `#beats.total`).
   - `#beats` (JSON dans `index.html`) porte TOUS les temps :
     `cam [t, durée, x, y, zoom, ease]` (ease `none` = lente poussée sur place),
     `dot [arrivée, durée, x, y]`, `blue [[début, fin]]` (le point passe au noir sur une zone
     bleue), `end` (début du mot de clôture), plus les listes du son (étape 6) et celles propres
     à la vidéo (`blocks`, `cmts` du gabarit, à retirer si inutiles).
   - Zones `.zone` (1080x980 utiles, fond plein `.bg`) placées dans le monde 3500x4400, la caméra
     va de l'une à l'autre. Réécrire le HTML des zones `#z1`..`#z8` et leur bloc d'animation
     (`// Z1 ...` jusqu'à `// Fin` exclu). Ce qui est avant `// Z1` (caméra, point, couleur du
     point) et le bloc Fin lisent `#beats` : ne pas y toucher.
   - Outils à garder : `drop` (lettres qui tombent), `fade`, `wipe`, `pop`, `draw` (trait à la
     main), la caméra (position + zoom log), le point (trajet unique, traîne sur les longs
     sauts, écrasement à l'arrivée), le `.split`, le fond `#face`, la couture.
   - Surligneurs et cercles calés sur la largeur MESURÉE du mot :
     `"$K/scripts/measure_words.py" assets/fonts/InterDisplay-Medium.woff2 <px> <letter-spacing em> "mot" ...`
6. **Son (facultatif)**, depuis `$R/motion/` : `sfx-cues.py` ne lit QUE `#beats` (son en-tête liste
   les clés). Pour chaque `drop()` écrit à l'étape 5, une ligne `drops [t, nb_lettres, pas]` ; pour
   chaque geste à la main (trait, impact, coche), une ligne `sfx [t, son, vol]`. Le gabarit
   contient des listes d'exemple : les REMPLACER, sinon les sons tombent aux anciens temps.
   Puis `python3 sfx-cues.py > sfx-cues.json && python3 "$K/scripts/sfx_mix.py" sfx-cues.json assets/sfx.wav`.
   **Aucune banque de sons n'est livrée.** Sans `$SFX_DIR` (un dossier de TES sons, nommés comme
   dans `sfx-cues.py` : `pop`, `whoosh`, `impact-bass-1`…), `sfx_mix.py` saute les sons proprement
   (seul le bruit synthétique `noise` reste) et écrit une piste silencieuse : le motion sort sans
   bruitages, la composition reste valide. Règles de mix : peu de sons (~12 à 15 pour 2 min), un
   son seulement sur un temps fort de ta voix où l'image fait un geste net, jamais un tic par
   lettre ni un clic par déplacement du point. `master` 0,55 : piste ~-26 LUFS sous la voix à -14
   (mesurer, ebur128).
7. **Vérifier**, depuis `$R/motion/` : `npm run check` (0 erreur), puis
   `npx --yes hyperframes@0.8.140 snapshot --at <milieu de chaque zone>` et REGARDER : texte
   entier, rien de coupé, visage visible, rien dans les 120 px du haut (barre de l'application),
   rien en bas à droite de la zone visage (interface).
8. **Revue unique (goût + orthographe), UNE fois, AVANT le rendu.** Un seul sous-agent
   `motion-reviewer` (`.claude/agents/motion-reviewer.md`, `model: "sonnet"`), qui n'a rien écrit :
   lance-le avec `subagent_type: "motion-reviewer"`, `model: "sonnet"`, en lui donnant le chemin de
   `index.html`, les snapshots et la liste des chaînes visibles (zones + notes `cmts`, extraites
   par toi). (Agent créé dans la session en cours : invisible tant que la session n'est pas
   relancée. Repli : un sous-agent `general-purpose`, `model: "sonnet"`, avec le corps de
   l'agent collé dans le prompt.) Il rend UNE liste de défauts classés, cible moins de 4 min.
   Portée fermée : sa liste + l'orthographe mot à mot + ce qui saute aux yeux sur les snapshots.
   Appliquer tout en un passage, re-check, re-snapshot, PAS de seconde revue. Cette revue EST la
   vérification de l'étape : ne pas relancer de vérificateur après chaque rendu (mesuré : quatre
   vérifications successives par un gros modèle = 14 min sur une vidéo, une seule à portée large
   = 9 min, une seule serrée sur Sonnet = 2,4 à 4,2 min).
9. **Pas d'effet qui fabrique des mots** (le « scramble » affichait du charabia : retiré).
10. **Rendu** : `npx --yes hyperframes@0.8.140 render -q looks -o "../<STEM>.motion.mp4"` (~1 min
    pour 80 s), puis
    `"$K/scripts/verify_render.sh" "../<STEM>.motion.mp4" assets/face.mp4 assets/sfx.wav <dossier de travail>`.
    Attendu : 1080x1920, 30 fps, durée = `total`, une piste audio, ~-14/-15 LUFS, et, si tu as des
    bruitages de ta banque (`SFX_DIR`), corrélation résidu/sfx > 0,8 ; sans banque, seuls les
    souffles `noise` sont mixés et une corrélation basse (~0,3) est normale, pas un échec. Regarder `sheet.jpg` et `last.jpg` (ton visage, pas
    du noir). Ouvrir le MP4. Le rendu se vérifie par ce script et ton regard, pas par un
    sous-agent. Un re-rendu après une retouche ne relance la revue de l'étape 8 que si des TEXTES
    ont changé, et alors sur les zones touchées seulement.
11. **Caption** : si la vidéo promet quelque chose « en caption » (une structure, une liste),
    l'écrire dans `videos/<STEM>/CAPTION.md`, même noms et même ordre qu'à l'écran, valeurs à
    remplir entre crochets. Relire contre `STYLE.md`. Moins de 2 200 signes (Instagram).
12. **Commit** par chemins nommés : `motion/index.html`, `sfx-cues.py`, `sfx-cues.json`,
    `hyperframes.json`, `package.json`, `assets/fonts/`, `motion/BRIEF-motion.md`, `CAPTION.md`.
    `.mp4`/`.wav` gitignorés ; `snapshots/` et `motion-work/` jamais.
13. **Rapport**, en puces : chemin du rendu, ce qui est à l'écran, ce que la revue a relevé et
    corrigé, ce qui reste à trancher (écart entre l'écran et ce que tu dis).

## STYLE-EXAMPLE (le style du gabarit, à remplacer par le tien)

- Esprit : playful, minimaliste, design suisse, un peu fait main. Pas de look UI/UX (fenêtres,
  terminal, cartes, puces).
- Couleurs (variables `:root`) : noir `#121212`, beige `#efe8dc`, bleu `#3d7bd9`, accent vert pâle
  `#b7c6b5` réservé à la main : notes et traits sur noir, surligneur sur beige, soulignement sur
  bleu. Pas de gris par opacité.
- Type : Inter Display Medium/Light, lettres qui tombent une à une ; Caveat pour la main ;
  JetBrains Mono pour les petits surtitres. Toutes trois sous licence OFL (voir `outils/fonts/`).
- Un seul monde, la caméra s'y déplace, un point passe d'une idée à l'autre. Les mots
  apparaissent quand tu les dis. Fin : le point grandit jusqu'à remplir le cadre.
- Pour un autre univers : change les variables, les `@font-face` (garde des polices libres de
  droits : OFL ou Apache), les zones. Pour le charger depuis `STYLE.md`, dis-le à Claude à
  l'étape 3.

## Pièges mesurés

- `.split` : espace insécable ` `, sinon les mots se collent.
- CSS `.ln > span`, jamais `.ln span` (attrape aussi les lettres).
- `draw()` cache le chemin avant de le tracer : sinon l'extrémité ronde laisse un point.
- Le point ne se pose jamais sur une ligne de base, ni au bord du cadre.
- Mots non prononcés à l'écran : interdit. Écart sens écran / sens parole : le signaler.
- Un débordement voulu porte `data-layout-allow-overflow` et finit à opacité 0.
- « Browser session never ran » dans `check` : Layout et Contrast n'ont pas tourné, les
  snapshots portent seuls la mise en page.
- Sortie : rendu `-q looks`, puis `loudnorm` à -14 LUFS (vidéo copiée), sinon `outils/video export`
  refuse ; le fichier `<STEM>.motion.mp4` est pris avant le reel.
- Vignette : l'image du TITRE d'ouverture une fois entier, pas une image du milieu. Si tu as les
  yeux fermés à cet instant, coller le bas d'un instant où tu regardes la caméra. Sortie
  `<STEM>.thumbnail.png` ; l'export la copie dans `final/`.
