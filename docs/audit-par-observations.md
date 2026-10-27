<!--
SPDX-FileCopyrightText: 2026 Bertrand Kempf
SPDX-License-Identifier: CC-BY-4.0
-->
# Audit par observations

**Statut : brouillon de spécification (27 octobre 2026).** Rien de ce qui est décrit ici n'est encore construit. Cible : RUXAWEB d'abord, RUXAAM ensuite (sans l'import d'outils automatiques, qui n'existent que pour le web).

## Principe
Aujourd'hui, l'audit part de la liste des critères : le testeur lit chaque critère, cherche s'il est respecté, puis décrit les problèmes.

L'audit par observations inverse ce sens. Le testeur note ce qu'il constate, au fil du test ; chaque constat est rattaché à un ou plusieurs critères ; **la grille des critères se remplit à partir des observations**.

Pourquoi :
- c'est l'ordre naturel du test : on voit un problème avant de savoir quel critère il viole ;
- une observation peut toucher plusieurs critères, et un critère peut regrouper plusieurs observations ;
- une observation non conforme a déjà la forme d'un ticket Jira.

La grille officielle reste la sortie de référence : mêmes critères, même formule de taux, même comparabilité avec l'audit simplifié du SIP.

## 1. Configurateur par écran
Avant de tester un écran, le testeur répond aux questions des déclencheurs (CAPTCHA, image complexe, média temporel, média non temporel, tableau de données, cadre, formulaire, changement de langue).

- Composant **absent** : les critères « si présent » qui en dépendent passent **NA**.
- Composant **présent** : ces critères entrent dans le **périmètre** de l'écran.
- Les critères de cœur sont toujours dans le périmètre.

Le périmètre est la liste des critères qui doivent recevoir un statut avant que l'écran soit complet. Rien n'est conforme par défaut.

## 2. Observations
### Format
```
Écran[type "Libellé"] (état) : constat. Attendu : ... #tag
```
- Élément : `Écran[type "Libellé"]`, état facultatif entre parenthèses.
- Flux : `Écran -> Écran`.
- Élément global présent sur tous les écrans : sans écran devant, par exemple `[Main navigation]`.
- Référence de critère facultative en fin de ligne : `RAWeb 11.1`.

Exemples :
```
Panier[bouton "×"] : restitué "bouton", sans nom. Attendu : "Supprimer l'article". #nc
Connexion[champ "E-mail"] (erreur) : message d'erreur restitué et lié au champ. #c
Accueil -> Panier : le focus reste sur le menu après validation. #nc
```

### Tags
Les tags reprennent les statuts de la grille, pour n'avoir qu'un seul vocabulaire.

| Tag | Sens | Effet sur les critères rattachés |
|---|---|---|
| `#c` | constat conforme | alimente C |
| `#nc` | constat non conforme | alimente NC |
| `#na` | le critère ne s'applique pas ici (justification sur place) | alimente NA |
| `#nt` | remise à zéro, par exemple avant un retest | remet NT, invalide les observations antérieures |

NT n'est pas un tag de constat : c'est l'état par défaut de tout critère du périmètre sans observation.

Le tag qualifie le **constat**, pas le critère : une observation `#nc` rend NC tous les critères auxquels elle est rattachée.

### Corriger ou retester
- **Erreur de saisie** (constat faux, mauvais rattachement) : on modifie ou on supprime l'observation. Le statut se recalcule.
- **Retest** (le constat était juste, la situation a changé, par exemple après correction) : on ajoute `#nt` sur le critère. Les observations antérieures restent visibles, barrées, comme historique ; seules les observations postérieures comptent. L'historique NC, puis NT, puis C sert de trace de correction.

### Règles de rédaction
- **Factuel** : ce qui est vu, entendu ou atteint, pas l'interprétation.
- **Restitution exacte** entre guillemets quand elle vient d'un lecteur d'écran.
- **Un constat par observation**, même si deux défauts touchent le même élément.
- **Noter aussi le conforme** : sans `#c`, un critère reste NT.
- Consignes génériques : aucun raccourci, menu ou produit propre à un lecteur d'écran ou à un outil.

## 3. Rattachement aux critères
Trois sources, toutes soumises à la validation du testeur :
1. **Référence saisie** par le testeur (`RAWeb 11.1`).
2. **Suggestion par symptôme**, sans IA : le testeur choisit un symptôme en langage de terrain (« non restitué », « nom incorrect », « focus perdu », « contraste faible », « non atteignable au clavier »...), l'outil propose les critères correspondants. La table symptôme vers critères est une donnée de RUXAL, à construire et à maintenir par référentiel.
3. **Import d'un rapport automatique** (section 5).

## 4. Calcul des statuts
Pour chaque critère et chaque écran :
1. Hors périmètre (déclencheur absent) : **NA**.
2. Seules comptent les observations **valides** : celles postérieures au dernier `#nt` du critère.
3. Parmi elles, **le pire statut l'emporte** : NC, puis C.
4. Une observation `#na` face à une observation `#c` ou `#nc` sur le même critère est signalée comme **incohérence** à trancher.
5. Sans observation valide : **NT**.

Le taux de conformité ne change pas : même formule, même sélection, critères hors sélection du SIP (comme RAWeb 13.11) évalués mais exclus du taux.

**Complétude** d'un écran : part des critères du périmètre qui ne sont plus NT. Une **passe de clôture** liste les critères restés NT pour les trancher (`#c`, `#nc`, `#na` justifié ou « à creuser »).

## 5. Import des outils automatiques (web)
La méthode de contrôle simplifié du SIP s'appuie déjà sur Axe pour une partie des critères ; l'import prolonge cette pratique.

Sources acceptées :
- **Rapport Lighthouse en JSON**, exporté depuis les outils de développement d'Edge ou de Chrome, sans rien installer.
- **Rapport axe-core en JSON**.

Lighthouse s'appuie sur axe-core pour son audit d'accessibilité : les deux rapports se recoupent, les résultats sont dédoublonnés par règle.

Correspondance : chaque règle porte les critères WCAG qu'elle teste ; chaque critère RAWeb cite ses critères WCAG. Le croisement des deux donne les critères RAWeb candidats.

| Résultat de l'outil | Ce que RUXAL en fait |
|---|---|
| Violation | observation **candidate** `#nc`, à confirmer |
| Résultat incomplet | point **à vérifier** manuellement |
| Règle réussie | **aucune conclusion** : un test automatique ne couvre qu'une partie d'un critère |

Aucune observation importée ne produit de statut tant que le testeur ne l'a pas confirmée. Un C demande toujours une observation `#c` humaine.

Les noms de règles des outils n'apparaissent pas dans les consignes de test ; ils restent dans le détail de l'observation importée, comme preuve.

## 6. Sorties
- **Vue interactive** : la grille actuelle de l'outil, alimentée par les observations, avec pour chaque critère ses observations et leurs preuves.
- **Grille officielle** du SIP en .xlsx (pas de CSV, que les tableurs déforment).
- **Tickets Jira** en CSV : une observation `#nc` confirmée donne un ticket (titre `[A11Y] | <Application> | <Thème> | <Écran/élément> : <défaut>`, blocs Actual behavior / Impact, Expected behavior, Recommendations, référence `RAWeb 1.1, Criterion X.Y`).

## 7. Niveaux de déploiement
1. **Socle sans IA, dans l'outil HTML** : configurateur, observations, tags, suggestion par symptôme, import Lighthouse et axe, calcul, exports. Gratuit, hors ligne, fonctionne sous Windows sans installation. C'est la référence.
2. **Agent dans l'assistant de l'organisation** (Copilot, à vérifier : Microsoft 365 ou GitHub) : suggestion de critères à partir d'observations rédigées librement, avec le référentiel et la table des symptômes en connaissance. Les données d'audit doivent respecter la politique de l'employeur.
3. **Script local** (Node.js, Playwright, axe-core) pour tester plusieurs écrans d'affilée, dans leurs différents états : utilise l'Edge déjà installé, se lance par un fichier `.cmd`, produit un JSON importable dans l'outil.

## Points ouverts
- Table symptôme vers critères : liste des symptômes et correspondances RAWeb, puis RAAM.
- Coexistence avec la saisie actuelle critère par critère : garder les deux modes ou basculer entièrement.
- Format d'export et de réimport des observations (sauvegarde d'un audit en cours).
- Type de Copilot disponible et ouverture de la création d'agents.
- Application à RUXAAM : configurateur et tags identiques, sans import automatique.
