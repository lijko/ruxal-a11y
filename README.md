# RUXAL : Revue UX Accessibilité

**FR** : RUXAL est une famille d'outils HTML autonomes qui aident à **préparer et prioriser un audit d'accessibilité**, avant l'audit complet. Chaque outil croise deux regards sur ce que l'on examine (écran, fonctionnalité ou parcours) :

- **les critères officiels du référentiel** (RAAM 1.1 pour le mobile, RAWeb 1.1 pour le web, RAPDF 1.1 pour le PDF), évalués critère par critère (conforme, non conforme, non testé, non applicable), qui donnent un **taux de conformité** par onglet ;
- **une lecture UX qualitative** : les quatre principes **POUR** de WCAG (Perceptible, Utilisable, Compréhensible, Robuste) et les **heuristiques d'utilisabilité**, qui servent à repérer les problèmes que les critères seuls ne montrent pas. Cette couche est **exclue du taux**.

Trois types d'audit : l'**audit rapide** (critères du référentiel), la **fonctionnalité primaire** (fermer, retour, menu, navigation, formulaire, notification) et le **scénario** (parcours complexe, critères + lecture UX). Les résultats s'exportent en Excel (liste des critères), CSV (import Jira), JSON et PDF.

RUXAL n'est **pas un audit de conformité** et ne produit aucune déclaration d'accessibilité : c'est un outil de pré-diagnostic, qui complète l'audit réalisé par un expert.

**Gravité** : chaque critère porte une gravité par défaut (Critique, Sérieux, Modéré, Mineur), qui sert à trier les non-conformités et à prioriser les tickets. Elle **n'est pas normative** : ni le RAAM ni WCAG 2.x n'en définissent. L'échelle est propre à RUXAL, inspirée de l'échelle d'impact de Deque (axe-core) ; le brouillon WCAG 3 du W3C, encore instable, n'est pas utilisé. Détail dans [`docs/gravite.md`](docs/gravite.md).

Outils : **RUXAAM** (mobile, RAAM 1.1), **RUXAWEB** (web, RAWeb 1.1), **RUXAPDF** (PDF, RAPDF 1.1, prévu).

**EN** : RUXAL is a family of standalone HTML tools that help **prepare and prioritise an accessibility audit**, ahead of a full audit. Each tool looks at what you are reviewing (a screen, a feature or a journey) in two ways:

- **the official criteria of the standard** (RAAM 1.1 for mobile, RAWeb 1.1 for web, RAPDF 1.1 for PDF), assessed one by one (compliant, non-compliant, not tested, not applicable), which produce a **conformity rate** per tab;
- **a qualitative UX reading**: the four **POUR** principles of WCAG (Perceivable, Operable, Understandable, Robust) and **usability heuristics**, used to spot issues that criteria alone do not reveal. This layer is **excluded from the rate**.

Three audit types: **quick audit** (standard criteria), **primary feature** (close, back, menu, navigation, form, notification) and **scenario** (complex journey, criteria + UX reading). Results can be exported to Excel (criteria list), CSV (Jira import), JSON and PDF.

RUXAL is **not a compliance audit** and produces no accessibility statement: it is a pre-diagnosis tool that complements an expert's audit.

**Severity**: each criterion has a default severity (Critical, Serious, Moderate, Minor), used to sort issues and prioritise tickets. It is **not normative**: neither RAAM nor WCAG 2.x define severity. The scale is RUXAL's own, inspired by Deque's axe-core impact levels; the unstable WCAG 3 draft is not used. See [`docs/gravite.md`](docs/gravite.md).

Tools: **RUXAAM** (mobile, RAAM 1.1), **RUXAWEB** (web, RAWeb 1.1), **RUXAPDF** (PDF, RAPDF 1.1, planned).

## Statut / Status
Projet en cours de préparation pour publication. / Project being prepared for publication.

## Utilisation / Usage
Ouvrir le fichier HTML de l'outil dans un navigateur. / Open the tool's HTML file in a browser.

RUXAAM 1.27 : **52 critères RAAM** (dont 20 « si présent ») et **3 bonnes pratiques** hors taux, soit 57 éléments. Gravités par défaut des critères RAAM : 12 Critique, 29 Sérieux, 10 Modéré, 1 Mineur.

