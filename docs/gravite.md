<!--
SPDX-FileCopyrightText: 2026 Bertrand Kempf
SPDX-License-Identifier: CC-BY-4.0
-->
# Gravité des non-conformités

## Avertissement
**La gravité n'est pas normative.** Ni le RAAM 1.1 ni WCAG 2.x ne définissent de gravité : un critère y est conforme ou non conforme. Les niveaux A et AA de WCAG indiquent à quel point un critère est exigible, pas à quel point un défaut gêne.

RUXAL ajoute une gravité pour **trier** les non-conformités et fixer la **priorité** des tickets Jira. Cette gravité :
- est **propre à RUXAL**, comme les thèmes RUXAL ;
- s'inspire de l'**échelle d'impact de Deque** (axe-core), sans en être une reprise officielle ;
- est une **valeur par défaut par critère**, pensée pour le cas où le défaut touche un élément important de l'écran. L'impact réel dépend de l'écran et de l'élément : un bouton sans nom bloque sur « Payer », gêne sur un bouton de partage secondaire ;
- **n'entre jamais dans le taux de conformité**.

RUXAL n'est ni approuvé ni certifié par Deque ni par le W3C.

## Échelle
Les quatre niveaux reprennent ceux d'axe-core (*critical*, *serious*, *moderate*, *minor*). Les définitions ci-dessous sont formulées pour RUXAL ; la source fait foi.

| Niveau | Repère | Priorité Jira |
|---|---|---|
| **Critique** | Empêche, pour au moins un groupe d'utilisateurs, d'accéder à une fonction ou à un contenu essentiel, sans contournement ; ou met la personne en danger (effets de flash). | Highest |
| **Sérieux** | Barrière forte : rend la tâche très difficile, et peut la bloquer selon le contexte. | High |
| **Modéré** | Difficulté réelle, mais un contournement existe et l'essentiel reste accessible. | Medium |
| **Mineur** | Gêne ou ralentissement, sans empêcher la tâche. | Low |

Pour choisir, trois questions :
1. La tâche reste-t-elle possible ?
2. Pour qui (lecteur d'écran, clavier ou contacteur, basse vision, surdité, troubles cognitifs, motricité) ?
3. Existe-t-il un contournement raisonnable, sans aide extérieure ?

## Et WCAG 3 ?
Le brouillon de travail de WCAG 3.0 (W3C, version du 10 septembre 2026) étudie, dans sa partie *Reporting* marquée *Exploratory*, quatre étiquettes de gravité pour les exigences essentielles : dommage physique (*Physical Harm*), risque financier, médical, juridique ou de sécurité (*Risk*), barrière qui empêche de continuer (*Barrier*) et friction qui gêne (*Friction*). Le W3C précise que ce document est un travail en cours, qui changera. **RUXAL ne l'utilise pas** ; il pourra être réexaminé quand WCAG 3 sera stable. Les notions de dommage et de risque sont déjà prises en compte dans les repères ci-dessus (flash : Critique ; formulaires à conséquences financières ou juridiques, RAAM 9.11 : Sérieux).

## Gravités par défaut
Passage de l'ancienne échelle à trois niveaux (version 1.17) : bloquant → Critique, majeur → Sérieux, mineur → Modéré ou Mineur selon le critère. Toute valeur qui s'écarte de cette correspondance directe est **à confirmer** (32 sur 62). Les données sont dans `data/textes-ruxal.json` (champs `gravite`, `gravite_v1_17`, `gravite_a_confirmer`).

Écarts motivés :
- **2.2 contraste du texte, 3.5 alternative d'une vidéo, 8.5 focus visible, 9.1 étiquette visible** : Critique → Sérieux. Le défaut gêne fortement sans bloquer dans la plupart des cas (contraste juste sous le seuil, bande son disponible, lecteur d'écran qui garde son propre focus, champ remplissable).
- **6.2, 7.1, 8.6, 9.7, 9.8, 9.10, 10.1, 11.12** : Sérieux → Modéré. Un contournement existe (explorer l'écran, recommencer la saisie, annuler l'action).
- **9.6 champs de même nature** : Mineur → Sérieux. Des choix « Oui / Non » annoncés sans leur question rendent le champ impossible à remplir seul au lecteur d'écran.
- **bp1 taille des zones tactiles** : Sérieux → Modéré (recommandation des plateformes, critère AAA en WCAG 2.1).

