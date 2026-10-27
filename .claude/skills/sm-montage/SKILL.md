---
name: sm-montage
description: "Étape 2 de la chaîne vidéo : dérusher la prise (silences, euh, hum, faux départs) ET garder la main dessus : timeline DaVinci Resolve où chaque coupe se rattrape, plus une boucle de correction par phrase avec Claude. Sortie dans videos/<STEM>/. Triggers: /sm-montage, monte ma vidéo, coupe les silences, enlève les euh, je veux pouvoir retoucher le dérush."
---

# /sm-montage

Étape 2 de la chaîne (`/sm-recherche` → `/sm-montage` → `/sm-video`, la porte qui enchaîne look,
sous-titres, caption et export).

Le moteur est la skill `derush` (`.claude/skills/derush/SKILL.md`) : la LIRE et la suivre, elle
porte la rubrique des faux départs et toutes les gardes. Cette commande ajoute ce que le dérush
automatique ne fait pas : **pouvoir rééditer**, parce qu'il ne fait pas un sans-faute.

## Rythme visé

- **Rapide, dynamique.** Un dérush auto qui garde tout le mou est « trop long » : le montage fait
  à la main est en général plus court de 30 % parce que les digressions sautent et que les blocs
  défilent vite.
- **Aucune durée cible.** On ne coupe QUE les faux départs, la régie et les phrases
  abandonnées. Une digression, un exemple, une explication de ce que fait une étape : on GARDE,
  tu repasse derrière. Couper du contenu pour tenir une durée est la pire faute (2026-10-27 :
  l'explication de `/sm-recherche` coupée pour tenir 2 min, à remettre).
- Le motion vient APRÈS ce montage validé, jamais avant : un re-montage oblige à refaire le motion.

## Étapes

0. **Rattacher les notes.** `derush prep` crée `videos/<STEM>/` au nom du fichier de la prise,
   alors que `/sm-recherche` a écrit ses notes dans un autre dossier (slug daté du sujet). Les
   trouver : `ls -t videos/*/NOTES-REPRISE.md | head -3`, prendre celle du sujet (une seule
   candidate récente : la prendre ; plusieurs sujets : demander lequel). Après l'étape 1, copier
   `NOTES-REPRISE.md` et `RECHERCHE.md` dans `videos/<STEM>/` : `/sm-motion` les lit là.
1. `derush prep "<video>"` (en arrière-plan, ~1.5x la durée). Prise en anglais (dit par
   l'utilisateur, ou évident à l'écoute) : ajouter `--lang en`. `derush` absent du PATH :
   `.claude/skills/derush/scripts/derush.sh` à la place, même arguments.
2. Étape 6 de `derush` : `derush words <STEM>`, écrire `retraction_cuts.json`.
2b. **Passages à te proposer, jamais coupés d'office** : si un passage semble hors sujet
   (digression, redite), le lister dans `videos/<STEM>/coupe-serree.md` (bornes SOURCE, la phrase,
   pourquoi) et le dire dans le rapport. Il n'entre dans `retraction_cuts.json` que sur demande.
3. `derush render <STEM>` : montage + `cuts.md` + **`<STEM>.fcpxml`** (écrit automatiquement).
4. Relire `cuts.md` (section diff) comme le dit `derush`.
5. Te rendre la main, en puces :
   - le montage : `<STEM>.derush.mp4` ;
   - **retoucher toi-même** : DaVinci Resolve, File > Import > Timeline, `<STEM>.fcpxml`.
     Chaque clip pointe sur la source entière : tirer un bord de clip fait revenir ce qui a été
     coupé. Rien n'est perdu ;
   - **retoucher par Claude** : tu dis la phrase (« remets "en fait" avant ce mot », « coupe la
     reprise sur ce passage »), voir la boucle ci-dessous.
6. Quand tu valides : `derush export <STEM>` (1080x1920, 30 fps, -14 LUFS). Si tu as retouché
   dans Resolve : exporter de Resolve (H.264, qualité master), puis
   `derush export <STEM> --from <export-resolve.mp4>` pour la même spec de sortie. Dans les
   deux cas `/sm-motion` prend `<STEM>.reel.mp4`. Tu peux aussi monter seul, dans n'importe quel
   logiciel : même chemin (`--from`). `/sm-motion` ne démarre que sur ce fichier validé.
   Suite : `/sm-video <STEM>` (la chaîne continue : étalonnage, sous-titres, caption, export).

## Boucle de correction par phrase

- Retrouver la phrase dans `derush words <STEM>` (bornes SOURCE).
- Mot coupé à tort : retirer la plage fautive de `_work/silence_cuts.json` (mot murmuré avalé par
  le seuil), `_work/gap_cuts.json`, `_work/filler_cuts.json` ou `retraction_cuts.json` (celle qui
  la couvre). `_work/` est gitignoré et **`derush prep` le réécrit** : après une correction, ne
  jamais relancer `prep`. Faux départ resté : l'ajouter à `retraction_cuts.json`.
- `derush render <STEM>`, puis vérifier dans la section diff de `cuts.md` que seule la phrase
  visée a bougé. Le `.fcpxml` est réécrit avec.
- Chaque correction demandée est un raté du dérush auto : noter une ligne dans
  `NOTES-DERUSH.md` à la racine du dépôt (quoi, quelle couche l'a coupé), pour que la rubrique
  s'améliore au lieu de rater pareil la fois suivante.

## Connu

- `<STEM>.derush.mp4` dure ~30 ms de plus par coupe que la somme de `keep.json`. Le `.fcpxml`
  suit `keep.json`, au cadre près.
- L'import Resolve du `.fcpxml` a été testé (Resolve 21, version gratuite) : un clip V1 et un clip
  A1 par plage, timeline 1080x1920 à 30 i/s, points d'entrée au cadre près, image droite et plein
  cadre. Le scripting externe est fermé sur Resolve gratuit. Audio 44,1 kHz non testé.
