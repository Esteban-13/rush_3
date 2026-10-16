# Rush 3 – Satisfaction des passagers

Analyse de la satisfaction des passagers d'une compagnie aérienne européenne pour la direction Expérience Client :

1. **comprendre ce qui fait la satisfaction**, pour savoir où investir ;
2. **repérer à l'atterrissage les passagers probablement insatisfaits**, pour que les équipes au sol les accueillent en priorité (10 % des passagers au maximum).

## Livrables

| Livrable | Où le trouver |
| --- | --- |
| Rapport (PDF, 8 pages + annexes) | [`rapport/rapport_rush3.pdf`](rapport/rapport_rush3.pdf) |
| Présentation orale (10 minutes) | [`presentation/presentation_rush3.html`](presentation/presentation_rush3.html), à ouvrir dans un navigateur · [version en ligne](https://claude.ai/artifact/4bT34gsv6cGrxAqB9tXWj1) |
| Code | notebooks et scripts de ce dépôt (voir « Relancer le projet ») |

## Équipe et responsabilités

| Membre | Partie | Fichiers |
| --- | --- | --- |
| Esteban | **A – Données, exploration et facteurs de satisfaction** : création du dépôt, `config.py`, nettoyage, exploration, analyse des 14 notes de service, effet des retards | `config.py`, `notebook_partA_exploration_facteurs.ipynb`, `figures/fig1` à `fig5`, `results_partA.json`, `data/clean/` |
| Ihman | **B – Modèles de prédiction** : règles simples, régression logistique, arbre de décision (retenu), validation croisée, contrôles (mineurs, âge, motif du voyage, capacité), évaluation finale sur le test, section Modèles du rapport | `modele_utils.py`, `notebooks/04_modeles.ipynb`, `notebooks/05_evaluation_finale.ipynb`, `figures/04_*`, `resultats/04_*`, `rapport/section_modeles.md` |
| Maïlys Augier | **C – Économie, protection des données et restitution** : calcul du gain en euros et analyse de sensibilité, protection des données (RGPD), synthèse pour la direction, recommandations, assemblage du rapport, support de présentation, README | `notebooks/04b_cout_metier.ipynb`, `figures/04b_*`, `resultats/04b_*`, `README.md`, rapport et slides |

## Structure

```
rush_3/
├── README.md
├── requirements.txt
├── config.py                  # graine, chemins, variables du modèle, hypothèses économiques
├── modele_utils.py            # chargement, règles simples, modèles, calcul du gain (partagé par 04, 04b, 05)
├── notebook_partA_exploration_facteurs.ipynb
├── data/
│   ├── raw/                   # train.csv, test.csv (fournis)
│   └── clean/                 # train nettoyé par la partie A
├── notebooks/
│   ├── 04_modeles.ipynb           # train uniquement, validation croisée 5 plis
│   ├── 04b_cout_metier.ipynb      # train uniquement, lit resultats/04_comparaison_cv.csv
│   └── 05_evaluation_finale.ipynb # SEUL notebook qui lit test.csv, exécuté une seule fois
├── figures/
├── resultats/
├── rapport/                   # sections du rapport + rapport_rush3.pdf
└── presentation/              # presentation_rush3.html (slides de l'oral)
```

## Relancer le projet

```bash
pip install -r requirements.txt
```

Exécuter les notebooks **depuis la racine du dépôt**, dans cet ordre :

1. `notebook_partA_exploration_facteurs.ipynb` — exploration et facteurs
2. `notebooks/04_modeles.ipynb` — comparaison des méthodes en validation croisée
3. `notebooks/04b_cout_metier.ipynb` — gains en euros et sensibilité (a besoin des résultats du 04)
4. `notebooks/05_evaluation_finale.ipynb` — **une seule fois**, après validation du modèle par toute l'équipe

Toutes les opérations aléatoires utilisent `SEED = 42` : deux exécutions donnent exactement les mêmes chiffres et figures que le rapport.

## Règles de méthode

- **Jeu de test utilisé une seule fois.** `test.csv` n'est lu que dans `05_evaluation_finale.ipynb`. Tous les choix (variables, modèle, réglages) sont faits en validation croisée sur `train.csv`.
- **Uniquement les informations connues à l'atterrissage.** Le modèle utilise 6 variables : type de client, motif du voyage, classe, distance, retard au départ, retard à l'arrivée. Les 14 notes de l'enquête (remplies après le vol) et le genre sont exclus ; l'âge est seulement testé en variante.
- **Choix du modèle selon le gain en euros** sur les 10 % de passagers les plus à risque, et selon son explicabilité, pas seulement selon un score statistique.

## Procédure du test (une seule lecture)

1. Les notebooks A, 04 et 04b sont relancés et leurs chiffres validés par les trois membres.
2. Le choix du modèle est figé dans un commit dédié : « Gel du modèle avant ouverture du test ».
3. `05_evaluation_finale.ipynb` est exécuté une seule fois, puis commité seul avec `resultats/05_resultats_test.csv`.
4. Aucun choix (variables, modèle, réglages) n'est modifié après cette lecture. L'historique Git permet de le vérifier.

## Résultats principaux (validation croisée)

| Méthode | Précision sur les 10 % signalés | Gain pour 1 000 passagers |
| --- | --- | --- |
| Arbre de décision (retenu) | 95,7 % | 5 575 € |
| Gradient boosting (comparaison « boîte noire ») | 95,7 % | 5 568 € |
| Régression logistique | 95,3 % | 5 525 € |
| Règle 3 questions (hors Business, voyage perso, retard > 5 min) | 94,9 % | 5 492 € |
| Règle « voyage personnel » | 89,8 % | 4 983 € |
| Au hasard | 56,7 % | 1 667 € |

Le gradient boosting ne fait pas mieux que l'arbre : on ne perd rien à choisir un modèle explicable. La règle de 3 questions résume l'arbre et obtient 98,5 % de son gain.

**Résultat sur le jeu de test** (lu une seule fois) : 96,1 % de bons choix et **5 607 €** pour 1 000 passagers, soit +606 € par rapport à la règle « voyage personnel ». Détail : `resultats/05_resultats_test.csv`.
