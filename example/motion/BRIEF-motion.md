<inputs>
Vidéo montée : [videos/habits_take2/habits_take2.reel.mp4], durée utile 63 s. Transcript mot à mot : [motion-work/words.txt].
Notes : [NOTES-REPRISE.md]. Ce que tu promets en caption : la liste des trois habitudes.
</inputs>

<direction>
Couche motion verticale 1080x1920 pour une vidéo face caméra sur trois habitudes pour garder des notes utiles. Motion de 0 à 980 px, ton visage intact de 1050 à 1920, une fine couture entre les deux.
STYLE-EXAMPLE (à remplacer par le tien). Un seul monde, fonds pleins noir #121212, beige #efe8dc, bleu #3d7bd9. Inter Display Medium/Light dont les lettres tombent une à une, Caveat pour la main, JetBrains Mono pour les petits surtitres. Le vert pâle #b7c6b5 ne sert qu'à la main : notes, traits, surligneur, soulignement. Un point guide passe d'une idée à l'autre et porte chaque transition. La caméra se déplace dans le monde pour que chaque idée remplisse le cadre. Les mots apparaissent quand tu les dis, jamais avant.

Interdits : look UI/UX (fenêtres, terminal, cartes, puces), coupes sèches, titres centrés en série, halos, particules, emojis, gris par opacité, flou pendant les mouvements de caméra, effet scramble, texte dans les 120 px du haut, toute affirmation que tu ne fais pas.
</direction>

<structure>
Environ 63 secondes, temps lus dans words.txt.

Z1 accroche (0.0 à 5.2) : « trois habitudes pour que tes notes servent vraiment », geste : le mot « servent » surligné (effet écrit dans le script : « surligne servent »).
Z2 habitude 1 (5.2 à 19.8) : « une date sur chaque note », geste : cercle sur « date ».
Z3 habitude 2 (19.8 à 36.4) : « un seul endroit », geste : trait qui rassemble trois mots en un.
Z4 habitude 3 (36.4 à 52.1) : « relire le dimanche », geste : coche, le chiffre « 10 min » arrive (effet écrit dans le script).
Fin (52.1 à 63.0) : le point grandit jusqu'à remplir le cadre, mot de clôture « Merci ».
</structure>

<build>
1. Copie du gabarit sm-motion, visage recadré dans assets/face.mp4 avec le son de la vidéo montée.
2. Tous les temps dans #beats (cam, dot, listes propres à la vidéo). Une seule timeline GSAP en pause.
3. Surligneurs et cercles calés sur les largeurs mesurées (measure_words.py).
4. Sons facultatifs (sfx-cues.py lit #beats, banque = $SFX_DIR), piste ~12 dB sous la voix.
5. check à 0 erreur, une image fixe par zone, revue unique par l'agent motion-reviewer, orthographe de chaque texte.
</build>

<gotchas>
Le point ne téléporte jamais et ne se pose jamais sur une ligne de base. Le texte dit ce que tu dis, en tutoyant. Rien sur ton visage, rien dans les 120 px du haut. Dernière image : ton visage, pas du noir.
</gotchas>

<start>
Montre la table des zones et 4 images fixes avant de construire le reste.
</start>
