# Protection des données : à quelles conditions signaler un passager

## Un nouvel usage, qui demande des garanties

L'enquête a été collectée pour **mesurer** la satisfaction. L'utiliser pour **signaler des passagers aux équipes au sol** est un usage différent, et il touche des personnes qui n'ont jamais répondu à l'enquête. Il faut donc distinguer deux temps :

- **Entraînement du modèle.** Les réponses à l'enquête servent uniquement à construire l'arbre de décision. Elles sont pseudonymisées (aucun nom, l'identifiant est retiré) et ne quittent pas l'équipe data.
- **Utilisation à l'atterrissage.** Le modèle ne lit **aucune réponse d'enquête**. Il utilise seulement des informations que la compagnie possède déjà pour organiser le vol : réservation, statut de fidélité, retards.

Nous recommandons ce dispositif seulement si les conditions suivantes sont réunies (à valider avec le délégué à la protection des données) :

1. **Base légale : l'intérêt légitime** de la compagnie à améliorer le service, avec une mise en balance écrite montrant que l'approche n'a pas d'effet négatif sur le passager.
2. **Analyse d'impact (AIPD) avant tout déploiement.** Il s'agit d'un profilage appliqué à un grand nombre de personnes.
3. **Information des passagers.** Une mention claire dans les conditions de réservation et dans l'application : « nous pouvons vous proposer un accueil personnalisé à l'arrivée ». Les passagers ont aussi un **droit d'opposition** simple (une case dans le compte client).
4. **Aucune conséquence négative.** Un signalement donne droit à une attention en plus, jamais à un refus de service, un tarif différent ou une note dans le dossier client. Le passager peut refuser l'échange sans justification.
5. **Durée de conservation courte.** La liste des passagers signalés est supprimée à la fin du service de la journée. On garde seulement des chiffres agrégés (nombre d'approches, taux de retour), pour mesurer l'efficacité du dispositif.
6. **Un humain décide.** Le modèle propose une liste, l'agent choisit d'aborder ou non. Aucune décision n'est prise automatiquement.

## Chaque information utilisée est-elle acceptable ?

| Information | Utilisée ? | Acceptable pour cet usage ? |
|---|---|---|
| Classe (Eco, Eco Plus, Business) | Oui | Oui : donnée de réservation, nécessaire au transport. |
| Statut de fidélité | Oui | Oui : connu via le programme de fidélité, dont le passager est membre volontairement. |
| Motif du voyage (pro / perso) | Oui | **À condition** qu'il soit connu de façon fiable : réservation via un compte entreprise ou déclaration du passager. S'il est seulement deviné, c'est une donnée déduite qu'il faudrait mentionner dans l'information aux passagers. Sans cette variable, le gain baisse de 751 € pour 1 000 passagers, mais le modèle reste utilisable. |
| Distance du vol | Oui | Oui : donnée du vol, pas de la personne. |
| Retards au départ et à l'arrivée | Oui | Oui : données opérationnelles du vol, connues à l'atterrissage. |
| Notes de l'enquête (14 services) | **Non** | Non : elles n'existent pas à l'atterrissage, et les utiliser détournerait les réponses de leur finalité. |
| Genre | **Non** | Non : aucune justification à cibler un passager selon son genre. |
| Âge | **Non** | Non : il n'apporte presque rien (+2 € pour 1 000 passagers) et exposerait directement les enfants. |

## Les enfants

L'âge n'est pas dans le modèle, mais **les mineurs représentent 18 % des passagers signalés, contre 7,6 % de l'ensemble des passagers**. Ce n'est pas un ciblage volontaire : 72 % des mineurs voyagent pour raisons personnelles, souvent en famille, et c'est le motif du voyage qui les fait ressortir.

Nous recommandons de **ne pas les retirer de la liste**. Ils sont aussi souvent vraiment mécontents que les adultes (95,3 % contre 95,7 % parmi les passagers signalés), et les exclure ferait perdre environ 100 € pour 1 000 passagers. En revanche, trois règles s'imposent :

- l'équipe s'adresse **toujours à l'adulte qui accompagne l'enfant**, jamais à l'enfant seul ;
- un **mineur non accompagné n'est jamais abordé** dans ce cadre : il reste sous la responsabilité du personnel dédié ;
- l'âge n'apparaît **nulle part** dans ce que voient les équipes.

## Ce que voient les équipes au sol

Pour chaque passager signalé, l'agent voit seulement :

- le **nom** du passager, le **numéro de vol** et la **porte d'arrivée** ;
- la mention **« accueil prioritaire »**.

L'agent ne voit **pas** le score de risque, ni la raison du signalement (classe, motif, retard), ni l'âge, ni une mention du type « passager probablement mécontent ». Ainsi, le passager n'est pas étiqueté. L'agent ouvre une conversation (« comment s'est passé votre voyage ? ») au lieu de partir d'un jugement, et l'information ne peut pas circuler hors de son usage.

## Points de vigilance

- **Le modèle a été construit sur des répondants à l'enquête**, mais il sera appliqué à tous les passagers. Le pilote sur quelques vols doit vérifier que la précision tient, et que certains groupes ne sont pas abordés de façon disproportionnée.
- **Suivi dans le temps.** Chaque trimestre, il faudra vérifier la répartition des passagers signalés (par classe, par tranche d'âge en données agrégées) et réentraîner le modèle si le comportement des passagers change.
