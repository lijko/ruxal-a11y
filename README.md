# RUXAL — Revue UX Accessibilité

**FR** — RUXAL est une famille d'outils HTML autonomes qui aident à **préparer et prioriser un audit d'accessibilité**, avant l'audit complet. Chaque outil croise deux regards sur ce que l'on examine (écran, fonctionnalité ou parcours) :

- **les critères officiels du référentiel** (RAAM 1.1 pour le mobile, RAWEB pour le web, RAPDF pour le PDF), évalués critère par critère (conforme, non conforme, non testé, non applicable), qui donnent un **taux de conformité** par onglet ;
- **une lecture UX qualitative** : les quatre principes **POUR** de WCAG (Perceptible, Utilisable, Compréhensible, Robuste) et les **heuristiques d'utilisabilité**, qui servent à repérer les problèmes que les critères seuls ne montrent pas. Cette couche est **exclue du taux**.

Trois types d'audit : l'**audit rapide** (critères du référentiel), la **fonctionnalité primaire** (fermer, retour, menu, navigation, formulaire, notification) et le **scénario** (parcours complexe, critères + lecture UX). Les résultats s'exportent en CSV.

RUXAL n'est **pas un audit de conformité** et ne produit aucune déclaration d'accessibilité : c'est un outil de pré-diagnostic, qui complète l'audit réalisé par un expert.

**Gravité** : chaque critère porte une gravité par défaut (Critique, Sérieux, Modéré, Mineur), qui sert à trier les non-conformités et à prioriser les tickets. Elle **n'est pas normative** : ni le RAAM ni WCAG 2.x n'en définissent. L'échelle est propre à RUXAL, inspirée de l'échelle d'impact de Deque (axe-core) ; le brouillon WCAG 3 du W3C, encore instable, n'est pas utilisé. Détail dans [`docs/gravite.md`](docs/gravite.md).

Outils : **RUXAAM** (mobile, RAAM 1.1), **RUXAWEB** (web), **RUXAPDF** (PDF).

**EN** — RUXAL is a family of standalone HTML tools that help **prepare and prioritise an accessibility audit**, ahead of a full audit. Each tool looks at what you are reviewing (a screen, a feature or a journey) in two ways:

- **the official criteria of the standard** (RAAM 1.1 for mobile, RAWEB for web, RAPDF for PDF), assessed one by one (compliant, non-compliant, not tested, not applicable), which produce a **conformity rate** per tab;
- **a qualitative UX reading**: the four **POUR** principles of WCAG (Perceivable, Operable, Understandable, Robust) and **usability heuristics**, used to spot issues that criteria alone do not reveal. This layer is **excluded from the rate**.

Three audit types: **quick audit** (standard criteria), **primary feature** (close, back, menu, navigation, form, notification) and **scenario** (complex journey, criteria + UX reading). Results can be exported as CSV.

RUXAL is **not a compliance audit** and produces no accessibility statement: it is a pre-diagnosis tool that complements an expert's audit.

**Severity**: each criterion has a default severity (Critical, Serious, Moderate, Minor), used to sort issues and prioritise tickets. It is **not normative**: neither RAAM nor WCAG 2.x define severity. The scale is RUXAL's own, inspired by Deque's axe-core impact levels; the unstable WCAG 3 draft is not used. See [`docs/gravite.md`](docs/gravite.md).

Tools: **RUXAAM** (mobile, RAAM 1.1), **RUXAWEB** (web), **RUXAPDF** (PDF).

## Statut / Status
Projet en cours de préparation pour publication. / Project being prepared for publication.

## Utilisation / Usage
Ouvrir le fichier HTML de l'outil dans un navigateur. / Open the tool's HTML file in a browser.

RUXAAM 1.23 : **52 critères RAAM** (dont 20 « si présent ») et **3 bonnes pratiques** hors taux, soit 57 éléments. Gravités par défaut des critères RAAM : 12 Critique, 29 Sérieux, 10 Modéré, 1 Mineur.

