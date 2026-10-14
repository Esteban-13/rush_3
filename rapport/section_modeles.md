# Modèles : repérer les passagers à aborder à l'atterrissage

## Ce que le modèle a le droit d'utiliser

Le modèle sert au moment où l'avion se pose. À cet instant, la compagnie ne dispose pas des réponses à l'enquête, et la plupart des passagers n'y répondront jamais. Il ne peut donc s'appuyer que sur six informations déjà connues : le statut de fidélité, le motif du voyage (professionnel ou personnel), la classe, la distance du vol, le retard au départ et le retard à l'arrivée.

Les quatorze notes de l'enquête sont exclues : elles n'existent pas encore à l'arrivée. Le genre est exclu parce que rien ne justifie de s'en servir pour cibler un passager. L'âge a été testé à part : il n'apporte presque rien (+2 € pour 1 000 passagers), et son usage poserait problème pour les enfants (voir la section Protection des données).

## Comment on a comparé les méthodes sans toucher au test

Le fichier test représente les passagers du mois prochain et ne sert qu'une fois, à la toute fin. Pour choisir entre les méthodes, on a utilisé une **validation croisée** sur le train : il est découpé en cinq parts, on entraîne sur quatre et on évalue sur la cinquième, cinq fois de suite. Chaque passager sert ainsi une fois d'« examen » sans que le test soit ouvert. La graine aléatoire est fixée : deux exécutions donnent exactement les mêmes chiffres.

## Le critère : des euros, pas un score

Les équipes ne peuvent aborder qu'un passager sur dix. Ce qui compte, c'est donc la qualité des 10 % de passagers désignés comme les plus à risque, et ce qu'ils rapportent. D'après les estimations de la direction :

- aborder un passager vraiment mécontent rapporte en moyenne 100 € (1/3 × 600 € × 1/2), moins 40 € d'approche, soit **+60 €** ;
- aborder un passager en réalité satisfait coûte **−40 €**.

Gain = passagers abordés × (précision × 100 € − 40 €). Une approche est rentable dès que plus de 40 % des passagers abordés sont vraiment mécontents. On indique aussi l'AUC, qui mesure la qualité du classement de l'ensemble des passagers. Tous les chiffres de cette section sont des moyennes sur les cinq découpages de la validation croisée.

## Les méthodes comparées

1. **Règle simple, sans modèle.** Parmi plusieurs règles de bon sens (classe Eco, client non fidèle, plus gros retards), la meilleure consiste à **aborder les passagers en voyage personnel**. Ils sont mécontents à 90 %. C'est le score à battre.
2. **Régression logistique.** Chaque information ajoute ou retire du risque, et on fait la somme.
3. **Arbre de décision** (quatre questions au maximum). Une suite de questions oui/non, qui se dessine sur une page.
4. **Gradient boosting**, en contrôle : un modèle plus puissant mais impossible à expliquer, sur les mêmes six informations.

