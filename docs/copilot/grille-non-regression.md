# Grille de non-régression des agents Copilot

À repasser après **chaque modification** d'une consigne, avant de la publier. Une conversation neuve par cas, la note collée telle quelle. Un écart sur la colonne « Attendu » est une régression : corriger la consigne avant de la publier.

Les critères attendus sont ceux de RUXAWEB (agent Observation -> RUXAWEB). L'agent Observation -> RAWeb doit donner les mêmes critères en tête, avec leur intitulé officiel ; il peut en ajouter sous « Also check ».

## Agent [A11Y] Observation -> RUXAWEB

| # | Note à coller | Attendu |
|---|---|---|
| 1 | page Login : la case à cocher "Don't ask again on this computer", redessinée par le site, a un contour trop pâle par rapport au fond. | `Écran : Login` puis une ligne, élément `[checkbox "Don't ask again on this computer"]`, critère **3.3** (jamais 3.2) |
| 2 | page Login : la case à cocher "Don't ask again on this computer" (case native du navigateur) est peu contrastée. | **Aucune ligne** : sous « To clarify: », question sur le cas particulier (apparence par défaut du navigateur) |
| 3 | Pied de page : texte gris clair sur fond blanc, difficile à lire. | Une ligne, élément `Footer`, critère **3.2** |
| 4 | page Cart : le bouton Pay est une div cliquable, annoncée comme du texte, impossible à atteindre au clavier. | Une ligne, élément `[button "Pay"]`, critères **7.1, 7.3** |
| 5 | Le focus clavier n'est pas visible dans le menu principal. | Une ligne, élément `Main navigation`, critère **10.7**, sans ligne « Écran : » |
| 6 | Formulaire Contact : le champ Email n'a pas d'étiquette, seulement un placeholder qui disparaît à la saisie. | Une ligne, élément `Contact form[field "Email"]`, critère **11.1** |
| 7 | Les liens "En savoir plus" de la page d'accueil sont tous identiques hors contexte. | Une ligne, élément `"En savoir plus" link`, critère **6.1** |
| 8 | Modale de connexion : Échap ne la ferme pas et à la fermeture le focus part en haut de la page. | **Deux lignes** (deux défauts) : **BP2** et **BP3** (12.8 accepté en plus pour la seconde) |
| 9 | Après envoi du formulaire, le message d'erreur "Mot de passe incorrect" s'affiche mais n'est pas lu par le lecteur d'écran. | Une ligne, critère **11.10** en tête (7.5 accepté en plus) |
| 10 | Le carrousel de la page d'accueil défile tout seul, sans bouton pause. | Une ligne, critère **13.8** |
| 11 | Le champ Email n'a pas d'autocomplete. | **Aucune ligne** : hors RUXAWEB, renvoi vers l'agent Observation -> RAWeb (qui doit répondre **11.13**) |
| 12 | Le formulaire n'est pas accessible. | **Aucune ligne** : une question sous « To clarify: » |
| 13 | Cas 1 suivi de « en français » | Observation et explications en français ; « Écran : », « Criteria: » et les numéros inchangés |
| 14 | Page Accueil : les titres sont bien hiérarchisés. | **Aucune ligne** : une observation conforme ne donne pas de ligne (le C se pose dans la grille) |

**À vérifier sur chaque réponse**
- Le bloc de lignes est un bloc de code, en premier, jamais omis.
- Lignes au format `élément | observation | critères` (ou `observation | critères` sans élément), sans statut en tête.
- Observations en anglais (sauf cas 13), sans citations ni liens vers le fichier.
- Critères en numéros seuls dans les lignes, uniquement parmi les 59 de RUXAWEB et BP1 à BP3.
- Coller la réponse entière dans RUXAWEB (vue Observation, « Coller des observations », puis « Importer les observations ») : autant de pistes que de lignes, aucune piste créée par les explications.

## Agent [A11Y] Observation -> RAWeb

Passer les cas 1, 3, 4, 11 et 12.
- Mêmes critères en tête que ci-dessus (11.13 pour le cas 11).
- Chaque intitulé recopié du fichier, mot pour mot. Vérifier au moins un intitulé par réponse dans `raweb-1.1-criteria.txt` : un intitulé inventé est une régression. Un intitulé introuvable doit être remplacé par le numéro seul, signalé sous « To clarify: ».

## Agent [A11Y] JIRA Task

Passer les cas 1 et 4, en précisant l'application (par exemple « application Phoenix, site web »).
- Titre : `[A11Y] | Phoenix | Colors & contrast | Login[checkbox "Don't ask again on this computer"]: ...` (cas 1), `Interactive components` (cas 4).
- Rubriques en titre 1, dans l'ordre : Flow(s) / Screen(s) / Element(s) in concern, Actual behavior / Impact, Expected behavior, Recommendations, Reference.
- Reference : `RAWeb 1.1, Criterion 3.3: <intitulé officiel>` puis le lien `...#crit-3-3` ; intitulé vérifié dans le fichier.
- Puis « Suggested priority: » et « Suggested tags: » (design pour le cas 1, code pour le cas 4).

Cas sans contexte : coller seulement « Le cadre de focus n'est pas assez épais ni assez contrasté. »
- Critères choisis malgré tout : **10.7 et 3.3**, avec leur intitulé, jamais `<X.Y>` ni `{Criterion X.Y}`. Aucun lien vers le fichier de critères dans Reference.
- Application, écran et élément manquants écrits `{Application}`, `{Screen}`, `{Element}` (jamais un emplacement vide ni un élément inventé), repris sous « To clarify: » avec l'hypothèse « site web ».
- « Suggested tags: » `design` ou `design, code`, jamais « both ».
