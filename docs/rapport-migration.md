<!--
SPDX-FileCopyrightText: 2026 Bertrand Kempf
SPDX-License-Identifier: CC-BY-4.0
-->
# Rapport de migration : RUXAAM 1.17

> **Mise à jour (version 1.18)** : les gravités citées dans ce rapport sont celles de l'ancienne échelle à trois niveaux (bloquant, majeur, mineur). L'outil utilise désormais une échelle à quatre niveaux, non normative et inspirée de Deque : voir [`gravite.md`](gravite.md), qui donne la correspondance et les gravités à confirmer.

Passage des anciens critères reformulés de `src/ruxaam.html` (identifiants `c01`…`c62`) aux données de `data/` :
59 critères officiels du RAAM 1.1 (`data/criteres-raam.json`, intitulés du SIP non modifiés, CC BY 3.0 LU),
3 bonnes pratiques hors RAAM (`data/bonnes-pratiques.json`) et les textes originaux RUXAL (`data/textes-ruxal.json`, CC BY 4.0).
L'outil reste un seul fichier HTML, régénéré par `scripts/build_ruxaam.py` (voir README).

## Règle appliquée
Un ancien texte (impact ou explication) n'est repris que si **le numéro RAAM est le même** et que **le sens correspond à l'intitulé officiel**.
Sinon, le texte est nouveau. La gravité des anciens critères est conservée quand la correspondance est sûre ; sinon elle est proposée et marquée `gravite_a_confirmer: true` dans `data/textes-ruxal.json`.
L'origine de chaque texte est tracée dans le champ `origine` de ce fichier.

## Bilan
- 43 critères : impact et explication repris.
- 1 critère : explication reprise, impact nouveau.
- 15 critères : textes entièrement nouveaux.
- 3 bonnes pratiques (bp1, bp2, bp3) : textes, gravités et sources repris tels quels.
- 16 gravités à confirmer : 15 sur des critères aux textes nouveaux, plus RAAM 9.6.
- Identifiants : `raam-x-y` et `bpN`. Les sessions enregistrées avec les anciens identifiants ne sont pas reprises (accepté) ; testé : leurs réponses sont ignorées sans erreur.

## Textes réutilisés (43)
Gravité conservée à l'identique pour tous.

| Critère | Ancien id | Gravité | Remarque |
|---|---|---|---|
| RAAM 1.1 | c02 | mineur |  |
| RAAM 1.2 | c01 | bloquant |  |
| RAAM 1.3 | c03 | majeur |  |
| RAAM 1.4 (si présent) | c04 | majeur |  |
| RAAM 1.5 | c05 | bloquant |  |
| RAAM 1.6 (si présent) | c06 | mineur |  |
| RAAM 2.1 | c08 | majeur | préfixe de l'impact corrigé (références WCAG/EN 301 549) |
| RAAM 2.2 | c09 | bloquant |  |
| RAAM 2.3 | c57 | majeur |  |
| RAAM 3.7 | c12 | bloquant | préfixe de l'impact corrigé (références WCAG/EN 301 549) |
| RAAM 3.12 | c16 | majeur |  |
| RAAM 4.5 | c19 | majeur |  |
| RAAM 5.2 | c22 | bloquant | préfixe de l'impact corrigé (références WCAG/EN 301 549) |
| RAAM 5.4 | c58 | majeur |  |
| RAAM 5.5 | c45 | majeur | préfixe de l'impact corrigé (références WCAG/EN 301 549) |
| RAAM 6.1 | c23 | majeur |  |
| RAAM 6.2 | c54 | majeur |  |
| RAAM 7.1 | c25 | majeur | préfixe de l'impact corrigé (références WCAG/EN 301 549) |
| RAAM 7.2 | c59 | mineur |  |
| RAAM 8.1 | c28 | majeur |  |
| RAAM 8.2 | c56 | majeur |  |
| RAAM 8.5 | c27 | bloquant |  |
| RAAM 8.6 | c29 | majeur |  |
| RAAM 9.3 | c33 | majeur |  |
| RAAM 9.5 | c37 | majeur |  |
| RAAM 9.6 | c34 | mineur |  |
| RAAM 9.7 | c60 | majeur |  |
| RAAM 9.8 | c61 | majeur |  |
| RAAM 9.9 | c38 | majeur | préfixe de l'impact corrigé (références WCAG/EN 301 549) |
| RAAM 9.12 | c46 | mineur |  |
| RAAM 10.1 | c39 | majeur |  |
| RAAM 10.2 | c55 | majeur |  |
| RAAM 10.3 | c40 | bloquant |  |
| RAAM 11.1 | c42 | majeur |  |
| RAAM 11.2 | c62 | majeur |  |
| RAAM 11.7 | c43 | bloquant |  |
| RAAM 11.8 | c44 | majeur |  |
| RAAM 11.9 | c47 | majeur |  |
| RAAM 11.10 | c48 | bloquant |  |
| RAAM 11.11 | c49 | bloquant | préfixe de l'impact corrigé (références WCAG/EN 301 549) |
| RAAM 11.12 | c50 | majeur |  |
| RAAM 11.13 | c51 | majeur |  |
| RAAM 11.15 | c52 | bloquant | préfixe de l'impact corrigé (références WCAG/EN 301 549) |

