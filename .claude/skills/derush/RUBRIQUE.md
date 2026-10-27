# Rubrique de détection des faux départs (étape 6)

Tu lis `derush words <STEM>` et tu écris `videos/<STEM>/retraction_cuts.json`. Cette rubrique
condense le modèle de l'auto-correction du parlé (Levelt, Clark & Wasow).

## Contrat de sortie

```json
{ "retraction_cuts": [
    { "start": 6.4, "end": 9.8, "cue_text": "enfin non", "rationale": "pourquoi cette coupe" }
] }
```

`start` = début de la pensée abandonnée (reparandum), `end` = fin du signal de correction (interregnum).
La reprise qui SUIT est GARDÉE. Liste vide `{"retraction_cuts": []}` si rien n'est un vrai faux départ.

```
[REPARANDUM]   [INTERREGNUM / SIGNAL]   [REPRISE]
 abandonné         « non attends »        remplaçant
   COUPÉ              COUPÉ                GARDÉ
```

## Test positif (couper) : TOUT doit être vrai

1. Tu invalides un contenu déjà dit (tu le nies, le juges faux ou incohérent), ET
2. tu le remplaces ou tu l'abandonnes : une version corrigée suit, ou la pensée est lâchée, ET
3. le reparandum existe dans le transcript (un signal sans parole avant lui : pas de coupe).

## Tests négatifs (NE PAS couper) : un seul suffit pour rejeter

- **Mise de côté avec délai** : « oublie le budget deux secondes », « on y revient la semaine
  prochaine ». Le contenu reste valide, il est différé.
- **Escalade additive** : « en fait c'est encore mieux ». « En fait » améliore l'affirmation, elle tient.
- **Affirmation** : « non mais c'est exactement ça ». Le « non » renforce l'accord.
- **Pause de procédure** : « attends, je te montre ». Rien n'est retiré.
- **Nuance** : « c'est plus subtil que ça ». L'affirmation est précisée, pas jetée.
- **Clôture de sujet** : « bref, de toute façon ». Ferme une chaîne sans l'invalider (« bref »
  n'est une coupe que suivi d'un vrai abandon : « bref, peu importe les critères »).

## Jusqu'où remonter le début

- **Que remplace la reprise ?** Le reparandum commence là où l'idée abandonnée diverge de la bonne.
- **Marqueurs de redémarrage** (« je reprends », « non attends je recommence ») : reparandum LARGE,
  jusqu'au début du passage refait.
- **Pivots de correction** (« non en fait », « wait no ») : reparandum ÉTROIT, la proposition précédente seulement.
- **Jamais au-delà d'un autre sujet** : une introduction partagée par la mauvaise et la bonne version est GARDÉE.
- **Test setup / élaboration** : si une affirmation d'introduction reste vraie et que seule
  l'énumération qui suit est abandonnée, le début de la coupe est l'énumération. Question décisive :
  « nies-tu CETTE proposition, ou seulement ce qui vient après ? »
- **Conservatisme** : dans le doute, la coupe la plus ÉTROITE. Laisser un bout de proposition
  fautive vaut mieux que couper une phrase juste. Sous incertitude de timestamp, arrondir vers
  l'INTÉRIEUR : début de coupe un peu plus tard (~0,3 à 0,5 s), fin un peu plus tôt. Couper trop tôt
  mange du contenu valide : la faute capitale.
- **Reparandum sur plusieurs segments** : la coupe les couvre tous.
- **Signal et reprise dans le même segment** : terminer la coupe AU MILIEU du segment, au mot où
  la reprise commence (interpoler par position de mot), jamais à la fin du segment, ce qui mangerait
  le début de la reprise : la pire faute.

Les bornes se lisent dans `derush words` (mots alignés sur le son). Voir `SKILL.md` pour les cas du
parlé spontané et la formule des bornes.
