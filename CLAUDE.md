# CLAUDE.md — RUXAL

Contexte et règles pour travailler sur ce dépôt public. Langue de travail : français (code et identifiants en anglais, interface en FR/EN).

## Identité du projet
- **RUXAL (Revue UX Accessibilité)** : famille d'outils HTML autonomes de **pré-diagnostic** d'accessibilité par parcours. Ce n'est **pas** un audit de conformité : l'outil prépare et priorise le travail avant un audit complet.
- Dépôt : `lijko/ruxal-a11y` (https://github.com/lijko/ruxal-a11y).
- Public visé : auditeurs et auditrices, équipes produit, UX designers, institutions.
- Outils : RUXAAM (mobile, RAAM 1.1), RUXAWEB (web, RAWEB), RUXAPDF (PDF, RAPDF).

## Principes non négociables
- Les **critères officiels (RAAM, RAWEB, RAPDF) ne sont jamais modifiés** : ni numéro, ni libellé, ni nombre. On peut ajouter des critères réels manquants, avec la source citée, chacun rattaché à son thème officiel et à son thème RUXAL.
- Les **7 thèmes RUXAL** sont une taxonomie propre, adaptable : Navigation & Structure, Composants Interactifs, Images & Médias, Couleurs & Contrastes, Contenu & Lisibilité, Fondations Techniques, Formulaires. Règle : tout ce qui empêche d'atteindre un élément ou un contenu au clavier relève de « Navigation & Structure ».
- Le **taux de conformité** suit la formule du référentiel (statuts C / NC / NT / NA). Chaque onglet garde son propre taux, jamais fusionné avec un autre.
- La couche **POUR (WCAG) et heuristiques UX** est qualitative, **exclue du taux**, et stockée dans un fichier de données séparé des critères officiels.
- Types d'audit : (1) Audit rapide, (2) Scénario (parcours complexe, référentiel + UX), (3) Fonctionnalité primaire (fermer, retour, étapes, menu, navigation, formulaire, notification).
- Modes clair et sombre, selon le réglage système.
- L'outil lui-même doit être accessible : clavier, contrastes, lecteurs d'écran, zoom.

## Structure
- `src/` : outils (un fichier HTML autonome par outil, sans dépendance externe obligatoire).
- `data/` : critères, thèmes, couche POUR/heuristiques (JSON).
- `docs/` : documentation.

## Licences et attribution
- Code (`src/`) : EUPL-1.2. Données et documentation (`data/`, `docs/`) : CC BY 4.0. Détail dans `REUSE.toml`, textes dans `LICENSES/`.
- Ajouter l'en-tête SPDX à tout nouveau fichier.
- Ne pas recopier le texte intégral de WCAG ni des heuristiques de Nielsen Norman : formulations propres, lien vers la source, attribution dans `NOTICE`.
- **Ne jamais versionner de données confidentielles ni de matériel appartenant à un client ou employeur** (captures, documents internes, tickets, logos), sans accord écrit.

## Exports
- « Exporter liste (CSV) » : une ligne par critère × onglet (statut agrégé, commentaire, preuves).
- Notation : élément = `Écran[type "Libellé"]` (état éventuel entre parenthèses) ; flux = `Écran -> Écran`.

## Contribution
- Réponses et documentation concises, directes, honnêtes sur les limites.
- Petits commits, messages en français ou en anglais, une pull request par évolution.
- Avant fusion : test manuel au clavier et avec un lecteur d'écran sur les écrans modifiés.