## Reprise partielle (1)
- RAAM 9.1 : explication reprise de c32, impact réécrit (l'intitulé officiel exige une étiquette **visible**, l'ancien impact ne le disait pas).

## Textes nouveaux (15)
Aucun ancien critère ne portait ce numéro, ou l'ancien texte ne correspondait pas à l'intitulé officiel.

| Critère | Gravité proposée |
|---|---|
| RAAM 1.8 | mineur |
| RAAM 3.5 (si présent) | bloquant |
| RAAM 3.9 (si présent) | majeur |
| RAAM 3.13 | majeur |
| RAAM 4.3 (si présent) | mineur |
| RAAM 5.1 | bloquant |
| RAAM 5.3 | majeur |
| RAAM 8.3 (si présent) | mineur |
| RAAM 8.4 (si présent) | mineur |
| RAAM 8.7 | mineur |
| RAAM 9.2 | bloquant |
| RAAM 9.4 (si présent) | mineur |
| RAAM 9.10 | majeur |
| RAAM 9.11 | majeur |
| RAAM 12.3 | bloquant |

## Gravités à confirmer (16)
Proposées pendant la migration, à relire. Repères : bloquant = empêche d'accomplir la tâche ; majeur = la rend difficile ; mineur = gêne.

| Critère | WCAG (niveau) | Gravité proposée |
|---|---|---|
| RAAM 1.8 | 1.4.5 (AA) | **mineur** |
| RAAM 3.5 (si présent) | 1.2.3 (A) | **bloquant** |
| RAAM 3.9 (si présent) | 1.2.5 (AA) | **majeur** |
| RAAM 3.13 | 2.1.1 / 2.1.2 (A) | **majeur** |
| RAAM 4.3 (si présent) | 1.3.1 (A) | **mineur** |
| RAAM 5.1 | 2.4.4 / 2.5.3 / 4.1.2 (A) | **bloquant** |
| RAAM 5.3 | 3.2.1 / 3.2.2 (A) | **majeur** |
| RAAM 8.3 (si présent) | 1.4.1 (A) | **mineur** |
| RAAM 8.4 (si présent) | 1.4.1 (A) | **mineur** |
| RAAM 8.7 | 1.4.13 (AA) | **mineur** |
| RAAM 9.2 | 1.3.1 / 3.3.2 / 4.1.2 (A) | **bloquant** |
| RAAM 9.4 (si présent) | 3.3.2 (A) | **mineur** |
| RAAM 9.10 | 3.3.3 (AA) | **majeur** |
| RAAM 9.11 | 3.3.4 (AA) | **majeur** |
| RAAM 12.3 | EN 301 549 seul (A) | **bloquant** |
| RAAM 9.6 | 1.3.1 / 3.3.2 (A) | **mineur** (ancienne gravité ; « majeur » proposé : des choix Oui/Non annoncés sans leur question rendent le champ impossible à remplir seul au lecteur d'écran) |

## Anciens critères non repris (15)
Leur numéro ou leur sens ne correspondait à aucun des 59 intitulés officiels retenus (voir `docs/comparaison-raam-ruxaam.csv`). Leurs textes ne sont pas réutilisés.

- c07 (ancien n° 1.7) : Pour chaque image porteuse d'information ayant une description détaillée, cette description est pertinente.
- c10 (ancien n° 3.1) : Chaque média temporel pré-enregistré dispose, si nécessaire, d'une transcription textuelle ou d'une audiodescription.
- c11 (ancien n° 3.2) : Pour chaque média temporel pré-enregistré ayant une transcription ou une audiodescription, celle-ci est pertinente.
- c13 (ancien n° 3.8) : Pour chaque média temporel synchronisé ayant des sous-titres, ces sous-titres sont pertinents.
- c17 (ancien n° 3.13) : La consultation de chaque média temporel est, si nécessaire, contrôlable au clavier et par tout dispositif de pointage.
- c18 (ancien n° 4.5) : Pour chaque tableau de données, les en-têtes de colonne et de ligne sont correctement déclarés.
- c20 (ancien n° 5.1) : Chaque lien est explicite.
- c21 (ancien n° 5.1) : Dans chaque écran, chaque lien a un intitulé.
- c26 (ancien n° 7.1) : La structure de l'écran est cohérente.
- c30 (ancien n° 8.6) : Cette règle sur la forme, la taille ou la position est implémentée de façon pertinente.
- c31 (ancien n° 8.7) : Les contenus additionnels apparaissant via les styles uniquement peuvent être rendus visibles au clavier et par tout dispositif de pointage.
- c35 (ancien n° 9.6) : Chaque regroupement de champs de même nature a une légende.
- c36 (ancien n° 9.6) : Chaque légende associée à un regroupement de champs est pertinente.
- c41 (ancien n° 8.7) : Les contenus additionnels apparaissant au survol, à la prise de focus ou à l'activation d'un composant sont, si nécessaire, atteignables au clavier.
- c53 (ancien n° 11.16) : Pour chaque application intégrant une fonctionnalité de répétition de touche, le délai avant répétition et l'intervalle entre les répétitions peuvent être réglés à au moins 2 secondes.

## Relecture contre la méthodologie RAAM (13 octobre 2026)
Chaque consigne « Comment vérifier » a été comparée à la méthodologie de test officielle du critère (`fr/json/methodologies.json` du dépôt du SIP). Les intitulés ne changent pas. La méthodologie n'est pas reproduite dans le dépôt : les consignes restent des textes originaux RUXAL, de même sens.

- 51 consignes retouchées, 8 inchangées (1.6, 2.3, 3.5, 5.4, 11.2, 11.7, 11.12, 11.13). Le champ `origine` de `data/textes-ruxal.json` indique « revu selon la méthodologie RAAM 1.1 ».
- Écarts de sens corrigés :
  - **6.2** : l'ancienne consigne testait les titres, qui relèvent du 7.1. Le RAAM vérifie que le rôle annoncé d'un élément non interactif correspond à sa nature (un paragraphe annoncé « bouton »).
  - **9.6** : vérifier que le groupe est **identifié** (nom annoncé sur le premier champ), pas seulement regroupé.
  - **10.1 et 10.2** : l'ordre doit être cohérent, il n'a pas à suivre strictement l'ordre visuel. On reteste aussi après une mise à jour du contenu.
  - **11.11** : il s'agit d'actions **simultanées** (deux touches, la voix et le toucher). Les gestes à plusieurs doigts relèvent du 11.10.
  - **5.2** : tester avec le lecteur d'écran **et** un clavier externe, pas l'un ou l'autre.
  - **8.5, 8.4 et 10.3** : test au clavier externe, en vérifiant que le focus du système est préservé.
  - **7.2** : le lecteur d'écran doit annoncer « liste ».
  - **4.3** : le titre doit être annoncé ; le RAAM n'exige pas qu'il soit visible.
  - **3.13** : il s'agit de la présence des commandes ; leur usage au clavier relève de 5.1 et 5.2.
  - **9.9** : le message d'erreur est annoncé à la prise de focus sur le champ.
  - **9.10** : le message donne un exemple concret de valeur attendue.
- Conditions alternatives ajoutées : 1.2 (information donnée par un élément voisin), 1.5 (code SMS, e-mail), 3.12 (son de 3 secondes au plus), 11.1 (avertissement avec 20 secondes pour prolonger), 11.8 (masquer ou afficher sans mouvement ; une pause pendant l'appui ne suffit pas), 11.15 (alternative biométrique d'un autre type).
- Impacts réalignés sur ces consignes : 6.2, 9.6, 10.1, 10.2, 11.11.
- Vérification de non-reprise : la plus longue suite de mots identique à la méthodologie fait 8 mots, et reprend des termes de l'intitulé (« forme, taille ou position »).

## Version 1.23 (16 octobre 2026)
- **Contenu des écrans** : panneau d'interrupteurs (écran × CAPTCHA, image complexe, média, tableau, formulaire ; « Limite de session » pour toute l'application). Un critère « si présent » non applicable sur un écran y compte comme NA et y affiche « Absent » ; un critère absent de tous les écrans est masqué de la liste, des raccourcis et des thèmes. Rien n'est effacé : réactiver un interrupteur retrouve les statuts et commentaires. Migration : une sauvegarde sans réglage garde visibles les critères « si présent » déjà évalués, et la limite de session est déduite du 11.2.
- **Champ « Ticket Jira » retiré** (saisie, rappel, exclusion à l'export). Les clés des anciennes sauvegardes ne masquent plus aucun ticket.
- **Élément concerné** : champ d'une ligne par critère non conforme et par écran, notation `Écran[type "Libellé"] (état)` ; repris dans le titre et le corps des tickets Jira (`|` remplacé par `/`) et dans l'export JSON. Section d'aide « Noter les éléments », avec retour au champ d'origine.
- **Mémoire des exports Jira** : critères déjà exportés retenus pour tout l'audit (`exportesJira`, inclus dans la sauvegarde, vidé à la réinitialisation), marqués seulement une fois le fichier enregistré ; messages « N ticket(s) déjà exporté(s), M nouveau(x) » ; menu « Tickets Jira : tout réexporter ». Limite documentée dans l'Aide : un critère déjà exporté qui devient non conforme sur un autre écran n'est pas réexporté automatiquement.
- La 1.22 publiée est conservée telle quelle (protocole de test, encarts d'étape, pastilles 3a / 3b, table ETAPES générée).
- **Tests** : 72 contrôles.

## Version 1.22 (15 octobre 2026)
- **Sélection** : 52 critères RAAM (dont 20 « si présent ») et 3 bonnes pratiques, soit 57 éléments. Critères retirés de la sélection : 1.8, 4.3, 7.2, 8.3, 8.4, 9.4 et 9.12. Le déclencheur « Lien coloré dans un texte » disparaît ; le déclencheur « Limite de session » est ajouté pour le 11.2, désormais « si présent ». Gravités RAAM : 12 Critique, 29 Sérieux, 10 Modéré, 1 Mineur.
- **8.7** : impact et consigne de test reformulés (fermeture sans déplacer le focus, maintien à l'affichage, survol possible au pointeur).
- **Protocole de test en 4 étapes** : champ `etape` dans les données (1, 2, 3a, 3b, 4), pastille d'étape sur chaque critère, vue « Par étape de test » (23 / 1 / 24 / 7 éléments), encart de consigne en tête de chaque étape, section « Protocole de test » dans l'Aide. Séquence construite par RUXAAM à partir des pratiques décrites par Apple et Android ; ce n'est pas un protocole officiel.
- **Plateforme** (iOS, Android, multiplateforme) : recommandations « Per platform » et étiquette des tickets Jira.
- **Exports** : messages explicites, aucun fichier vide ; import d'une ancienne sauvegarde avec signalement des critères qui n'existent plus.
- **Notes par écran** retirées de l'onglet (les notes générales restent) ; l'export JSON ne contient plus que le nom des écrans.
- **Tests** : `tests/test_ruxaam.py` (Playwright), 46 contrôles.

## Revue de cohérence avec le RAAM (14 octobre 2026, version 1.21)
1. **Retrait du RAAM 3.1** (transcription d'un contenu seulement audio, ajouté le 13 octobre) : retiré des données, des textes, de `gravite.md` et de la sélection. Résultat : **59 critères RAAM, dont 24 « si présent », plus 3 bonnes pratiques**.
2. **Consignes de test** :
   - **8.2** : les paliers officiels remplacent « au maximum ». Sur iOS, « Police plus grande » au palier 190 % ; sur Android, la taille de police au maximum pour approcher 200 % ; avant Android 14, on la combine avec la taille d'affichage.
   - **11.7** : ajout des seuils admis, 3 flashs par seconde au plus ou une surface cumulée inférieure à 21 824 pixels.
3. **Licences** :
   - `src/ruxaam.html` est déclaré sous `EUPL-1.2 AND LicenseRef-CC-BY-3.0-LU AND MIT` (code RUXAL, critères RAAM, jsPDF), dans son en-tête SPDX et dans `REUSE.toml`, avec les trois titulaires de droits ;
   - ajout de `LICENSES/MIT.txt` ;
   - NOTICE précise que les intitulés, niveaux et références WCAG / EN 301 549 sont reproduits sans modification dans `data/criteres-raam.json` et `src/ruxaam.html`, et que les références WCAG sont reprises telles que publiées dans le RAAM.
4. **Attribution visible** : un pied de page dans l'outil (critères du SIP sous CC BY 3.0 LU, modifications RUXAL, code EUPL-1.2), et une ligne d'attribution en tête du PDF du Référentiel.
5. Documentation : README (59 critères, dossier `scripts/`), mentions de `CLAUDE.md` remplacées (fichier supprimé du dépôt).

## Déclencheurs des critères « si présent » (14 octobre 2026, version 1.20)

> **Mise à jour (14 octobre 2026)** : les questions « Cet écran contient-il… ? » en tête d'onglet ont été **retirées**, jugées trop compliquées à l'usage, avec les règles qui en dépendaient (passage automatique en NA, correction des réponses contredites). Restent : le champ `declencheur` dans les données, la pastille « Si présent · <déclencheur> » et la mention dans les consignes. Les critères non applicables se mettent en NA à la main. Ajout d'un bouton « Haut de page », qui apparaît après défilement, remonte en haut et place le focus sur le titre de l'outil.
- 25 critères « si présent », 35 « cœur ». Chaque critère « si présent » est rattaché à un déclencheur, dans une liste fermée de six (champ `declencheur` de `data/criteres-raam.json`) :
  - **CAPTCHA** : 1.4, 1.5 ;
  - **image complexe** : 1.6 ;
  - **média temporel ou son qui se lance seul** : 3.1, 3.5, 3.7, 3.9, 3.12, 3.13 ;
  - **tableau de données** : 4.3, 4.5 ;
  - **lien coloré dans un texte** (lien repérable seulement par sa couleur, ni souligné ni en gras) : 8.3, 8.4 ;
  - **formulaire** (au moins un champ de saisie) : 9.1 à 9.12.
- 16 critères passent de « cœur » à « si présent » : 1.5, 3.7, 3.12, 3.13, 4.5, 9.1 à 9.3 et 9.5 à 9.12. Cela règle l'incohérence relevée au contrôle global.
- La question du déclencheur média mentionne aussi « un son qui se lance seul », pour le 3.12 : un son automatique peut exister sans lecteur audio ou vidéo à l'écran.
- Dans l'outil, en tête de chaque onglet RAAM, une question par déclencheur et par écran :
  - « Non » passe les critères liés en NA pour cet écran, y compris ceux déjà évalués, et un message le signale ;
  - « Oui » après un « Non » les remet en NT ;
  - un premier « Oui » ne change rien.

  Les critères restent visibles, avec la pastille « Si présent · <déclencheur> ».
- Le script de génération refuse tout déclencheur hors liste, tout critère « si présent » sans déclencheur, et tout déclencheur sur un critère « cœur ».
- Cohérence : si un critère lié reçoit C, NC ou NT sur un écran qui avait répondu « Non », la réponse passe à « Oui » pour cet écran, et les autres critères liés reviennent à NT (message à l'appui). Mettre un critère en NA ne change aucune réponse. La même règle s'applique à l'ouverture de l'outil et à l'import d'une sauvegarde, pour corriger les données enregistrées avant elle.
- Un thème dont tous les critères sont NA sur tous les écrans (typiquement Formulaires, quand chaque écran répond « Non » à la question sur les champs de saisie) disparaît des raccourcis et du sommaire. Il reste dans la liste, replié, avec la mention « non applicable sur tous les écrans ».

## Contrôle global (13 octobre 2026, version 1.19)

### Corrigé
- **Ajout du RAAM 3.1** (transcription d'un contenu seulement audio), en « si présent », gravité Critique : 60 critères RAAM, dont 9 « si présent », plus 3 bonnes pratiques.
- **Intitulés officiels** : 39 intitulés avaient perdu l'apostrophe typographique (’) du référentiel, remplacée par une apostrophe droite. Ils sont rétablis à l'identique ; un contrôle automatique compare désormais chaque intitulé, niveau et référence WCAG / EN 301 549 au dépôt officiel (aucun écart restant).
- **Comparabilité avec le SIP** : l'outil affirmait que son taux était « comparable au SIP » et que la liste CSV était « à coller dans le fichier SIP ». L'audit rapide du SIP repose sur le RAWEB : il sert ici de modèle (échantillon, sélection de critères essentiels), pas de base de comparaison. Les textes de l'outil le disent maintenant.
- **Libellé « SIP »** affiché à côté du nom des onglets (nom interne de l'approche) : remplacé par « RAAM ».
- **Marquage « si présent »** : 1.4 et 1.6 n'avaient pas la mention « Ne concerne que… » dans leur consigne.
- **Gravités** : acceptées comme base de discussion (voir `gravite.md`).
- **Accessibilité de l'outil lui-même** :
  - langue de la page non déclarée (`lang="fr"` ajouté) et absence de titre de niveau 1 ;
  - après chaque clic, le focus retombait au début de la page : au clavier ou au lecteur d'écran, chaque statut saisi renvoyait en haut. Le focus est maintenant conservé, et placé sur le titre quand la vue change ;
  - boutons de statut : état sélectionné indiqué seulement par la couleur, sans nom de groupe. Ils annoncent désormais leur sens (« NC, non conforme »), leur état (`aria-pressed`) et le critère et l'écran concernés ; même chose pour les réponses POUR/UX ;
  - commentaires par écran sans étiquette : étiquette ajoutée ;
  - thèmes et critères exposés comme titres (niveaux 3 et 4) pour naviguer au lecteur d'écran.
- Testé dans le navigateur : clavier réel (Tab, Entrée), mode clair et sombre, largeur 375 px sans défilement horizontal, taux, exports CSV, Jira, JSON et PDF, aucune erreur de console.

### Restant à discuter
- **Cohérence du « si présent »** (réglé en 1.20, voir ci-dessus) : le statut ne suivait pas une règle unique. 1.4 (CAPTCHA) est « si présent » mais 1.5 (CAPTCHA) est « cœur » ; 3.1, 3.5 et 3.9 (médias) sont « si présent » mais 3.7, 3.12 et 3.13 (médias) sont « cœur » ; 4.3 (tableau) est « si présent » mais 4.5 (tableau) est « cœur ». Proposition : « si présent » = tout critère qui ne porte que sur un type de contenu absent de beaucoup d'écrans (CAPTCHA, médias, tableaux, liens dans un texte).
- **Couche POUR / heuristiques** : il est prévu qu'elle soit stockée dans un fichier de données séparé ; elle est encore écrite dans `src/ruxaam.html`.
- **NOTICE** indique que les intitulés RAAM sont reproduits « dans src/ruxaam.html » ; ils le sont aussi dans `data/criteres-raam.json`.
- **Non testé** : VoiceOver et TalkBack réels, zoom navigateur à 200 % et 400 %, contrastes de toutes les couleurs de l'interface.

## Changements dans l'outil
- Critères injectés depuis `data/` entre les marqueurs `DEBUT_DONNEES` / `FIN_DONNEES` ; le script valide les données (texte manquant, thème ou gravité inconnus, doublon).
- Ordre des thèmes RUXAL lu dans `data/themes-ruxal.json` ; la table de correspondance des noms de thèmes pour l'export Jira, devenue inutile, est supprimée.
- Les 8 critères « si présent » restent affichés, avec une pastille « Si présent » (audit et page Référentiel) et la mention dans l'export PDF.
- Version de l'outil : 1.16 → 1.17.

## Contrôles effectués
- `python3 scripts/build_ruxaam.py --check` : à jour, 59 critères RAAM (8 « si présent ») + 3 bonnes pratiques.
- Navigateur (mode clair et sombre) : aucune erreur de console ; page Référentiel = 62 fiches, 7 thèmes dans l'ordre, 8 pastilles « Si présent », 3 « Hors RAAM ».
- Audit rapide sur 3 écrans : tout C, 8 critères en NA, 2 critères RAAM NC (2.2 sur tous les écrans, 5.2 sur un seul), bp1 NC → taux 96 % (49/51), bp1 hors taux. Export liste CSV = 62 lignes + en-tête ; export Jira = 3 tickets ; export JSON valide.
- Non fait : test manuel au clavier et au lecteur d'écran (exigé avant fusion, voir CONTRIBUTING.md).

## Limites
- Les textes nouveaux et les gravités proposées n'ont pas été relus par un auditeur ou une auditrice.
- Les références WCAG des impacts suivent `data/criteres-raam.json` ; pour 5.5 et 12.3, le RAAM ne cite que l'EN 301 549.
