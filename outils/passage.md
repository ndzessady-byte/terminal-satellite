# Passage automatique 3A Wealth (midi ou soir)

Ce fichier est la consigne complète d'un passage. Les passages sont programmés à l'avance pour deux semaines (13h23 et 19h23, heure de Paris, jours de bourse) : un passage raté n'empêche donc pas les suivants.

0. Réserve : compte les passages encore programmés (list_triggers, noms « 3A Wealth passage »). S'il en reste moins de 10, programme avec send_later les suivants jusqu'à 14 jours de bourse devant, avec le message court habituel (« Passage 3A Wealth <midi|soir> : suis outils/passage.md »). Jamais deux passages au même horaire.
1. Si c'est un jour férié de la Bourse de Paris, arrête-toi là.
2. Dans /home/claude/terminal-satellite (le recloner si absent) : git pull. Suis outils/procedure_maj.md et les règles détaillées du prompt de l'ancienne tâche trig_01Qzw1dmriNeg5GEg8cWVtvr (list_triggers pour la relire).
3. Midi = veille actu + géopolitique (geo.json) + snapshot. Soir = vérifier que « Cours du soir » a tourné (sinon workflow_dispatch prix.yml via l'API GitHub, en-tête Content-Type: application/json), python3 outils/maj_flux.py, veille actu, snapshot avec macro.
4. Recherche : sous-agents avec la consigne du scratchpad (consigne.txt, date à mettre à jour), 2 groupes de valeurs + 1 macro/géo, budgets serrés. Si les sous-agents échouent (limite d'utilisation), veille réduite soi-même, et publier quand même.
5. Fusion par script (merge.py), export_app, commit « Analyses du <date> <midi|soir> » signé 3A Wealth sans mention de Claude ni Co-Authored-By, push, vérifier git log -1.
6. Alerte à Dylan via SendUserMessage seulement selon les critères (cassée, OPA, ±10 % séance, entrée en zone d'intérêt, suivi ko, point chaud passant à élevé).
7. Rattrapage : si le dernier commit « Analyses du » date de plus de 30 heures de bourse, couvrir toute la période manquée.
