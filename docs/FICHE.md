# Mon pipeline vidéo face caméra

## En une phrase

Je parle à la caméra, je donne la prise à Claude Code, il monte la vidéo et pose les effets que j'ai écrits dans mon script. Je valide chaque étape.

## La version à dire en 30 secondes

Je filme une prise, sans couper. Claude enlève les silences, les euh et les phrases que je reprends. Dans mon script, j'écris ce que je veux voir à l'écran. Claude transcrit ma voix mot à mot et fait apparaître chaque effet au moment où je le dis. L'animation, c'est du HTML rendu en vidéo par HyperFrames. Il s'arrête à chaque étape, je regarde, je valide. Rien ne se publie tout seul.

## Les étapes

`/sm-video <vidéo>` enchaîne tout : il regarde où en est la vidéo, lance l'étape suivante, s'arrête quand c'est à moi de valider, et reprend là où on en était au prochain appel. Chaque étape a aussi sa skill.

1. Recherche, `/sm-recherche <sujet>`. Claude trouve 3 à 5 sources, un contrepoint, et écrit mes notes. Moi : je lis, je filme.
2. Montage, `/sm-montage <ma prise>`. Claude coupe les silences, les euh, les faux départs. Moi : je valide les coupes, je retouche phrase par phrase.
3. Étalonnage, `/sm-etalonnage <vidéo>`. Claude sort une planche de looks. Moi : je choisis A, B, C ou D. Une seule fois : le look est repris pour les vidéos suivantes.
4. Motion, `/sm-motion <vidéo>`, si je le veux. Claude lit mon script, cale chaque effet sur le mot que je prononce, et rend le tout. Moi : je regarde, je valide.
5. Sous-titres, `/sm-soustitres <vidéo>`. Claude écrit l'accroche et les idées clés à l'écran. Moi : je valide la vidéo.
6. Caption, `/sm-caption <vidéo>`. Claude écrit le texte et le relit contre ce que j'ai dit. Moi : je relis.
7. Export, `/sm-export <vidéo>`. Claude range la vidéo, la caption et la vignette dans un seul dossier et vérifie ce qu'il contient. Moi : je publie.

## DaVinci Resolve : optionnel

Le pipeline marche sans. Resolve (la version gratuite suffit) apporte deux choses :

- les looks film de l'étalonnage (B, C et D). Sans lui, la planche ne montre que A, le look neutre ;
- la retouche manuelle des coupes, via le fichier `.fcpxml` du montage.

Les coupes elles-mêmes sont faites par ffmpeg, pas par Resolve.

## Où ça marche

- Claude Code dans le terminal : oui, c'est comme ça que je l'utilise.
- Claude Desktop, onglet Code : oui, c'est le même Claude Code, en local sur ta machine. Le chat de l'app, lui, ne rend pas de vidéo.
- Cowork, pour les effets HyperFrames : sa machine a déjà Node 22 et ffmpeg, et il installe des plugins. Le navigateur de rendu se télécharge au premier rendu ; s'il est bloqué, `npx hyperframes cloud render` rend chez HeyGen (compte HeyGen, payant au crédit). Pour la chaîne entière, avec le dérush et la transcription, prends Claude Code.
- Claude Code sur le web : possible, mais il faut envoyer ta vidéo brute dans la machine distante et y installer la transcription. Lourd.
- Le chat claude.ai : non. Pas de terminal, pas de rendu vidéo.

## HyperFrames, il faut l'installer ?

Oui, les skills : `npx skills add heygen-com/hyperframes --all`. Le rendu, lui, se lance tout seul. Il te faut Node 22, ffmpeg et Chrome sur ta machine. L'installeur du repo te dit ce qui manque.

## Les 3 questions qu'on me pose

- Il faut savoir coder ? Non. Tu tapes une commande, tu lis, tu valides. Il faut juste accepter d'ouvrir un terminal ou l'onglet Code.
- Ça coûte combien ? Un abonnement Claude qui inclut Claude Code. Le reste tourne en local et gratuit : ffmpeg, la transcription, le rendu.
- Claude décide tout seul ? Non. Il s'arrête à chaque étape et attend mon accord. La publication, c'est moi.
