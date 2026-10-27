# Rushs : du brut à la vidéo à poster

Un dossier par vidéo, nommé comme le fichier iPhone. Rien ne sort d'ici sans passer par `derush`.
Toute session Claude qui touche une vidéo parlée lit cette page, puis `INDEX.md` (à créer à la première vidéo : une ligne par vidéo).

Les médias (`.mov`, `.mp4`, `.wav`) ne sont jamais suivis par git (`.gitignore`). `derush` se lance par son chemin
(`.claude/skills/derush/scripts/derush.sh`) ou par `derush` si `outils/installer.sh --lier` l'a lié dans ton PATH.

## En trois commandes

```bash
derush prep ~/Downloads/IMG_4567.MOV   # range la source ici, transcrit, repère silences et euh. ~1,5x la durée
derush words IMG_4567                   # le transcript mot à mot : toi ou Claude écrivez les faux départs
derush render IMG_4567 && derush export IMG_4567   # monte, vérifie, sort le fichier à poster
```

Depuis Claude Code : « dérushe IMG_4567 » suffit. La skill `derush` enchaîne les trois et écrit
les faux départs elle-même. Pour une passe sans lecture (0 faux départ) : `derush all <video>`.

La chaîne entière, de la recherche à l'export : `/sm-video IMG_4567`. Elle lit `outils/video statut`,
appelle la skill de l'étape suivante dans la MÊME session, s'arrête à chaque validation (la tienne), puis
reprend là où la vidéo en est au prochain appel. Chaque étape a aussi sa commande :

| Étape | Skill | Tu valides |
|---|---|---|
| recherche | `/sm-recherche <sujet>` | les notes, puis tu filme |
| montage | `/sm-montage <prise>`, puis `derush export <STEM>` | les coupes |
| étalonnage (clé `look`) | `/sm-etalonnage <STEM>` | la lettre du look |
| motion, optionnel | `/sm-motion <STEM>` | le motion |
| sous-titres (clé `overlays`) | `/sm-soustitres <STEM>` | la vidéo |
| caption | `/sm-caption <STEM>` | le texte |
| export | `/sm-export <STEM>` | rien : publier est ton geste |

DaVinci Resolve est OPTIONNEL (gratuit suffit). Il apporte les LUT film de l'étalonnage (sans lui,
seul le look A, neutre, est proposé) et la retouche manuelle des coupes via le `.fcpxml`. Les coupes
elles-mêmes sont faites par ffmpeg, pas par Resolve.

`diag`, `repare` et `medias` n'ont aucun outil : étapes optionnelles, `statut` les affiche
« optionnelle, pas d'outil » et elles ne bloquent jamais la suite. Le nom affiché de `look` est
« étalonnage » (`outils/video valide <STEM> etalonnage` marche aussi). La finition est plus bas.

## Où en est une vidéo

```bash
cd <racine du dépôt>
outils/video statut IMG_4567   # 10 lignes max : ce qui est fait, ce qui attend ton geste, la commande suivante
outils/video statut            # une ligne par vidéo en cours ; --toutes ajoute les terminées
outils/video valide IMG_4567 overlays   # ton OK sur une étape faite (montage, overlays, caption...)
```

