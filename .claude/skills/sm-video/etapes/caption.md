# Caption

Un seul nom, `caption.txt` : brouillon dans le dossier de recherche, version finale dans
`videos/<STEM>/`. Un exemple de forme : `example/caption.txt`.

## Faire

1. Partir des notes de recherche (`videos/<STEM>/NOTES-REPRISE.md`, s'il existe), sinon du
   transcript : `outils/overlays.py texte <STEM>`.
2. Écrire `videos/<STEM>/caption.txt` :
   - texte brut, dans la langue de la vidéo ;
   - la 1re ligne accroche ;
   - des paragraphes de 1 à 3 phrases, longueurs variées, avec au moins une phrase très courte ;
   - les liens des sources à la fin s'il y a une recherche ;
   - une fin qui invite au commentaire, sans formule théâtrale.
   Seulement ce que tu dis ou ce que la recherche source. Ne jamais inventer un fait ni un nom.
3. **Relire contre `STYLE.md`** (ton, interdits, formules proscrites), phrase par phrase, puis
   contre le transcript : une option reste une option (« parfois »), un « je pense » n'est pas une
   certitude. Corriger, relire une seconde fois. Il n'y a pas de contrôle automatique : la
   relecture EST le contrôle, alors la faire vraiment, en re-lisant chaque affirmation.
4. Tu relis, puis `outils/video valide <STEM> caption`. Ensuite l'export :
   `outils/video export <STEM> <nom-court>`.
