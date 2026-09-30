# Mise à jour des analyses

Passages : 13h23 (midi) et 19h23 (soir), jours de bourse, heure de Paris. Screener : le 1er du mois à 9h47.

1. `git pull` à la racine du dépôt (le cloner s'il manque).
2. Soir seulement, après « Cours du soir » : `python3 outils/maj_flux.py` (cours, histo, technique, matières, ETF).
3. Veille d'actualité par valeur depuis le dernier fait enregistré (sources primaires d'abord, chiffres confirmés par deux sources, rien d'inventé). Mettre à jour faits, analyse.actu, pub, societe.suivi. Midi : geo.json. Chaque passage : snapshot.json (asOf, majLe, macro le soir, semaineTexte, attention).
4. `python3 outils/export_app.py data/analyses`, puis commit signé « 3A Wealth » (`Analyses du <date> <midi|soir>`) et `git push`.
5. Alerte seulement si : statut « cassee », OPA, mouvement de plus de 10 % sur la séance, entrée en zone d'intérêt, suivi qui passe à « ko », point chaud qui passe à « eleve ».
6. Programmer le passage suivant.

Screener : 4 à 6 idées hors watchlist (au moins 2 hors d'Europe, 2 liées aux matières ou à la géopolitique) dans data/analyses/propositions/<TICKER>.json, jamais dans valeurs/.
