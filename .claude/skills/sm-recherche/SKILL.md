---
name: sm-recherche
description: "Étape 1 de la chaîne vidéo : recherche sourcée + notes de ce que tu vas dire face caméra. Entrée = un sujet, une prise ratée ou un transcript. Sortie = RECHERCHE.md, NOTES-REPRISE.md et un document prompteur recherche.html (angle, ton point de vue challengé, arguments sourcés, script) dans videos/<dossier>/. Triggers: /sm-recherche, recherche pour ma vidéo, je connais pas bien mon sujet, prépare-moi mes notes, quoi dire."
---

# /sm-recherche

Étape 1 de la chaîne vidéo. La porte de toute la chaîne : `/sm-video <STEM>`.

1. `/sm-recherche` : savoir quoi dire (ici).
2. `/sm-montage` : dérusher la prise, en gardant la main sur les coupes.
3. `/sm-video <STEM>` : la suite, une étape par session (look, sous-titres, caption, export ;
   `/sm-motion` si tu veux le motion).

## Entrée

- Un sujet en une phrase, OU une vidéo ratée (la transcrire : `derush prep <video>` écrit
  `transcript.txt`), OU un transcript collé.
- Dossier : `videos/<STEM>/` à la racine du dépôt. Le créer s'il n'existe pas (sujet seul : slug
  daté `AAAA-MM-JJ-sujet`).

## Étapes

1. **Lire le transcript** et en sortir trois listes : le SUJET (ce que le spectateur saura faire
   après), les affirmations à vérifier, les questions ouvertes. Sujet seul, sans prise : les
   affirmations à vérifier sont celles de ta phrase de sujet et ce que tu crois savoir (te le
   demander en une question s'il n'y a rien).
2. **Recherche web, faite par Claude** avec `WebSearch` et `WebFetch` : 3 à 5 sources réelles, ouvertes
   et lues (pas seulement les extraits du moteur), dont UN contrepoint (la meilleure objection
   publiée à ta thèse). Pour chaque affirmation, noter l'URL exacte et ce que la page dit. Si
   la recherche est large (plus de 3 affirmations indépendantes), déléguer chaque affirmation à un
   sous-agent (`model: "sonnet"`) qui rend les URL et les citations.
   **« Non trouvé » ne veut pas dire faux** : revérifier à la source (page officielle, doc) avant
   de retirer un fait des notes, et écrire la réconciliation dans `RECHERCHE.md`. Ce qui n'est pas
   sourcé est écrit comme tel. Jamais de source inventée, jamais de chiffre sans source.
3. **`RECHERCHE.md`** dans le dossier : les sources (URL, date de consultation, ce qu'elles
   prouvent), le contrepoint, plus une table « ce que tu as dit / ce qui est vrai / source » pour
   chaque affirmation de la prise (sujet seul : « ce qu'on croit / ce qui est vrai / source »).
   Dire le nom du dossier : `/sm-montage` étape 0 y reprendra les notes une fois la vidéo
   tournée.
4. **`NOTES-REPRISE.md`** :
   - Accroche, 3 versions. **Elle porte le SUJET, pas un chiffre ramassé en route.** Un chiffre
     n'entre dans l'accroche que s'il EST le sujet.
   - Les 3 points clés, une phrase chacun, avec le nom ou le chiffre sourcé.
   - Le contenu principal (structure, étapes, exemples courts). C'est ce que le motion montrera à
     l'écran : noms courts, dans l'ordre où tu les diras, mêmes mots que la caption.
   - **Les effets que tu veux à l'écran** (« cercle sur ce mot », « la liste se construit », « le
     chiffre arrive »), marqués dans le script : `/sm-motion` les prend comme matière première.
   - Ce que la vidéo promet en caption (une structure, une liste, un modèle) : l'annoncer face
     caméra, la caption le livre.
   - Les highlights, une ligne chacun.
   - Ce qu'il ne faut PAS redire : chaque affirmation de la prise que la recherche contredit.
   - Clôture sans formule théâtrale. Repères à dire, pas un texte à lire. 60 à 90 s visés.
5. **Ton** : relire les notes et la caption contre `STYLE.md` (à remplir une fois). Zéro tiret
   cadratin, tutoiement si c'est ton style.
6. **Vérification** : un sous-agent qui n'a rien écrit (`model: "sonnet"`) re-dérive 5 faits de
   `NOTES-REPRISE.md` depuis les URL de `RECHERCHE.md`. Verdict en bas du fichier : vérifié /
   corrigé / bloqué.
7. **Le livrable : un document prompteur**, `recherche.html` dans le dossier (une page
   autonome, à ouvrir dans le navigateur ; la publier comme page partageable seulement si ton
   environnement le permet). C'est LUI que tu lis, les `.md` sont l'arrière-boutique. Contenu :
   - **L'angle** en une phrase, en tête, gros.
   - **Ton point de vue, challengé** : ce que tu penses (ta phrase de sujet, ta prise ; si on le
     déduit, l'écrire « je suppose que tu penses... »), l'objection la plus forte, ce qui tient
     quand même.
   - **Les arguments**, 4 à 6, dans l'ordre où tu les diras. Chacun : une phrase à dire (gros,
     lisible comme un prompteur), la preuve chiffrée avec son renvoi de source [n], l'objection
     qu'on te fera et sa réponse.
   - **Le script prompteur** : 6 à 10 lignes courtes, dans l'ordre, rien d'autre.
   - **Ce qu'il ne faut pas dire.**
   - **Les sources numérotées**, cliquables, chacune avec ce qu'elle prouve.
   - **Écrit pour un spectateur qui ne connaît pas le sujet** : zéro jargon sans traduction.
   - **Ne jamais te prêter une méthode ou un avis que tu n'as pas donné.** Sans avis donné : écrire
     les idées reçues du spectateur, et te demander le tien.
   - Langage simple. Pas de catalogue en vrac : un outil n'apparaît que comme preuve ou comme
     geste d'un argument.
8. **Répondre en puces** : le chemin du document en premier, l'angle, ce qui contredit ton point
   de vue, où sont les `.md`.

## Ne pas faire

- Pas de motion ici, pas de montage. Une étape, une commande.
- Pas de source inventée, pas de chiffre sans source.
