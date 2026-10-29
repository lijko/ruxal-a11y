<!--
SPDX-FileCopyrightText: 2026 Bertrand Kempf
SPDX-License-Identifier: CC-BY-4.0
-->
# Projet A11Y : modules Audit et Scénario

**Statut : spécification, à relire avant développement (29 octobre 2026), choix du questionnaire intégrés.** Cible : RUXAWEB 2.x. Rien de ce qui est décrit ici n'est encore construit, sauf mention contraire.

## Principe
Le fichier de travail devient un **projet** : « Projet A11Y - nom du projet ». Un projet contient un ou plusieurs onglets, chacun relevant d'un **module** :

- **Audit** : un échantillon d'écrans représentatifs ;
- **Scénario** : un enchaînement d'écrans (souscription, achat, prise de rendez-vous).

Dans les deux modules, le testeur travaille sur trois volets qui aboutissent tous à la grille des critères :

1. **Import axe ou Lighthouse** : des pistes à reprendre ou écarter, jamais des statuts ;
2. **Observations** : saisies, collées ou converties par une IA, rattachées aux critères par un point de contrôle ;
3. **Grille des critères** : lecture de tous les statuts, et pose directe de C ou NA (NC demande une phrase).

L'import et les observations restent dans la vue **Saisie** : une piste n'a de sens qu'à côté du formulaire qui la reprend. La grille reste une vue à part.

## 1. En-tête du projet
- Le champ « Nom de l'audit » devient **« Nom du projet »**. Le titre affiché est « Projet A11Y - » suivi du nom.
- Les fichiers exportés (grille Excel, tickets Jira, sauvegarde) reprennent le nom du projet.
- Support (Ordinateur ou Mobile), Référentiel et Fichier sont inchangés.

## 2. Module Audit
### Modes
| Mode | Écrans | Critères | Scores | État |
|---|---|---|---|---|
| **Simple** | 3 à 5 | sélection de l'audit simplifié du SIP (52), 6 critères hors sélection, 3 bonnes pratiques | taux sélection SIP (principal), taux élargi | à construire à partir de l'audit rapide actuel |
| **Complet** | selon l'échantillon du RAWeb | les 136 critères du RAWeb 1.1 (17 thématiques) | taux RAWeb | affiché « à venir », non développé |

