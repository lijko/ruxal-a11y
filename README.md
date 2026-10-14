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

## Données et génération / Data and build
Chaque outil reste **un seul fichier HTML autonome**, mais ses critères ne s'éditent pas dans le HTML : la source de vérité est dans `data/`.

| Fichier | Contenu | Licence |
|---|---|---|
| `data/criteres-raam.json` | 60 critères officiels du RAAM 1.1 (intitulés du SIP, non modifiés) ; 25 « si présent », chacun rattaché à un déclencheur | CC BY 3.0 LU |
| `data/bonnes-pratiques.json` | bonnes pratiques hors RAAM (hors taux) | CC BY 4.0 |
| `data/themes-ruxal.json` | ordre et noms des 7 thèmes RUXAL | CC BY 4.0 |
| `data/textes-ruxal.json` | gravité (non normative, voir `docs/gravite.md`), texte d'impact et consigne de test de chaque critère ; questions des 6 déclencheurs | CC BY 4.0 |

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

## Licences / Licences
| Contenu | Licence |
|---|---|
| Code (`src/`) | EUPL-1.2 |
| Données et documentation (`data/`, `docs/`) | CC BY 4.0 |

Le détail par fichier est dans `REUSE.toml`. Les textes complets sont dans `LICENSES/`.

## Attributions
Voir `NOTICE`. Cet outil n'est ni approuvé ni certifié par le W3C, le SIP, l'OSAPS ou Deque Systems.

## Contribuer / Contributing
Voir `CONTRIBUTING.md`.
