# Exploration des données

## Les données et leur nettoyage

L'enquête compte **103 904 passagers**, sans aucun doublon. **43,3 % se disent satisfaits** et 56,7 % neutres ou insatisfaits. Chaque passager donne une note de 1 à 5 à 14 services ; un 0 signifie « pas de réponse » ou « service non utilisé ».

- **Les 0 sont traités comme des valeurs manquantes**, pas comme de très mauvaises notes. 7,9 % des passagers en ont au moins un, surtout pour les horaires (5,1 %), la réservation en ligne (4,3 %) et le wifi (3,0 %). Ce 0 n'est pas neutre : les passagers sans note de wifi sont satisfaits à 99,7 %. Il s'agit probablement d'un groupe particulier qui n'a pas utilisé le service. Dans les modèles, la note manquante est remplacée par une note neutre (3), et un indicateur « non répondu » est ajouté pour garder cette information.
- **310 retards à l'arrivée manquent.** Ils sont estimés à partir du retard au départ, qui lui est presque identique (corrélation de 0,965).
- **Les âges vont de 7 à 85 ans.** 7 931 répondants sont mineurs (7,6 %), ce qui compte pour la protection des données.

## Qui est satisfait ? Le profil du voyage pèse lourd

*(Figures 1 et 2)*

| Profil | Part des passagers | Satisfaits |
|---|---|---|
| Classe Business | 47,8 % | 69,4 % |
| Classe Eco | 45,0 % | 18,6 % |
| Voyage professionnel | 69,0 % | 58,3 % |
| Voyage personnel | 31,0 % | **10,2 %** |
| Client fidèle | 81,7 % | 47,7 % |
| Client non fidèle | 18,3 % | 23,7 % |

En croisant la classe et le motif du voyage, l'écart devient spectaculaire : **72 % de satisfaits en Business pour un voyage professionnel, contre 10 % en Eco pour un voyage personnel.** Ces deux groupes représentent à eux seuls 71 % des passagers.

Plusieurs écarts apparents viennent en fait de ce profil. C'est un **effet de composition** :

- **Distance.** Les vols de plus de 3 000 km ont 77 % de satisfaits, contre 33 % sous 500 km. Mais 99 % des passagers des vols longs sont en Business. À profil égal, la distance ne change presque rien : en Eco pour un voyage personnel, le taux reste autour de 10 % quelle que soit la distance.
- **Âge.** Les moins de 18 ans et les plus de 65 ans sont nettement moins satisfaits (16 % et 18 %), mais ils voyagent surtout en Eco et pour raisons personnelles. Dans ce groupe, le taux est d'environ 10 % à tous les âges.
- **Genre.** Aucune différence (42,7 % contre 43,9 %).

## Les retards : un effet réel, mais modéré

56 % des vols arrivent à l'heure. Quand il y a un retard, il est en général de 17 minutes (médiane). La satisfaction passe de **47 % pour un vol à l'heure à environ 35 % au-delà de 15 minutes**. À profil de passager égal, un retard de plus de 15 minutes fait perdre environ **7 points de satisfaction**. L'effet est plus fort pour les passagers déjà fragiles : en Eco pour un voyage personnel, le taux passe de 13 % à l'heure à 4 % avec 16 à 60 minutes de retard.

# Les facteurs de satisfaction

## Méthode

Les 14 notes de service ont été analysées de trois façons complémentaires, toutes sur le fichier d'entraînement :
1. le **lien simple** entre chaque note et la satisfaction (corrélation de Spearman) ;
2. une **régression logistique**, qui mesure l'effet de chaque note à notes égales sur les autres services ;
3. l'**importance par permutation** d'un gradient boosting, qui mesure ce que le modèle perd quand on brouille une note.

On a ensuite refait la régression **en contrôlant le profil** (classe, motif, fidélité, âge, distance, retards), pour séparer l'effet des services de celui du profil. Les notes seules prédisent très bien la satisfaction (AUC de 0,92 en régression, 0,99 en gradient boosting) : elles en sont presque une traduction directe.

