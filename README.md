# Terminal Satellite, flux de cours

Chaque soir de bourse, GitHub Actions lance `prix.py` : il télécharge un an de cours pour les valeurs de `tickers.json`, calcule moyennes 50 et 200 jours, RSI 14, plus haut et plus bas sur 52 semaines, performances, et enregistre `data/prices.json`. Le Terminal Satellite lit ce fichier à sa mise à jour du soir.

Pour ajouter une valeur : ajoute une ligne `"TICKER": "SYMBOLE.YAHOO"` dans `tickers.json` (ex. `"SOI": "SOI.PA"`).

## Matières premières

`matieres.json` liste les matières premières et changes suivis (or, argent, Brent, gaz TTF, cuivre, aluminium, blé, euro/dollar). Leurs séries sont écrites dans `data/prices.json` sous la clé `matieres`, avec les mêmes indicateurs que les actions (plus `perf1s`, la variation sur une semaine).