- **Protocole de test en 4 étapes** : 1. usage standard, 2. agrandissement (texte, puis affichage), 3. lecteur d'écran (3a contenus et structure, 3b composants, formulaires et annonces), 4. navigation alternative (clavier externe, commande vocale ; contrôle de sélection et Switch Access optionnels). Chaque critère est rattaché à l'étape où on le constate le plus facilement. Séquence construite par RUXAAM à partir des pratiques décrites par Apple et Android ; ce n'est pas un protocole officiel. Le détail est dans l'écran Aide de l'outil.
- **Vue « Par étape de test »** : dans un onglet RAAM, la liste peut être rangée par thème ou par étape. Un critère n'apparaît qu'une fois, dans son étape principale. Statuts, taux et exports ne changent pas.
- **Plateforme** : iOS, Android ou multiplateforme, choisie sous le nom de l'audit (un audit = une plateforme). Elle détermine les recommandations « Per platform » et une étiquette supplémentaire des tickets Jira.
- **Contenu des écrans** : en tête d'un onglet RAAM, un interrupteur par écran et par type d'élément (CAPTCHA, image complexe, média, tableau, formulaire), plus un interrupteur « Limite de session » pour toute l'application. Un critère « si présent » ne s'affiche que si un écran contient l'élément ; ailleurs il compte comme NA, sans rien effacer de ce qui a été saisi.
- **Écrans testés** : dans un onglet, le panneau « Écrans testés » permet de renommer, d'ajouter ou de supprimer (en deux clics) un écran en cours d'audit. Un ajout ou une suppression repasse l'onglet en brouillon ; un nouvel écran part en NT. L'audit rapide garde au moins 3 écrans. Les tickets Jira déjà créés ne sont pas modifiés.
- **Un écran à la fois** : au-delà de 6 écrans (outil pensé pour l'ordinateur), la liste n'affiche plus que l'écran choisi dans une barre qui reste visible pendant le défilement (avec Précédent / Suivant et le nombre de non-conformités par écran), plus la colonne « Tous » et le statut d'ensemble de l'onglet sur chaque critère.
- **Élément concerné** : pour chaque critère non conforme et chaque écran, un champ d'une ligne reçoit la notation `Écran[type "Libellé"] (état)`, expliquée dans l'Aide (« Noter les éléments »). L'export Jira la reprend dans le titre et le corps du ticket.
- **Mémoire des exports Jira** : l'outil retient les critères déjà exportés (pour tout l'audit, avec la sauvegarde) et ne les exporte pas deux fois ; « Tickets Jira : tout réexporter » les reprend tous. Le champ « Ticket Jira » des versions précédentes est retiré.
- **Formats d'export** : Liste des critères en **Excel (.xlsx)** : une ligne par critère et par onglet, colonnes dimensionnées, ligne d'en-tête figée, filtres, statuts colorés, numéros de critères gardés en texte (« 10.10 » reste 10.10). Tickets Jira en **CSV** (séparateur virgule), à importer dans Jira et non à ouvrir dans Excel. Le téléchargement passe uniquement par le navigateur, sans dépendance à une autre application. 
- **Exports** : aucun fichier vide n'est produit. Sans onglet, sans onglet RAAM, sans critère testé ou sans critère non conforme, un message explique pourquoi l'export n'a pas lieu. À l'import d'une sauvegarde plus ancienne, l'outil signale les critères qui n'existent plus dans cette version.

### RUXAWEB 2.0 (web, RAWeb 1.1)
`src/ruxaweb.html` : audit par observations. L'auditeur note ce qu'il constate, la grille des critères se remplit. Spécification : [`docs/audit-par-observations.md`](docs/audit-par-observations.md).