| Méthode (validation croisée, train) | AUC | Bons choix parmi les 10 % abordés | Gain pour 1 000 passagers | Gain en plus vs règle simple |
|---|---|---|---|---|
| Règle « voyage personnel » | 0,71 | 89,8 % | 4 983 € | — |
| Régression logistique | 0,846 | 95,3 % | 5 525 € | +542 € |
| **Arbre de décision** | **0,848** | **95,7 %** | **5 575 €** | **+591 €** |
| Gradient boosting (contrôle) | 0,850 | 95,7 % | 5 568 € | +584 € |
| Règle des 3 questions (résumé de l'arbre) | — | 94,9 % | 5 492 € | +509 € |
| Modèle parfait (borne théorique) | — | 100 % | 6 000 € | +1 017 € |

Les trois modèles battent nettement la règle simple, d'environ 550 à 600 € pour 1 000 passagers. Entre eux, l'écart est faible, du même ordre que la variation d'un découpage à l'autre (environ 25 à 30 €). En particulier, le gradient boosting ne fait pas mieux que l'arbre : **on ne perd rien à choisir un modèle explicable**.

## Le modèle retenu : l'arbre de décision

À rentabilité égale, l'arbre est le plus facile à expliquer. On peut le montrer au comité exécutif et dire pourquoi un passager est signalé. Il pose d'abord la question de la classe (Business ou non), puis celles du motif du voyage, de la fidélité et du retard à l'arrivée (plus ou moins 5 minutes). Par exemple, un client fidèle en Business, en voyage professionnel et arrivé à l'heure n'est mécontent que dans environ 18 % des cas.

Pour la direction, l'arbre se résume en **trois questions** : le passager n'est pas en Business, il voyage pour raisons personnelles, et il est arrivé avec plus de 5 minutes de retard. Ce groupe représente 9,8 % des passagers, soit presque exactement la capacité des équipes. Il est mécontent à 96 %, et cette règle retrouve 98,5 % du gain de l'arbre (5 492 € contre 5 575 €).

Ce choix a été figé avant l'ouverture du test.

## Ce que coûtent ses erreurs

Pour 1 000 passagers à l'arrivée, on en aborde 100 :

- environ **96 sont vraiment mécontents** : 96 × 60 € = +5 760 € ;
- environ **4 sont en fait satisfaits** : 4 × −40 € = −160 €. C'est une erreur peu grave : un passager content reçoit une attention de plus.

Environ 470 passagers mécontents ne seront pas abordés. Ce n'est pas une erreur du modèle : c'est la limite de capacité des équipes. Le modèle sert à bien choisir les 100 que l'on peut voir. Si les équipes pouvaient aborder plus de monde, le gain continuerait d'augmenter : environ 8 100 € à 15 % de capacité et 10 400 € à 20 %.

**En pratique, que font les équipes ?** L'arbre donne le même niveau de risque à tous les passagers d'une case, et la limite des 10 % tombe au milieu de l'une d'elles. Nous recommandons que **le système tire au sort** les passagers à prendre dans cette dernière case : les équipes reçoivent directement une liste qui fait exactement 10 % des arrivées. S'arrêter à la dernière case entière laisserait environ un dixième de la capacité inutilisé et ferait perdre près de 590 € pour 1 000 passagers (4 986 € au lieu de 5 575 €).

## Contrôles complémentaires

- **Mineurs.** L'âge n'est pas dans le modèle, mais les mineurs représentent 18 % des passagers signalés, contre 7,6 % de l'ensemble des passagers. Nous recommandons de **les garder** dans la liste. Les mineurs signalés sont aussi souvent vraiment mécontents que les adultes (95,4 % contre 95,8 %), et les retirer ferait perdre 87 € pour 1 000 passagers (5 487 € au lieu de 5 575 €). Surtout, 72 % d'entre eux voyagent pour raisons personnelles, le plus souvent en famille : recueillir l'avis d'un enfant mécontent, c'est s'adresser à une famille qui décidera ensemble de revoler ou non avec la compagnie. Nos données ne disent pas qui voyage avec qui, donc ce gain ne peut pas être mesuré, seulement estimé. Si une approche sauve 2 billets au lieu d'un, le gain passe à environ 7 300 € pour 1 000 passagers, et à environ 9 000 € pour 3 billets (contre 5 575 € avec l'hypothèse de base). Condition indispensable : l'équipe s'adresse **toujours à l'adulte qui accompagne l'enfant**, jamais à l'enfant seul (voir la section Protection des données).
- **Âge.** Ajouter l'âge au modèle ne rapporte que 2 € de plus pour 1 000 passagers : il reste exclu.
- **Motif du voyage.** C'est l'information la plus utile au modèle. Sans elle, le gain tombe à 4 824 € pour 1 000 passagers (−751 €). Il reste toutefois au-dessus de la règle « classe Eco / Eco Plus » (4 056 €), la meilleure règle simple qui n'utilise pas le motif. Avant tout déploiement, il faut vérifier que la compagnie connaît ce motif de façon fiable à l'atterrissage (réservation via une entreprise, programme de fidélité).

## Résultat final sur le test (lu une seule fois)

| Méthode (test, 25 976 passagers) | AUC | Bons choix parmi les 10 % abordés | Gain pour 1 000 passagers |
|---|---|---|---|
| Règle « voyage personnel » | 0,710 | 90,0 % | 5 001 € |
| **Arbre de décision** | **0,845** | **96,1 %** | **5 607 €** |
| Modèle parfait (borne théorique) | — | 100 % | 6 000 € |

Sur ces passagers que le modèle n'avait jamais vus, le résultat est très proche de la validation croisée : 96,1 % de bons choix contre 95,7 %, et 5 607 € contre 5 575 € pour 1 000 passagers. L'arbre rapporte 606 € de plus que la règle simple pour 1 000 passagers. Sur l'ensemble du test, les équipes auraient abordé 2 598 passagers : 2 495 étaient vraiment mécontents et 102 satisfaits, pour un gain total d'environ 145 600 €. La méthode de choix, sans jamais toucher au test, était donc fiable.

## Limite à garder en tête

Le modèle a été entraîné et testé sur des passagers **qui ont répondu à l'enquête**, mais il sera appliqué à **tous** les passagers. Si ceux qui ne répondent pas sont différents, par exemple moins mécontents, la précision réelle sera plus faible que celle annoncée. Nous recommandons un **pilote sur quelques vols**, en comparant des passagers abordés et non abordés, avant de généraliser.
