# Ce que rapporte le dispositif, et nos recommandations

## La valeur d'une approche

D'après les estimations de la direction, un passager neutre ou insatisfait sur trois ne revient pas, ce qui représente 600 € de revenus futurs perdus, et une approche ramène la moitié de ceux qui seraient partis. Aborder un passager vraiment mécontent évite donc en moyenne une perte de **1/3 × 1/2 × 600 € = 100 €**, pour un coût de 40 €.

- Aborder un vrai mécontent rapporte **+60 €**.
- Aborder un passager en réalité satisfait coûte **−40 €**.
- L'approche est rentable dès que **plus de 40 %** des passagers abordés sont vraiment mécontents.

## Toutes les méthodes, en euros

Pour 1 000 passagers à l'arrivée, les équipes en abordent 100 (capacité de 10 %). Chiffres en validation croisée sur le fichier d'entraînement, puis sur le test (lu une seule fois) pour le modèle retenu :

| Méthode | Bons choix parmi les 100 abordés | Gain pour 1 000 passagers |
|---|---|---|
| Modèle parfait (limite théorique) | 100 | 6 000 € |
| **Arbre de décision, sur le test** | **96** | **5 607 €** |
| Arbre de décision (validation croisée) | 96 | 5 575 € |
| Règle « voyage personnel » | 90 | 4 983 € |
| Règle « classe Eco / Eco Plus » | 81 | 4 056 € |
| Règle « client non fidèle » | 76 | 3 632 € |
| Règle « plus gros retard » | 64 | 2 421 € |
| Au hasard | 57 | 1 667 € |

Le modèle retenu rapporte **3,3 fois plus qu'un ciblage au hasard**, **+591 € (+12 %)** par rapport à la meilleure règle simple, et atteint **93 % du gain maximal possible**. Sur le test, il confirme ce résultat : 5 607 €, soit +606 € par rapport à la règle simple.

**Ce qu'il faut retenir sur la capacité.** Le gain continue d'augmenter au-delà de 10 % : environ 8 100 € à 15 % et 10 400 € à 20 %. C'est la taille des équipes qui limite le dispositif, pas sa rentabilité.

**Appliquer la limite des 10 % sur le terrain.** L'arbre classe les passagers en groupes. La limite des 10 % tombe au milieu du dernier groupe retenu : les équipes complètent alors par **tirage au sort dans ce groupe**. S'arrêter au dernier groupe complet ferait tomber le gain à 4 986 €.

## Que se passe-t-il si les estimations de la direction sont fausses ?

« Un sur trois ne revient pas » et « une approche en récupère la moitié » sont des estimations, pas des mesures. Nous avons recalculé le gain pour 1 000 passagers dans quatre scénarios :

| Scénario (part qui ne revient pas, part récupérée) | Précision minimale pour être rentable | Modèle retenu | Règle « voyage personnel » | Au hasard |
|---|---|---|---|---|
| Optimiste (1/2, 1/2) | 27 % | 10 362 € | 9 475 € | 4 500 € |
| **Hypothèses de la direction (1/3, 1/2)** | 40 % | **5 575 €** | 4 983 € | 1 667 € |
| Récupération faible (1/3, 1/4) | 80 % | 787 € | 492 € | −1 167 € |
| Pessimiste (1/5, 1/4) | 133 % | −1 128 € | −1 305 € | −2 300 € |

- **Le dispositif reste rentable tant que (part qui ne revient pas) × (part récupérée) dépasse 7 %.** L'estimation de la direction est de 16,7 %, la marge est donc confortable.
- Plus les hypothèses sont pessimistes, plus un ciblage précis compte : avec une récupération faible, le ciblage au hasard fait perdre de l'argent, alors que le modèle reste rentable.
- Dans le scénario pessimiste, **aucune méthode n'est rentable, même un modèle parfait** : il faut une approche au moins 133 % précise, ce qui est impossible. C'est la raison principale de notre recommandation de pilote.

## Recommandations

**1. Investir d'abord dans l'embarquement en ligne et le wifi.** Ce sont les deux services les plus liés à la satisfaction sur lesquels la compagnie peut agir. Le wifi est le levier décisif pour les passagers en Eco et en voyage personnel, les plus mécontents. Comme ces liens peuvent être gonflés par l'effet de halo, chaque amélioration doit d'abord être testée sur quelques lignes, comparées à des lignes témoins.

**2. Lancer un pilote d'accueil prioritaire avant de généraliser.** Sur quelques vols, pendant environ trois mois :
- les passagers signalés par le modèle sont répartis au hasard en deux groupes : un groupe abordé et un groupe témoin non abordé ;
- on compare le taux de retour des deux groupes dans les mois suivants.

Ce pilote mesure les deux chiffres dont dépend toute la rentabilité, et vérifie que le modèle, construit sur les répondants à l'enquête, garde sa précision sur l'ensemble des passagers.

**3. Généraliser si le pilote confirme le gain**, avec la règle de trois questions comme outil pour les équipes : *pas en Business, voyage personnel, plus de 5 minutes de retard*. Le déploiement doit respecter les conditions de protection des données : analyse d'impact, information des passagers, aucun score montré aux équipes, et toujours passer par l'adulte pour les enfants.

**4. Revoir la capacité des équipes.** Le gain augmente jusqu'à 20 % de passagers abordés et au-delà. Si le pilote est concluant, élargir la capacité est l'investissement le plus rentable.

**5. Fiabiliser la connaissance du motif du voyage.** C'est l'information la plus utile au modèle : sans elle, le gain baisse de 751 € pour 1 000 passagers. Il faut s'assurer qu'elle est connue de façon fiable à l'atterrissage (réservation via un compte entreprise, déclaration du passager).
