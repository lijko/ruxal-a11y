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

### RUXAWEB 1.7 (web, RAWeb 1.1)
`src/ruxaweb.html` : même moteur, mêmes types d'audit, mêmes thèmes RUXAL, même couche POUR et UX, mêmes exports que RUXAAM, adaptés au web.

- **Critères** : les **52 critères du RAWeb 1.1** retenus par la [méthode de contrôle simplifié v1.2.1 du SIP](https://accessibilite.public.lu/fr/monitoring/controle-simplifie.html) (47 testés manuellement, 19 avec Axe, 52 distincts), intitulés officiels non modifiés ; 24 « si présent ». Contrairement à RUXAAM, aucune adaptation : la grille du SIP est faite pour le web, le taux reste donc lisible à côté d'un audit simplifié du SIP (même sélection, même formule), sans en être un résultat officiel. Traçabilité : `docs/selection-audit-rapide-web.csv`.
- **6 critères hors sélection** : 3.3, 7.1, 7.5, 9.3, 10.4 et 13.11, critères officiels du RAWeb 1.1 absents de la méthode du SIP, ajoutés parce qu'ils couvrent des défauts fréquents (composant en script sans nom, rôle ni état ; message de statut non restitué ; contraste des icônes et du focus ; listes ; texte agrandi). Champ `hors_selection` de `data/criteres-raweb.json` ; leurs non-conformités partent dans l'export Jira.
- **Deux taux** : le **taux sélection SIP**, taux principal, calculé sur les 52 critères de la méthode du SIP et comparable à leur audit simplifié ; le **taux élargi**, calculé sur les 58 critères RAWeb de l'outil, affiché à côté (audit, résumé, tableau de bord, export JSON). Même formule pour les deux.
- **3 bonnes pratiques hors RAWeb** (hors taux) : taille des cibles (WCAG 2.2, 2.5.8), fermeture d'une fenêtre modale au clavier, retour du focus à sa fermeture.
- **Écrans** : comme dans RUXAAM, l'objet testé s'appelle un écran (une page du site, ou un état de page : fenêtre modale ouverte, étape d'un formulaire). L'audit rapide porte sur 3 écrans au moins (accueil, écran avec formulaire, écran au contenu particulier), comme l'audit simplifié du SIP.
- **Contenu des écrans** : 8 déclencheurs (CAPTCHA, image complexe, média temporel ou son, média non temporel, tableau de données, cadre, formulaire, autre langue). Pas de déclencheur global : la limite de temps (13.1) est un critère cœur.
- **Protocole de test en 4 étapes** : 1. usage standard, 2. code et outils (inspecteur du navigateur, outil automatique en appoint), 3. lecteur d'écran (NVDA ou VoiceOver ; 3a contenus et structure, 3b formulaires), 4. navigation au clavier. Construit à partir de l'environnement de test et de la méthodologie du RAWeb 1.1 et de la méthode simplifiée du SIP ; pas un protocole officiel.
- **Écrans testés** : dans un onglet, le panneau « Écrans testés » permet de renommer, d'ajouter ou de supprimer (en deux clics) un écran en cours d'audit. Un ajout ou une suppression repasse l'onglet en brouillon ; un nouvel écran part en NT. L'audit rapide garde au moins 3 écrans. Les tickets Jira déjà créés ne sont pas modifiés.
- **Un écran à la fois** : au-delà de 6 écrans (outil pensé pour l'ordinateur), la liste n'affiche plus que l'écran choisi dans une barre qui reste visible pendant le défilement (avec Précédent / Suivant et le nombre de non-conformités par écran), plus la colonne « Tous » et le statut d'ensemble de l'onglet sur chaque critère.
- **Support** : Ordinateur ou Mobile (un audit = un support), repris dans le bloc « Recommendations » et une étiquette des tickets Jira. Référence des tickets : « RAWeb 1.1, Criterion X.Y » avec un lien `criteres.html#crit-X-Y`.
- **Données séparées de RUXAAM** : stockage local (`atelier-ruxaweb-state`) et sauvegardes (`RUXAWEB-etat`) distincts ; une sauvegarde RUXAAM ne s'ouvre pas dans RUXAWEB.
- **Gravités** : base de discussion, alignées sur les critères équivalents de RUXAAM quand il y en a (8 Critique, 25 Sérieux, 18 Modéré, 1 Mineur).

**EN**: `src/ruxaweb.html` applies the same engine to the web, with the 52 RAWeb 1.1 criteria of the SIP simplified audit method, a 4-step web test protocol, and the same notion of screens.

### RUXAWEB 2.0 (web, audit par observations)
`src/ruxaweb2.html` : nouvelle façon d'auditer, à côté de la 1.7 qui reste disponible (`src/ruxaweb.html`, branche `archive/ruxaweb-v1.7`). Mêmes critères, mêmes textes, même formule de taux. Spécification : [`docs/audit-par-observations.md`](docs/audit-par-observations.md).

- **On note des observations, la grille se remplit** : chaque observation porte un tag (#c, #nc, #na) et un ou plusieurs critères, proposés à partir d'un point de contrôle (`data/symptomes-ruxaweb.json`). Sans critère, c'est une note libre.
- **Parcours guidé, écran par écran** : tour à vide, puis les 4 étapes du protocole, puis clôture et résumé. Le panneau d'aide, toujours au même endroit, montre le parcours et dit quoi faire et quoi chercher à l'étape en cours.
- **Élément et écrans concernés** : deux champs ordinaires de toute observation, sans saisie à part. L'écran en cours est toujours coché ; l'auditeur coche les autres écrans où l'observation est vraie et peut nommer l'élément (ex. Menu principal). Un élément observé sur au moins deux écrans figure dans la liste « Éléments répétés ». Un #nc vaut NC sur les écrans cochés, un #c y reste à confirmer. Une observation n'a jamais de statut propre : le taux reste comparable à celui du SIP.
\1\n- **Clôture** : un critère à la fois, avec sa consigne « Comment vérifier », puis le statut de chaque écran encore sans statut (C, NC avec une observation, NA). « Conforme sur les N écrans » existe, mais critère par critère, pour éviter de tout valider en série.
- **Scénario** : champ « Transition vers » pour une observation sur le passage d'un écran à l'autre (notation Écran -> Écran).
- **Exports** (menu Fichier) : grille Excel, un ticket Jira par observation non conforme (un seul pour une observation qui vaut sur plusieurs écrans), sauvegarde JSON. Les sauvegardes 1.x s'ouvrent dans la 1.7.
- **Import axe ou Lighthouse** : un rapport JSON (axe-core, ou Lighthouse depuis les outils de développement d'Edge ou de Chrome) s'importe sur l'écran en cours. Ses échecs et points à vérifier arrivent comme pistes, jamais comme statuts : l'auditeur les reprend dans une observation ou les écarte. Critères proposés par `data/axe-raweb.json` (correspondance RUXAL, relue contre la documentation officielle d'axe-core), sinon par les critères WCAG que donne le rapport axe.
- **Lecture POUR/UX** (scénarios seulement) : les 8 questions de la 1.7, sur le parcours entier (Succès, Difficile, Échec, N/A, avec un commentaire si difficile ou échec). Score à part, jamais dans le taux ; repris dans le résumé et l'export Excel.
- **Pas encore repris** : PDF du référentiel. RUXAAM reste sur le modèle 1.x pour le moment.

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
python3 scripts/build_ruxaweb2.py
```

Le script valide les données (texte manquant, thème ou gravité inconnus, identifiant en double) puis remplace le bloc compris entre les marqueurs `DEBUT_DONNEES` et `FIN_DONNEES` de `src/ruxaam.html`. Ne pas modifier ce bloc à la main. `python3 scripts/build_ruxaam.py --check` vérifie que le HTML est à jour (code retour 1 sinon), utile avant un commit.

Identifiants stables : `raam-1-2` pour le critère RAAM 1.2, `bp1` pour une bonne pratique. / Stable ids: `raam-1-2` for RAAM criterion 1.2, `bp1` for a best practice. **EN** : edit `data/`, then run the script above to inject the data into the standalone HTML file.

## Structure
- `src/` : outils (code)
- `data/` : critères, thèmes, couche POUR/heuristiques (données)
- `docs/` : documentation
- `scripts/` : génération des outils à partir de `data/`
- `tests/` : tests de bout en bout de l'outil (Playwright)

## Tests
```bash
python3 -m pip install playwright
python3 -m playwright install chromium
python3 tests/test_ruxaam.py
python3 tests/test_ruxaweb.py
python3 tests/test_ruxaweb2.py
python3 tests/test_symptomes_ruxaweb.py
```
Les tests ouvrent `src/ruxaam.html` en `file://` et vérifient notamment : nombre de critères et de pastilles d'étape, vues par thème et par étape, « Contenu des écrans », « Élément concerné » et aide à la notation, export Jira selon la plateforme et mémoire des exports, messages d'export sans fichier vide, import d'une sauvegarde 1.21 (migration), absence d'erreur JavaScript, gestion des écrans en cours d'audit et affichage un écran à la fois au-delà de 6. `tests/test_ruxaweb.py` fait les mêmes vérifications pour RUXAWEB (écrans, 8 déclencheurs, étapes web, support Ordinateur ou Mobile, lien RAWeb des tickets). `tests/test_ruxaweb2.py` vérifie les règles de RUXAWEB 2 : configurateur, observations valables sur plusieurs écrans, retest, deux taux, exports et import.

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