## Résultats

*(Figures 3, 4 et 5)*

**1. L'embarquement en ligne est le facteur le plus constant.** Il arrive en tête du lien simple (0,59) et de la régression. Chaque point de note en plus multiplie par 2,8 les chances d'être satisfait, et son poids tient après contrôle du profil. L'effet est un **effet de seuil** : avec une note de 1, 2 ou 3, environ 13 % des passagers sont satisfaits ; avec 4, 62 % ; avec 5, 87 %. Passer de « moyen » à « bon » compte plus que corriger l'excellent.

**2. Le wifi à bord est décisif pour les passagers les plus mécontents.** C'est le service le plus mal noté (2,8 / 5 en moyenne, 43 % de notes 1 ou 2), et le plus important pour le gradient boosting. Chez les passagers en Eco ou en voyage personnel, il est presque le **seul** service qui compte : son poids est au moins dix fois supérieur à celui de n'importe quel autre service. Avec une note de 5, 99 % des passagers sont satisfaits.

**3. Le confort à bord vient ensuite**, avec un effet plus modeste : espace pour les jambes (×1,47 par point), service à bord (×1,42), divertissement (×1,40), enregistrement (×1,30). Le poids du divertissement chute après contrôle du profil : son effet vient en partie de la classe Business, mieux équipée.

**4. Deux résultats trompeurs, à ne pas prendre pour des leviers :**
- **Horaires pratiques.** Le signe est négatif dans la régression (×0,52 par point), mais seul, son lien avec la satisfaction est presque nul. Le signe s'inverse dès qu'on ajoute le wifi et la réservation en ligne, auxquels il est lié. C'est un **effet de suppression** statistique, pas un vrai effet négatif des bons horaires.
- **Emplacement de la porte.** Aucun lien simple avec la satisfaction (0,00), mais une importance élevée dans le gradient boosting, qui l'utilise en combinaison avec d'autres notes. Il n'est pas interprétable comme un levier.

**L'expérience globale compte.** Les passagers qui notent 4 ou 5 au plus deux services sont satisfaits à 7 % ; ceux qui en notent 4 ou 5 au moins douze le sont à 91 %.

## Associé, actionnable, causal : la distinction pour chaque facteur

| Facteur | Lié à la satisfaction ? | La compagnie peut agir ? | Cause probable ? |
|---|---|---|---|
| **Embarquement en ligne** | Oui, le plus fort | **Oui** (application, parcours numérique) | Plausible, à confirmer par un test |
| **Wifi à bord** | Oui, décisif en Eco et en voyage personnel | **Oui** (équipement, offre) | Plausible, à confirmer par un test |
| Espace pour les jambes, service à bord, enregistrement | Oui, modéré | Oui | Plausible, effet plus faible |
| Divertissement à bord | Oui, mais surtout via la classe Business | Oui | Incertain |
| Retards | Oui, environ −7 points au-delà de 15 min | En partie (opérations) | **Oui** : le retard précède la réponse à l'enquête |
| Classe, motif du voyage, fidélité | Oui, très fort | **Non** : c'est le profil du client | Non : décrit qui voyage |
| Distance, âge | Apparent | Non | **Non** : effet de composition |
| Horaires pratiques, emplacement de la porte | Trompeur | — | **Non** : artefact statistique |

**Pourquoi « plausible » et pas « certain ».** Les notes et la satisfaction sont données **au même moment**, dans la même enquête. Un passager content a tendance à bien noter tous les services : c'est l'**effet de halo**. Les liens mesurés surestiment donc probablement l'effet réel de chaque service. Seul un test (améliorer l'embarquement en ligne ou le wifi sur quelques lignes, et comparer avec des lignes témoins) permettrait d'en mesurer l'effet véritable avant un investissement à grande échelle. Enfin, ces résultats portent sur les passagers qui ont répondu à l'enquête, pas forcément sur tous les passagers.
