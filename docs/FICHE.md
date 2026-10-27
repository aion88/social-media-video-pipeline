# Mon pipeline vidéo face caméra

## En une phrase

Je parle à la caméra, je donne la prise à Claude Code, il monte la vidéo et pose les effets que j'ai écrits dans mon script. Je valide chaque étape.

## La version à dire en 30 secondes

Je filme une prise, sans couper. Claude enlève les silences, les euh et les phrases que je reprends. Dans mon script, j'écris ce que je veux voir à l'écran. Claude transcrit ma voix mot à mot et fait apparaître chaque effet au moment où je le dis. L'animation, c'est du HTML rendu en vidéo par HyperFrames. Il s'arrête à chaque étape, je regarde, je valide. Rien ne se publie tout seul.

## Les étapes

1. Recherche, `/sm-recherche <sujet>`. Claude trouve 3 à 5 sources, un contrepoint, et écrit mes notes. Moi : je lis, je filme.
2. Montage, `/sm-montage <ma prise>`. Claude coupe les silences, les euh, les faux départs. Moi : je valide les coupes, je retouche phrase par phrase.
3. Look. Claude sort une planche de 4 étalonnages. Moi : je choisis A, B, C ou D.
4. Motion, `/sm-motion <vidéo>`. Claude lit mon script, cale chaque effet sur le mot que je prononce, et rend le tout. Moi : je regarde, je valide.
5. Sous-titres. Claude écrit les idées clés à l'écran. Moi : je valide.
6. Caption et export. Claude écrit la caption et range la vidéo, la caption et la vignette dans un seul dossier. Moi : je publie.

`/sm-video` est la porte d'entrée : il regarde où en est la vidéo et lance l'étape suivante.

## Est-ce que ça marche chez toi ?

- Claude Code dans le terminal : oui, c'est comme ça que je l'utilise.
- Claude Desktop, onglet Code : oui, c'est le même Claude Code, en local sur ta machine.
- Claude Code sur le web : possible, mais il faut envoyer ta vidéo brute dans la machine distante et y installer la transcription. Lourd.
- Le chat claude.ai : non. Pas de terminal, pas de rendu vidéo.

## HyperFrames, il faut l'installer ?

Non. La skill le lance toute seule. Il te faut Node, ffmpeg et un navigateur Chrome sur ta machine. L'installeur du repo te dit ce qui manque.

## Les 3 questions qu'on me pose

- Il faut savoir coder ? Non. Tu tapes une commande, tu lis, tu valides. Il faut juste accepter d'ouvrir un terminal ou l'onglet Code.
- Ça coûte combien ? Un abonnement Claude qui inclut Claude Code. Le reste tourne en local et gratuit : ffmpeg, la transcription, le rendu.
- Claude décide tout seul ? Non. Il s'arrête à chaque étape et attend mon accord. La publication, c'est moi.