`statut` n'écrit rien. Avec `ETAT.json` (section suivante), il le compare aux fichiers et dit
« ETAT.json en retard » si un fichier est plus récent que l'étape notée : un `derush` lancé à la
main, par exemple. Sans `ETAT.json` (dossier d'avant la chaîne), il lit l'ancienne chaîne sur les
fichiers, la plus haute trace gagne : `<STEM>.motion.mp4` = motion rendu ; `<STEM>.overlays.mp4`
et `caption.txt` = finition faite, à exporter ; `<STEM>.overlays.mp4` seul = sous-titres à valider ;
`overlays/overlays.json` seul = sous-titres commencés ; `motion/` seul = motion commencé ;
`<STEM>.reel.mp4` = exportée (sans caption : la finition est proposée) ; `cuts.md` ou `<STEM>.derush.mp4` = montée, à valider ;
`_work/aligned.json` + `transcript.txt` = transcrite ; la prise seule = rangée ; `NOTES-REPRISE.md`
ou `RECHERCHE.md` seuls = recherche faite, prise à tourner. Si un `_work/source.txt`
vise un chemin disparu, `statut` le dit et donne la commande avec le chemin du fichier.

## La finition : étalonnage, sous-titres, caption, export

```bash
outils/look.py planche videos/IMG_4567/IMG_4567.reel.mp4   # /sm-etalonnage : les looks sur une planche, une seule fois (sans Resolve : A seul)
outils/look.py fixe D                    # outils/looks/look.cube (+ copie dans DaVinci LUT/Perso si Resolve est là)
outils/overlays.py texte IMG_4567        # /sm-soustitres : les phrases datées (transcrit la vidéo la 1re fois)
outils/overlays.py essai IMG_4567        # le calendrier des idées, sans rendu
outils/overlays.py IMG_4567              # IMG_4567.overlays.mp4 + overlays/check.jpg, ~1 min
# la caption : Claude la relit contre STYLE.md (pas de contrôle automatique)
outils/video export IMG_4567 mon-sujet   # /sm-export : videos/IMG_4567/final/ : mon-sujet.mp4 + caption.txt + thumbnail.png ; refuse sans caption ou hors -14 LUFS (±1)
```

Les idées (`overlays/overlays.json`) et la caption s'écrivent avec Claude, selon les règles de
`.claude/skills/sm-soustitres/` et `.claude/skills/sm-caption/` : une idée par phrase, ses mots, mots clés surlignés,
fondu sans parallaxe, sous le menton. Le look passe sous le texte, une seule fois (`/sm-etalonnage`) : sans
`outils/looks/look.cube` ni clé `look`, le rendu refuse.

## Ce qu'il y a dans un dossier

| Fichier | C'est quoi | Dans git |
|---|---|---|
| `IMG_4567.MOV` | La source, déplacée depuis Downloads par `prep` | non (trop lourd) |
| `IMG_4567.derush.mp4` | Le montage, qualité master (fps et débit de la source) | non |
| `IMG_4567.reel.mp4` | La version à poster, voir la spec ci-dessous | non |
| `cuts.md` | Le rapport : durées, couches de coupe, faux départs, diff source/sortie | oui |
| `retraction_cuts.json` | Les faux départs, avec le texte et le motif de chaque coupe | oui |
| `transcript.txt` | Le transcript lisible, bornes alignées sur le son | oui |
| `keep.json` | Les plages gardées. Suffit à re-monter sans retranscrire | oui |
| `IMG_4567.fcpxml` | La timeline DaVinci du montage (File > Import > Timeline), écrite par `render`. Chaque clip pointe sur la source entière : tirer un bord rend ce qui a été coupé | oui |
| `coupe-serree.md` | Les passages coupés en plus des faux départs, avec leur motif (`/sm-montage`, étape 2b) | oui |
| `logos.json`, `IMG_4567.logos.mp4` | Les logos posés par `derush logos`. `export` part de la version avec logos si elle existe | json oui, mp4 non |
| `NOTES-REPRISE.md`, `RECHERCHE.md` | Les notes et la recherche de `/sm-recherche`, écrites ici ou copiées par `/sm-montage` (étape 0) | oui |
| `caption.txt` | La caption, un seul nom désormais : brouillon dans le dossier de recherche, version finale ici, relue contre `STYLE.md`. `CAPTION.md` (ancien nom) disparaît | oui |
| `overlays/` | Les sous-titres : `overlays.json` (accroche et idées, écrit avec Claude), `sous-titres.json` (quoi, quand), `check.jpg` (la planche), `_work/aligned.json` (le transcript daté) | json et jpg oui, `_work/` non |
| `IMG_4567.overlays.mp4`, `IMG_4567.thumbnail.png` | La vidéo avec look et sous-titres, son copié tel quel ; la vignette à 1,3 s | non (régénérables) |
| `look/` | Les looks d'essai de cette vidéo : `planche.jpg`, un cube d'essai | planche oui, cube non (`look.py cube` le refait) |
| `motion/` | Le projet HyperFrames du motion (`/sm-motion`) : `index.html`, `sfx-cues.py`, `sfx-cues.json`, `BRIEF-motion.md`, polices | en partie : ni `.mp4`, `.mov`, `.wav` (`.gitignore`) ; `snapshots/` jamais |
| `IMG_4567.motion.mp4` | Le rendu du motion, 1080x1920, 30 fps, -14 LUFS | non |
| `medias/` | Réservé (pas d'outil) : les médias dont tu parles, `MEDIAS.json` (source, crédit, statut de chacun) et la planche numérotée | json oui, vidéos non |
| `davinci/` | Réservé (pas d'outil) : la timeline DaVinci du motion, toi en V1, le bandeau en V2, un média par piste au-dessus | fcpxml oui, vidéos non |
| `ETAT.json` | L'état de la vidéo, étape par étape (schéma ci-dessous). Écrit par `outils/video valide` et `export`  | oui |
| `broll/`, `v2/` | Médias et versions faits à la main, avant `medias/`. `statut` les montre « hors chaîne » | selon le dossier |
| `_work/` | Intermédiaires (wav, whisper, cuts par couche). Se régénère | non |

Ce qui est dans git est la mémoire du montage : ce qui a été coupé et pourquoi.

## ETAT.json, l'état d'une vidéo

Un fichier par dossier, un seul écrivain : `outils/video`, par `valide` et `export`. Le premier `valide` d'une
vidéo commencée sans lui le tire des fichiers : une étape que ses fichiers montrent est faite, motion est sautée tant qu'il
n'y a pas de motion. `diag`, `repare` et `medias` n'ont aucun outil : OPTIONNELLES, jamais bloquantes, `statut` les affiche
« optionnelle, pas d'outil » (un ancien `ETAT.json` qui les porte se lit comme avant). L'étalonnage (clé `look`) n'est plus sauté :
`outils/looks/LOOK.json`, écrit par `look.py fixe`, le montre fait pour toutes les vidéos. Le schéma est défini en un seul endroit, l'en-tête de `outils/video` :

```json
{
  "version": 1,
  "stem": "IMG_4640",
  "source_origine": "~/Downloads/IMG_4640.MOV",
  "recherche": "videos/2026-10-20-<sujet>",
  "etapes": {
    "diag":    {"fait": "2026-10-20T14:03:12+02:00", "mesures": {"verdict": "OK"}, "valide": true},
    "repare":  {"fait": "2026-10-20T14:03:12+02:00", "mesures": {"saute": "diag OK"}, "valide": true},
    "montage": {"fait": "2026-10-20T14:40:05+02:00", "mesures": {}, "valide": false},
    "look":    {"fait": null, "mesures": {}, "valide": false},
    "medias":  {"fait": null, "mesures": {}, "valide": false},
    "motion":  {"fait": null, "mesures": {"saute": "pas demandé, /sm-motion le fait"}, "valide": false},
    "overlays": {"fait": null, "mesures": {}, "valide": false},
    "caption": {"fait": null, "mesures": {}, "valide": false},
    "export":  {"fait": null, "mesures": {}, "valide": false}
  }
}
```

- `fait` : date ET heure ISO 8601 avec fuseau, `null` tant que l'étape n'est pas faite. `statut`
  compare cette heure à celle des fichiers ; une date seule vaut la fin de ce jour-là.
- `mesures` : ce que l'étape a mesuré, libre par étape. `"saute": "<raison>"` = étape passée exprès
  (pas de réparation quand le diag est bon, pas de médias sans référence).
- `valide` : ton OK, posé par `outils/video valide <STEM> <étape>`. `false` sur une étape faite =
  elle attend ton geste (montage, médias, motion, overlays, caption). Les étapes automatiques
  s'écrivent à `true`.
- Le fichier qui montre chaque étape, comparé à `fait` : `<STEM>.repare.mp4` (repare), `cuts.md`
  ou `<STEM>.derush.mp4` (montage), `outils/looks/LOOK.json` (look, fixé une fois pour toutes),
  `medias/MEDIAS.json` (medias), `<STEM>.motion.mp4` (motion), `<STEM>.overlays.mp4` (overlays),
  `caption.txt` (caption). `diag` et `export` n'ont pas de fichier dans le dossier : `ETAT.json`
  seul les porte (l'export note où il a copié la vidéo et sa sonie). Une étape plus ancienne qu'une étape d'avant est à
  refaire (un re-montage après l'export périme l'export).

## La spec de sortie

| | Master `.derush.mp4` | À poster `.reel.mp4` |
|---|---|---|
| Image | 1080x1920 (9:16 natif iPhone), fps de la source (120) | 1080x1920, **30 fps**, H.264 high 4.1, crf 20, yuv420p |
| Son | AAC, niveau de la source | AAC 192k 48 kHz, **voix à -14 LUFS** (true peak -1,5) |
| Conteneur | mp4 | mp4 `faststart` |
| Pour quoi | Re-monter, re-exporter, archiver | Uploader tel quel |

- 30 fps : les plateformes ré-encodent à 30. 120 fps triple le poids pour rien sur un visage.
- -14 LUFS : une voix de téléphone sort entre -20 et -28 selon la pièce. Sans normalisation,
  deux vidéos à la suite n'ont pas le même volume. -14 est le niveau de référence des
  plateformes de streaming. [classe de preuve : connaissance générale, non recontrôlée ce jour]
- Les coupes : fondu audio 12 ms par raccord, coupe à l'image près. Un raccord se voit (jump
  cut assumé), il ne s'entend pas.

## Où ça va

| Plateforme | Format accepté | Durée max | Taille max | Zone sûre | Ce qui compte | Source (lue le 2026-10-08) |
|---|---|---|---|---|---|---|
| Instagram Reels | ratio de 9:16 à 1,91:1 ; 720 px et 30 fps minimum | 20 min enregistrées ou montées ; au-delà de 3 min, le reel n'est plus recommandé aux nouvelles audiences ; un reel boosté : 90 s et 9:16 | non trouvée sur page officielle pour un reel organique (4 Go pour une pub Reels) | 14 % en haut, 35 % en bas, 6 % sur les côtés (spec PUB Meta, aucune page organique ne la donne) | couper à 3 min max si on veut la reco | [taille et ratio](https://help.instagram.com/1038071743007909), [durée](https://help.instagram.com/2720958398006062), [boost](https://help.instagram.com/570215404599013), [zone sûre et 4 Go](https://www.facebook.com/business/ads-guide/update/video/instagram-reels) |
| TikTok | non trouvé sur page officielle grand public ; l'API n'impose aucun ratio (360 à 4096 px de côté) ; les pubs recommandent 9:16, acceptent 16:9 et 1:1 | 3 min pour tous les comptes, 5 ou 10 min selon le compte (page développeurs) ; le « 60 min » des blogs : non trouvé sur page officielle | 4 Go (API) ; 500 Mo (pubs) | non chiffrée sur page officielle (la page pub renvoie à des fichiers à télécharger, non lus) | laisser la colonne de droite libre reste un usage, pas une spec | [page développeurs](https://developers.tiktok.com/docs/en/content-posting-api-media-transfer-guide), [spec pub](https://ads.tiktok.com/help/article/video-ads-specifications) |
| LinkedIn | ratio de 1:2,4 à 2,4:1, donc 9:16 et 1:1 passent ; 256x144 à 4096x2304 | 15 min depuis un profil (desktop et mobile) ; 10 min depuis une Page entreprise | 5 Go | non trouvée sur page officielle | autoplay **muet** : sans sous-titres, personne ne reste | [profil](https://www.linkedin.com/help/linkedin/answer/a548372), [Page entreprise](https://www.linkedin.com/help/linkedin/answer/a1311816) |
| YouTube Shorts | carré ou vertical, sinon c'est une vidéo longue ; 1080p max depuis l'app | 3 min | pas de limite propre aux Shorts ; limite générale 256 Go ou 12 h | non trouvée sur page officielle | le titre fait le travail du hook | [classement Shorts](https://support.google.com/youtube/answer/15424877), [upload](https://support.google.com/youtube/answer/12779649), [débuter](https://support.google.com/youtube/answer/10059070), [256 Go](https://support.google.com/youtube/answer/71673) |

Classe de preuve : chaque valeur chiffrée a été lue le 2026-10-08 sur la page officielle liée dans
la dernière colonne. Les pages Instagram ont été lues via un rendu texte de l'URL officielle, le
site refusant la lecture directe. Reste non sourcé : la taille max d'un reel organique, le ratio
et la durée d'upload TikTok côté grand public (seules la page développeurs et la spec pub ont été
trouvées), et les zones sûres hors Instagram. La zone sûre Instagram vient d'une spec publicitaire.

**Fichier SRT : pas dans la chaîne.** Les sous-titres brûlés sont ceux de `outils/overlays.py`.

## Conventions

- Le nom reste le nom iPhone (`IMG_4567`). Il lie la source, le montage, le rapport et la
  ligne d'`INDEX.md`. On ne renomme pas.
- `INDEX.md` porte une ligne par vidéo : date, durées, sujet en une phrase, état. L'état vaut
  `brut`, `monté`, ou `posté <plateforme> <date>`. C'est toi qui passes à `posté`.
- Downloads n'est pas un dossier de rushs. `derush prep` en sort la source.
- Un mot de vrai contenu coupé est la pire faute. La chaîne refuse de rendre si un mot gardé
  serait rogné (`check_clips`). Un rapport dont la section « diff » montre un `delete` non
  voulu se corrige dans `retraction_cuts.json` puis `derush render`, une minute.

## Réglages

- Rythme plus serré (format très court) : `derush prep <video> --min 0.3 --pad 0.08`.
- Rythme plus posé : `--min 0.8 --pad 0.2`.
- Voix faible ou pièce bruyante : `--noise -40`.
- Anglais : `--lang en`.
- Changer un réglage ou un faux départ, puis `derush render` : une minute, pas de retranscription.

## Ce qui n'est pas vérifié

- Dans le tableau des plateformes : la taille max d'un reel organique, les limites TikTok côté
  grand public, et les zones sûres hors Instagram. Le reste est sourcé sur page officielle.
- Le rendu 30 fps depuis du 120 fps : regarder la première vidéo postée pour une saccade.
- La normalisation -14 LUFS, deux passes depuis le 2026-10-08 : mesuré -14,9 et -14,4 LUFS sur les
  deux exports mesurés. Le reliquat vient du plafond de crête à -1,5 dBTP. Passe unique : -15,8.