- **Protocole de test en 4 étapes** : 1. usage standard, 2. agrandissement (texte, puis affichage), 3. lecteur d'écran (3a contenus et structure, 3b composants, formulaires et annonces), 4. navigation alternative (clavier externe, commande vocale ; contrôle de sélection et Switch Access optionnels). Chaque critère est rattaché à l'étape où on le constate le plus facilement. Séquence construite par RUXAAM à partir des pratiques décrites par Apple et Android ; ce n'est pas un protocole officiel. Le détail est dans l'écran Aide de l'outil.
- **Vue « Par étape de test »** : dans un onglet RAAM, la liste peut être rangée par thème ou par étape. Un critère n'apparaît qu'une fois, dans son étape principale. Statuts, taux et exports ne changent pas.
- **Plateforme** : iOS, Android ou multiplateforme, choisie sous le nom de l'audit (un audit = une plateforme). Elle détermine les recommandations « Per platform » et une étiquette supplémentaire des tickets Jira.
- **Contenu des écrans** : en tête d'un onglet RAAM, un interrupteur par écran et par type d'élément (CAPTCHA, image complexe, média, tableau, formulaire), plus un interrupteur « Limite de session » pour toute l'application. Un critère « si présent » ne s'affiche que si un écran contient l'élément ; ailleurs il compte comme NA, sans rien effacer de ce qui a été saisi.
- **Élément concerné** : pour chaque critère non conforme et chaque écran, un champ d'une ligne reçoit la notation `Écran[type "Libellé"] (état)`, expliquée dans l'Aide (« Noter les éléments »). L'export Jira la reprend dans le titre et le corps du ticket.
- **Mémoire des exports Jira** : l'outil retient les critères déjà exportés (pour tout l'audit, avec la sauvegarde) et ne les exporte pas deux fois ; « Tickets Jira — tout réexporter » les reprend tous. Le champ « Ticket Jira » des versions précédentes est retiré.
- **Exports** : aucun fichier vide n'est produit. Sans onglet, sans onglet RAAM, sans critère testé ou sans critère non conforme, un message explique pourquoi l'export n'a pas lieu. À l'import d'une sauvegarde plus ancienne, l'outil signale les critères qui n'existent plus dans cette version.

## Données et génération / Data and build
Chaque outil reste **un seul fichier HTML autonome**, mais ses critères ne s'éditent pas dans le HTML : la source de vérité est dans `data/`.

| Fichier | Contenu | Licence |
|---|---|---|
| `data/criteres-raam.json` | 52 critères officiels du RAAM 1.1 (intitulés du SIP, non modifiés) ; 20 « si présent », chacun rattaché à un déclencheur ; étape de test de chaque critère | CC BY 3.0 LU |
| `data/bonnes-pratiques.json` | 3 bonnes pratiques hors RAAM (hors taux), avec leur étape de test | CC BY 4.0 |
| `data/themes-ruxal.json` | ordre et noms des 7 thèmes RUXAL | CC BY 4.0 |
| `data/textes-ruxal.json` | gravité (non normative, voir `docs/gravite.md`), texte d'impact et consigne de test de chaque critère ; libellés des 6 déclencheurs | CC BY 4.0 |

Après toute modification de `data/`, régénérer l'outil (Python 3, sans dépendance) :

```bash
python3 scripts/build_ruxaam.py
```

Le script valide les données (texte manquant, thème ou gravité inconnus, identifiant en double) puis remplace le bloc compris entre les marqueurs `DEBUT_DONNEES` et `FIN_DONNEES` de `src/ruxaam.html`. Ne pas modifier ce bloc à la main. `python3 scripts/build_ruxaam.py --check` vérifie que le HTML est à jour (code retour 1 sinon), utile avant un commit.

Identifiants stables : `raam-1-2` pour le critère RAAM 1.2, `bp1` pour une bonne pratique. / Stable ids: `raam-1-2` for RAAM criterion 1.2, `bp1` for a best practice. **EN** — edit `data/`, then run the script above to inject the data into the standalone HTML file.

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
```
Les tests ouvrent `src/ruxaam.html` en `file://` et vérifient notamment : nombre de critères et de pastilles d'étape, vues par thème et par étape, « Contenu des écrans », « Élément concerné » et aide à la notation, export Jira selon la plateforme et mémoire des exports, messages d'export sans fichier vide, import d'une sauvegarde 1.21 (migration), absence d'erreur JavaScript.

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