- Le choix du mode se fait à la création de l'onglet. Le mode Complet est visible mais désactivé, avec la mention « à venir : audit complet en vue d'une déclaration d'accessibilité ».
- Simple : 5 écrans au plus. Les trois écrans proposés par défaut restent : accueil, écran avec formulaire, écran au contenu particulier (comme l'échantillon du SIP). L'affichage « un écran à la fois » prévu au-delà de 6 écrans n'est plus nécessaire dans ce mode.
- **Pas de lecture UX/POUR** dans l'Audit : elle est réservée au Scénario.

### Configurateur des fonctions primaires
Les fonctions primaires appartiennent au **projet**, pas à un onglet : c'est le même site, donc la navigation principale testée une fois vaut pour l'Audit comme pour le Scénario. Le configurateur est un **configurateur**, pas un objet de test à part : il prépare les éléments répétés.

- Au niveau du projet : la liste des fonctions et leur état (observations, statuts).
- Dans chaque onglet : les écrans où chaque fonction apparaît.

Liste préréglée, modifiable :
- navigation principale ;
- menu ou menu burger ;
- recherche ;
- formulaire type (connexion, contact) ;
- fenêtre modale et sa fermeture ;
- retour ou fil d'Ariane ;
- notifications et messages ;
- pied de page.

Pour chaque fonction, le testeur indique si elle existe et, dans chaque onglet, sur quels écrans elle apparaît. Chaque fonction présente devient un **élément répété** préparé d'avance : ses observations valent sur tous les écrans cochés, dans tous les onglets, sans ressaisie (même règle qu'aujourd'hui : un NC vaut NC sur ces écrans, un C y reste à confirmer).

Les **éléments répétés libres** restent possibles en plus : un élément hors de la liste (bandeau cookies, chat) se crée au fil de l'audit, comme aujourd'hui.

**Pas de score par fonction.** Un taux sur 4 ou 5 critères n'aurait pas de sens, le SIP n'en définit pas, et les défauts comptent déjà dans les taux de l'audit. À la place, chaque fonction affiche un **état** dans le configurateur et dans le résumé :

| Fonction | Exemple d'état |
|---|---|
| Navigation principale | 2 NC (10.7, 7.1) · 5 écrans |
| Recherche | rien à signaler · 3 écrans |
| Modale de connexion | 1 NC (12.9) · 1 écran |
| Notifications | pas encore testée |

### Déroulé
1. Préparer : nom de l'onglet, mode, écrans et leurs contenus (interrupteurs actuels).
2. Configurer les fonctions primaires.
3. Étapes de test, chacune sur tous les écrans (ordre « étape d'abord ») : tour à vide, usage standard, code et outils, lecteur d'écran, clavier. **À chaque étape, les fonctions primaires passent en premier**, puis les écrans : à l'étape Clavier, on teste la navigation principale, puis chaque écran. Une fonction déjà testée à cette étape (dans un autre onglet du projet) est marquée faite.
4. Clôture : définir les critères encore sans statut.
5. Résumé et exports : deux taux, état des fonctions primaires, non-conformités.

## 3. Module Scénario
- Même modèle qu'aujourd'hui : écrans dans l'ordre du parcours, observations de transition notées `Écran -> Écran`.
- Mêmes préréglages de fonctions primaires que l'Audit, limités à celles que le parcours traverse (formulaire, étapes, retour, confirmation).
- **Scores** : le **taux sélection SIP** seul (même formule, sur les écrans du scénario ; pas de taux élargi, peu parlant sur quelques écrans d'un parcours) et le **score UX/POUR**, réservé à ce module.
- Module à rediscuter dans le détail : liste des préréglages propres au scénario, nombre d'écrans, présentation des défauts de transition.

## 4. Panneau des étapes
- Plus de titre visible : la liste des étapes parle d'elle-même. Un titre masqué (« Étapes de l'audit » ou « Étapes du scénario ») reste lu par les lecteurs d'écran, pour que la zone soit identifiable.
- Le mot « Parcours » est libéré pour un autre usage, à définir.

## 5. Données et compatibilité
- Projet : `fonctions` (liste des fonctions primaires : identifiant, nom, présente, étapes faites) et les observations portées par une fonction.
- Onglet : `module` (`audit` ou `scenario`), `mode` (`simple`, plus tard `complet`), et pour chaque fonction présente, les écrans de l'onglet où elle apparaît.
- Une observation sur une fonction est stockée une fois, au niveau du projet, et vaut sur les écrans cochés de chaque onglet. Les taux restent calculés par onglet.
- Une fonction primaire est liée à un nom d'élément répété : les observations existantes portant ce nom s'y rattachent.
- Sauvegardes actuelles : un onglet `rapide` devient `audit` en mode `simple` ; un onglet `scenario` reste `scenario`. Un audit rapide de plus de 5 écrans reste lisible ; l'outil signale la limite à l'ajout d'un écran.

## 6. Hors périmètre de cette étape
- Mode Complet (136 critères, échantillon, déclaration).
- Agent Copilot de conversion des notes (voir la consigne intégrée et le skill « observations-ruxaweb »).
- Report dans RUXAAM.

## 7. Questions ouvertes
- Usage du mot « Parcours ».
- Liste définitive des fonctions primaires, et leurs types d'élément par défaut.
- Retest d'une fonction : remet-il le critère à NT dans tous les onglets à la fois (proposition : oui, puisque la fonction est commune) ?
- Scénario : nombre minimal et maximal d'écrans.