- **Critères** : les **52 critères du RAWeb 1.1** retenus par la [méthode de contrôle simplifié v1.2.1 du SIP](https://accessibilite.public.lu/fr/monitoring/controle-simplifie.html), intitulés officiels non modifiés, dont 24 « si présent ». Aucune adaptation : le taux reste lisible à côté d'un audit simplifié du SIP (même sélection, même formule), sans en être un résultat officiel. Traçabilité : `docs/selection-audit-rapide-web.csv`.
- **6 critères hors sélection** : 3.3, 7.1, 7.5, 9.3, 10.4 et 13.11, critères officiels absents de la méthode du SIP, ajoutés parce qu'ils couvrent des défauts fréquents. Champ `hors_selection` de `data/criteres-raweb.json`.
- **Deux taux**, même formule : le **taux sélection SIP** (52 critères), taux principal, et le **taux élargi** (58 critères).
- **3 bonnes pratiques hors RAWeb** (hors taux) : taille des cibles (WCAG 2.2, 2.5.8), fermeture d'une fenêtre modale au clavier, retour du focus à sa fermeture.
- **On note des observations, la grille se remplit** : chaque observation porte un tag (#c, #nc, #na) et un ou plusieurs critères, proposés à partir d'un point de contrôle (`data/symptomes-ruxaweb.json`). Sans critère, c'est une note libre. Un critère sans observation reste NT ; le pire statut l'emporte.
- **Écrans** : une page du site, ou un état de page (fenêtre modale ouverte, étape d'un formulaire). L'audit simple porte sur 3 à 5 écrans (accueil, écran avec formulaire, écran au contenu particulier), comme l'audit simplifié du SIP. Fonctions primaires : configurateur au niveau du projet, voir `docs/projet-a11y-modules.md`.
- **Contenu des écrans** : un interrupteur par écran et par contenu (CAPTCHA, image complexe, média temporel ou son, média non temporel, tableau de données, cadre, formulaire, autre langue). Un contenu absent rend ses critères « si présent » non applicables.
- **Parcours guidé, étape par étape** : chaque étape se fait sur tous les écrans avant la suivante (un seul réglage d'outil par étape, éléments répétés repérés tôt) ; la navigation reste libre. Tour à vide, puis les 4 étapes du protocole (1. usage standard, 2. code et outils, 3. lecteur d'écran, 3a contenus et 3b formulaires, 4. clavier), puis clôture et résumé. Le panneau Parcours, fixe et toujours au même endroit, montre l'étape en cours (liste complète à déplier, boutons Précédente et Suivante) et dit quoi faire et quoi chercher. Protocole construit à partir de la méthodologie du RAWeb 1.1 et de la méthode du SIP ; pas un protocole officiel.
- **Navigation** : en haut le nom de l'audit, le support (Ordinateur ou Mobile) et le menu Fichier, puis les onglets de l'audit ; dans un onglet, les vues Saisie et Grille.
- **Élément et écrans concernés** : deux champs ordinaires de toute observation. L'écran en cours est toujours coché ; l'auditeur coche les autres écrans où l'observation est vraie et peut nommer l'élément (ex. Menu principal). Un élément observé sur au moins deux écrans figure dans la liste « Éléments répétés ». Un #nc vaut NC sur les écrans cochés, un #c y reste à confirmer. Le taux reste comparable à celui du SIP.
- **Retest** : depuis la grille, un critère se remet à NT sur un écran ; les observations précédentes restent visibles, barrées.
- **Clôture** : un critère à la fois, avec sa fiche (niveau, comment vérifier, impact, lien officiel, observations), puis le statut de chaque écran encore sans statut (C, NC avec une observation, NA).
- **Scénario** : champ « Transition vers » pour une observation sur le passage d'un écran à l'autre (notation Écran -> Écran), et **lecture POUR/UX** : 8 questions sur le parcours entier (Succès, Difficile, Échec, N/A). Score à part, jamais dans le taux.
- **Exports** (menu Fichier) : grille Excel, un ticket Jira par observation non conforme (un seul pour une observation qui vaut sur plusieurs écrans), sauvegarde JSON. Référence des tickets : « RAWeb 1.1, Criterion X.Y » avec un lien `criteres.html#crit-X-Y`. Mémoire des exports Jira : un ticket déjà exporté ne repart pas (mémoire gardée dans la sauvegarde) ; « Tickets Jira : tout réexporter » les reprend tous.
- **Référentiel** (bouton du haut) : une fiche par critère et bonne pratique, avec gravité, étape de test, « Comment vérifier » et impact, regroupées par thématique RAWeb ou par thème RUXAL, plus la notation des éléments. « Imprimer ou enregistrer en PDF » passe par l'impression du navigateur, sans bibliothèque ajoutée.
- **Gravité** : affichée dans la grille, les fiches et le résumé ; elle trie les non-conformités et donne la priorité des tickets Jira.
- **Saisie assistée** : suggestions de points de contrôle pendant la frappe (mots-clés de `data/symptomes-ruxaweb.json`), « Coller des observations » au format `statut | élément | observation | point de contrôle` (critères déduits ; numéros de critères acceptés), et consigne prête à copier pour faire convertir des notes libres par une IA. Les lignes collées deviennent des pistes à vérifier.
- **Import axe ou Lighthouse** : un rapport (JSON d'axe-core, export JSON ou CSV de l'extension axe DevTools, JSON de Lighthouse) s'importe sur l'écran en cours. Ses échecs et points à vérifier arrivent comme pistes, jamais comme statuts : l'auditeur les reprend dans une observation ou les écarte. Critères proposés par `data/axe-raweb.json`, sinon par les critères WCAG du rapport axe.
- **Données séparées de RUXAAM** : stockage local et sauvegardes distincts.
- **Gravités** : base de discussion, alignées sur les critères équivalents de RUXAAM quand il y en a.
- **RUXAAM** garde pour le moment la saisie critère par critère.

**EN**: `src/ruxaweb.html` is an observation-based audit tool for the web: the auditor records observations, and the RAWeb 1.1 criteria grid (52 criteria of the SIP simplified audit method, plus 6) fills itself. Guided screen-by-screen flow, two compliance rates, axe and Lighthouse report import.

## Données et génération / Data and build
Chaque outil reste **un seul fichier HTML autonome**, mais ses critères ne s'éditent pas dans le HTML : la source de vérité est dans `data/`.

| Fichier | Contenu | Licence |
|---|---|---|
| `data/criteres-raam.json` | 52 critères officiels du RAAM 1.1 (intitulés du SIP, non modifiés) ; 20 « si présent », chacun rattaché à un déclencheur ; étape de test de chaque critère | CC BY 3.0 LU |
| `data/bonnes-pratiques.json` | 3 bonnes pratiques hors RAAM (hors taux), avec leur étape de test | CC BY 4.0 |
| `data/themes-ruxal.json` | ordre et noms des 7 thèmes RUXAL | CC BY 4.0 |
| `data/textes-ruxal.json` | gravité (non normative, voir `docs/gravite.md`), texte d'impact et consigne de test de chaque critère ; libellés des 6 déclencheurs | CC BY 4.0 |
| `data/criteres-raweb.json` | RUXAWEB : 52 critères officiels du RAWeb 1.1 (audit simplifié du SIP), plus 6 critères hors sélection (3.3, 7.1, 7.5, 9.3, 10.4, 13.11), comptés dans le taux élargi seulement (intitulés non modifiés) ; 24 « si présent » ; étape de test | CC BY 3.0 LU |
| `data/bonnes-pratiques-web.json` | RUXAWEB : 3 bonnes pratiques hors RAWeb (hors taux) | CC BY 4.0 |
| `data/textes-ruxaweb.json` | RUXAWEB : gravité, impact et consigne de test de chaque critère ; 8 déclencheurs | CC BY 4.0 |

`data/themes-ruxal.json` est commun à toute la famille.

Après toute modification de `data/`, régénérer l'outil (Python 3, sans dépendance) :

```bash
python3 scripts/build_ruxaam.py
python3 scripts/build_ruxaweb.py
```

Le script valide les données (texte manquant, thème ou gravité inconnus, identifiant en double) puis remplace le bloc compris entre les marqueurs `DEBUT_DONNEES` et `FIN_DONNEES` de `src/ruxaam.html`. Ne pas modifier ce bloc à la main. `python3 scripts/build_ruxaam.py --check` vérifie que le HTML est à jour (code retour 1 sinon), utile avant un commit.

Identifiants stables : `raam-1-2` pour le critère RAAM 1.2, `bp1` pour une bonne pratique. / Stable ids: `raam-1-2` for RAAM criterion 1.2, `bp1` for a best practice. **EN** : edit `data/`, then run the script above to inject the data into the standalone HTML file.

## Structure
- `src/` : outils (code)
- `data/` : critères, thèmes, couche POUR/heuristiques (données)
- `docs/` : documentation
- `scripts/` : génération des outils à partir de `data/` ; `demo_ruxaam.py` et `demo_ruxaweb.py` régénèrent les données fictives en saisissant un audit dans l'outil (Playwright)
- `exemples/` : données fictives à ouvrir dans l'outil pour l'essayer (`donnees-fictives-ruxaam.json` : bouton « Importer » de RUXAAM ; `donnees-fictives-ruxaweb.json` : Fichier, « Ouvrir une sauvegarde » de RUXAWEB)
- `tests/` : tests de bout en bout de l'outil (Playwright)

## Tests
```bash
python3 -m pip install playwright
python3 -m playwright install chromium
python3 tests/test_ruxaam.py
python3 tests/test_ruxaweb.py
python3 tests/test_symptomes_ruxaweb.py
```
Les tests ouvrent `src/ruxaam.html` en `file://` et vérifient notamment : nombre de critères et de pastilles d'étape, vues par thème et par étape, « Contenu des écrans », « Élément concerné » et aide à la notation, export Jira selon la plateforme et mémoire des exports, messages d'export sans fichier vide, import d'une sauvegarde 1.21 (migration), absence d'erreur JavaScript, gestion des écrans en cours d'audit et affichage un écran à la fois au-delà de 6. `tests/test_ruxaweb.py` vérifie les règles de RUXAWEB : contenu des écrans, observations valables sur plusieurs écrans, retest, clôture, deux taux, exports et import.

## Licences / Licences
| Contenu | Licence |
|---|---|
| Code (`src/`) | EUPL-1.2 |
| Données et documentation (`data/`, `docs/`) | CC BY 4.0 |

Le détail par fichier est dans `REUSE.toml`. Les textes complets des licences sont dans `LICENSES/`.

## Attributions
Voir `NOTICE`. Cet outil n'est ni approuvé ni certifié par le W3C, le SIP, l'OSAPS ou Deque Systems.

## Contribuer / Contributing
Voir `CONTRIBUTING.md`.
