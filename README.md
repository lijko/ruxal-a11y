# RUXAL — Revue UX Accessibilité

**FR** — RUXAL est une famille d'outils HTML autonomes qui aident à **préparer et prioriser un audit d'accessibilité**, avant l'audit complet. Chaque outil croise deux regards sur ce que l'on examine (écran, fonctionnalité ou parcours) :

- **les critères officiels du référentiel** (RAAM 1.1 pour le mobile, RAWEB pour le web, RAPDF pour le PDF), évalués critère par critère (conforme, non conforme, non testé, non applicable), qui donnent un **taux de conformité** par onglet ;
- **une lecture UX qualitative** : les quatre principes **POUR** de WCAG (Perceptible, Utilisable, Compréhensible, Robuste) et les **heuristiques d'utilisabilité**, qui servent à repérer les problèmes que les critères seuls ne montrent pas. Cette couche est **exclue du taux**.

Trois types d'audit : l'**audit rapide** (critères du référentiel), la **fonctionnalité primaire** (fermer, retour, menu, navigation, formulaire, notification) et le **scénario** (parcours complexe, critères + lecture UX). Les résultats s'exportent en CSV.

RUXAL n'est **pas un audit de conformité** et ne produit aucune déclaration d'accessibilité : c'est un outil de pré-diagnostic, qui complète l'audit réalisé par un expert.

Outils : **RUXAAM** (mobile, RAAM 1.1), **RUXAWEB** (web), **RUXAPDF** (PDF).

**EN** — RUXAL is a family of standalone HTML tools that help **prepare and prioritise an accessibility audit**, ahead of a full audit. Each tool looks at what you are reviewing (a screen, a feature or a journey) in two ways:

- **the official criteria of the standard** (RAAM 1.1 for mobile, RAWEB for web, RAPDF for PDF), assessed one by one (compliant, non-compliant, not tested, not applicable), which produce a **conformity rate** per tab;
- **a qualitative UX reading**: the four **POUR** principles of WCAG (Perceivable, Operable, Understandable, Robust) and **usability heuristics**, used to spot issues that criteria alone do not reveal. This layer is **excluded from the rate**.

Three audit types: **quick audit** (standard criteria), **primary feature** (close, back, menu, navigation, form, notification) and **scenario** (complex journey, criteria + UX reading). Results can be exported as CSV.

RUXAL is **not a compliance audit** and produces no accessibility statement: it is a pre-diagnosis tool that complements an expert's audit.

Tools: **RUXAAM** (mobile, RAAM 1.1), **RUXAWEB** (web), **RUXAPDF** (PDF).

## Statut / Status
Projet en cours de préparation pour publication. / Project being prepared for publication.

## Utilisation / Usage
Ouvrir le fichier HTML de l'outil dans un navigateur. / Open the tool's HTML file in a browser.

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
Voir `NOTICE`. Cet outil n'est ni approuvé ni certifié par le W3C, la DINUM, le SIP ou l'OSAPS.

## Contribuer / Contributing
Voir `CONTRIBUTING.md`.