| Critère | Gravité | Ancienne (v1.17) | À confirmer |
|---|---|---|---|
| RAAM 1.1 | Mineur | mineur | oui |
| RAAM 1.2 | Critique | bloquant |  |
| RAAM 1.3 | Sérieux | majeur |  |
| RAAM 1.4 | Sérieux | majeur |  |
| RAAM 1.5 | Critique | bloquant |  |
| RAAM 1.6 | Modéré | mineur | oui |
| RAAM 1.8 | Modéré | mineur | oui |
| RAAM 2.1 | Sérieux | majeur |  |
| RAAM 2.2 | Sérieux | bloquant | oui |
| RAAM 2.3 | Sérieux | majeur |  |
| RAAM 3.5 | Sérieux | bloquant | oui |
| RAAM 3.7 | Critique | bloquant |  |
| RAAM 3.9 | Sérieux | majeur | oui |
| RAAM 3.12 | Sérieux | majeur |  |
| RAAM 3.13 | Sérieux | majeur | oui |
| RAAM 4.3 | Mineur | mineur | oui |
| RAAM 4.5 | Sérieux | majeur |  |
| RAAM 5.1 | Critique | bloquant | oui |
| RAAM 5.2 | Critique | bloquant |  |
| RAAM 5.3 | Sérieux | majeur | oui |
| RAAM 5.4 | Sérieux | majeur |  |
| RAAM 5.5 | Sérieux | majeur |  |
| RAAM 6.1 | Sérieux | majeur |  |
| RAAM 6.2 | Modéré | majeur | oui |
| RAAM 7.1 | Modéré | majeur | oui |
| RAAM 7.2 | Mineur | mineur | oui |
| RAAM 8.1 | Sérieux | majeur |  |
| RAAM 8.2 | Sérieux | majeur |  |
| RAAM 8.3 | Modéré | mineur | oui |
| RAAM 8.4 | Modéré | mineur | oui |
| RAAM 8.5 | Sérieux | bloquant | oui |
| RAAM 8.6 | Modéré | majeur | oui |
| RAAM 8.7 | Modéré | mineur | oui |
| RAAM 9.1 | Sérieux | bloquant | oui |
| RAAM 9.2 | Critique | bloquant | oui |
| RAAM 9.3 | Sérieux | majeur |  |
| RAAM 9.4 | Mineur | mineur | oui |
| RAAM 9.5 | Sérieux | majeur |  |
| RAAM 9.6 | Sérieux | mineur | oui |
| RAAM 9.7 | Modéré | majeur | oui |
| RAAM 9.8 | Modéré | majeur | oui |
| RAAM 9.9 | Sérieux | majeur |  |
| RAAM 9.10 | Modéré | majeur | oui |
| RAAM 9.11 | Sérieux | majeur | oui |
| RAAM 9.12 | Mineur | mineur | oui |
| RAAM 10.1 | Modéré | majeur | oui |
| RAAM 10.2 | Sérieux | majeur |  |
| RAAM 10.3 | Critique | bloquant |  |
| RAAM 11.1 | Sérieux | majeur |  |
| RAAM 11.2 | Sérieux | majeur |  |
| RAAM 11.7 | Critique | bloquant |  |
| RAAM 11.8 | Sérieux | majeur |  |
| RAAM 11.9 | Sérieux | majeur |  |
| RAAM 11.10 | Critique | bloquant |  |
| RAAM 11.11 | Critique | bloquant |  |
| RAAM 11.12 | Modéré | majeur | oui |
| RAAM 11.13 | Sérieux | majeur |  |
| RAAM 11.15 | Critique | bloquant |  |
| RAAM 12.3 | Critique | bloquant | oui |
| bp1 | Modéré | majeur | oui |
| bp2 | Sérieux | majeur |  |
| bp3 | Modéré | mineur | oui |

## Sources
- Deque, axe-core — *Issue impact* : https://github.com/dequelabs/axe-core/blob/develop/doc/issue_impact.md
- W3C, *WCAG 3.0* (Working Draft) : https://www.w3.org/TR/wcag-3.0/
- W3C, *Understanding Conformance* (WCAG 2) : https://www.w3.org/WAI/WCAG21/Understanding/conformance
