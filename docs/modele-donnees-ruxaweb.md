# Modèle de données de RUXAWEB

Un seul objet `state`, enregistré dans le navigateur et dans les sauvegardes JSON (`v: 2`).
L'état d'interface passager (fiche ouverte, filtre de la grille, confirmation en attente, case qui garde le focus) vit à part, dans `ui`, et n'est jamais enregistré.

## Projet (`state`)

| Champ | Rôle |
|---|---|
| `v` | version du format (2) |
| `auditNom`, `support` | nom du projet, `desktop` ou `mobile-web` |
| `onglets` | les onglets (audits simples et scénarios) |
| `fonctions`, `obsF` | fonctions primaires du projet et leurs observations, valables dans tous les onglets |
| `compteur` | numéro d'ordre de la dernière observation (champ `n`), qui décide de ce qu'un retest annule |
| `exportesJira` | observations déjà exportées en tickets, clé `idOnglet:idObservation` |
| `vue`, `ongletId`, `ecranId`, `etape`, `fonctionId`, `theming`, `parcoursOuvert` | position de travail, reprise à la réouverture |

## Onglet

`id`, `nom`, `type` (`rapide` ou `scenario`), `ecrans`, `obs`, `valide`, et selon le cas `fonctionsEcrans` (écrans où chaque fonction primaire apparaît), `candidats` (pistes axe, Lighthouse ou collage), `heuristiques` (lecture POUR/UX d'un scénario).

## Écran

`id`, `nom`, `contenus` (contenus présents : formulaire, captcha...), `etapes` (étapes de test faites sur cet écran).

## Observation

| Champ | Rôle |
|---|---|
| `id`, `n` | identifiant stable, numéro d'ordre |
| `ecran` | écran où elle a été faite |
| `partage` | `{ecrans: [...]}` : autres écrans où elle vaut, ou `null` |
| `etape` | étape de test, ou `grille` pour un statut posé depuis la grille |
| `tag` | `c`, `nc`, `na`, ou `nt` pour un retest |
| `criteres` | critères concernés (vide : note libre, sans effet sur les statuts) |
| `texte`, `attendu`, `point`, `elementNom`, `vers`, `source` | contenu, attendu, point de contrôle, élément, transition (scénario), origine (axe, Lighthouse, collage) |

## Règles

- **Rien n'est stocké en double** : le statut d'une case, celui de l'onglet et les taux sont toujours recalculés à partir des observations.
- **Le pire statut l'emporte** : NC, puis NT, puis C ; NA seulement si non applicable partout.
- **Retest** : un `nt` sur un écran et un critère annule toutes les observations plus anciennes de ce critère sur cet écran. Une observation retestée sur tous ses écrans ne sort plus dans l'export Jira.
- **Statut posé dans la grille** : une observation `etape: "grille"` sans texte pour C et NA, avec sa phrase pour NC. « Tous les écrans » avec un NC donne une seule observation partagée, donc un seul ticket.
- **Anciennes sauvegardes** : les 1.x sont converties (`migrerV1`), les 2.x antérieures normalisées (`normaliser`), au chargement comme à l'ouverture d'un fichier.
