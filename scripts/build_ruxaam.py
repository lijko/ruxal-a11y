#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Injecte les données de data/ dans src/ruxaam.html (outil autonome, un seul fichier).

Le bloc situé entre les marqueurs DEBUT_DONNEES et FIN_DONNEES de src/ruxaam.html est
remplacé à chaque exécution : ne pas le modifier à la main, modifier les fichiers JSON.

Sources :
  data/criteres-raam.json    intitulés officiels RAAM 1.1 (SIP, CC BY 3.0 LU)
  data/bonnes-pratiques.json bonnes pratiques hors RAAM
  data/themes-ruxal.json     ordre et noms des thèmes RUXAL
  data/textes-ruxal.json     impact, explication, gravité, questions des déclencheurs (textes originaux)

Usage :
  python3 scripts/build_ruxaam.py          régénère src/ruxaam.html
  python3 scripts/build_ruxaam.py --check  vérifie que le fichier est à jour (code retour 1 sinon)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'src' / 'ruxaam.html'
DEBUT = '  // <<< DEBUT_DONNEES : généré par scripts/build_ruxaam.py depuis data/, ne pas modifier à la main >>>'
FIN = '  // <<< FIN_DONNEES >>>'
GRAVITES = {'critique', 'serieux', 'modere', 'mineur'}  # voir docs/gravite.md
# Liste fermée des déclencheurs des critères « si présent » (questions posées pour chaque écran).
DECLENCHEURS = ['captcha', 'image-complexe', 'media-temporel', 'tableau-donnees', 'formulaire', 'session']
# Protocole de test RUXAAM en 4 étapes (champ etape : étape principale, ou sous-étape 3a / 3b du lecteur d'écran).
ETAPES = {'1': 'Usage standard', '2': 'Agrandissement', '3': "Lecteur d'écran", '4': 'Navigation alternative'}
ETAPES_VALIDES = {'1', '2', '3a', '3b', '4'}


def charger(nom):
    return json.loads((ROOT / 'data' / nom).read_text(encoding='utf-8'))


def construire():
    raam = charger('criteres-raam.json')['criteres']
    bps = charger('bonnes-pratiques.json')['bonnes_pratiques']
    themes = [t['nom'] for t in charger('themes-ruxal.json')['themes']]
    textes = charger('textes-ruxal.json')
    erreurs = []
    declencheurs = textes.get('declencheurs', [])
    if [d['id'] for d in declencheurs] != DECLENCHEURS:
        erreurs.append('déclencheurs de textes-ruxal.json différents de la liste fermée : ' + ', '.join(DECLENCHEURS))

    criteres = []
    for c in raam:
        cid = 'raam-' + c['raam'].replace('.', '-')
        t = textes['criteres'].get(cid)
        if not t:
            erreurs.append(cid + ' : aucun texte dans textes-ruxal.json')
            continue
        criteres.append({
            'id': cid,
            'raam': c['raam'],
            'theme_ruxal': c['theme_ruxal'],
            'theme_raam': '%d. %s' % (c['theme_raam_numero'], c['theme_raam']),
            'niveau': t['gravite'],
            'niveau_wcag': c['niveau'],
            'siPresent': c['statut'] == 'si présent',
            'declencheur': c.get('declencheur', ''),
            'etape': c.get('etape', ''),
            'libelle': c['intitule'],
            'impact': t['impact'],
            'explication': t['explication'],
        })
    for b in bps:
        t = textes['bonnes_pratiques'].get(b['id'])
        if not t:
            erreurs.append(b['id'] + ' : aucun texte dans textes-ruxal.json')
            continue
        criteres.append({
            'id': b['id'],
            'horsRaam': True,
            'raam': '',
            'theme_ruxal': b['theme_ruxal'],
            'theme_raam': 'Hors référentiel RAAM — bonne pratique',
            'etape': b.get('etape', ''),
            'niveau': t['gravite'],
            'niveau_wcag': '',
            'libelle': b['libelle'],
            'impact': t['impact'],
            'explication': t['explication'],
            'note': t.get('note', ''),
            'sources': [{'t': s['titre'], 'u': s['url']} for s in t.get('sources', [])],
        })

    ids = [c['id'] for c in criteres]
    if len(ids) != len(set(ids)):
        erreurs.append('identifiants en double')
    orphelins = set(textes['criteres']) - set(ids)
    if orphelins:
        erreurs.append('textes sans critère : ' + ', '.join(sorted(orphelins)))
    for c in criteres:
        if c.get('etape') not in ETAPES_VALIDES:
            erreurs.append('%s : étape inconnue « %s » (attendu : %s)' % (c['id'], c.get('etape'), ', '.join(sorted(ETAPES_VALIDES))))
        if c.get('siPresent') and c.get('declencheur') not in DECLENCHEURS:
            erreurs.append('%s : critère « si présent » sans déclencheur valide' % c['id'])
        if not c.get('siPresent') and c.get('declencheur'):
            erreurs.append('%s : déclencheur sur un critère « cœur »' % c['id'])
        if c['theme_ruxal'] not in themes:
            erreurs.append('%s : thème RUXAL inconnu « %s »' % (c['id'], c['theme_ruxal']))
        if c['niveau'] not in GRAVITES:
            erreurs.append('%s : gravité inconnue « %s »' % (c['id'], c['niveau']))
        if not c['impact'] or not c['explication']:
            erreurs.append(c['id'] + ' : impact ou explication vide')
    if erreurs:
        sys.exit('Données invalides :\n- ' + '\n- '.join(erreurs))
    return criteres, themes, textes.get('verification_sources', ''), declencheurs


def js(valeur):
    # « </ » fermerait la balise <script> si un texte en contenait un.
    return json.dumps(valeur, ensure_ascii=False).replace('</', '<\\/')


def bloc(criteres, themes, verif, declencheurs):
    lignes = [DEBUT, '  var CRITERES = [']
    lignes += ['    ' + js(c) + ',' for c in criteres]
    lignes[-1] = lignes[-1].rstrip(',')
    lignes.append('  ];')
    lignes.append('  var THEMES_RUXAL_ORDRE = ' + js(themes) + ';')
    lignes.append('  var DECLENCHEURS = ' + js(declencheurs) + ';')
    # ETAPES : id -> [étape ou sous-étape, libellé de l'étape] ; ETAPES_ORDRE : titres des 4 groupes de la vue par étape.
    etapes = {c['id']: [c['etape'], ETAPES[c['etape'][0]]] for c in criteres}
    lignes.append('  var ETAPES = ' + js(etapes) + ';')
    lignes.append('  var ETAPES_ORDRE = ' + js(['%s · %s' % (n, ETAPES[n]) for n in sorted(ETAPES)]) + ';')
    if verif:
        a, m, j = verif.split('-')
        lignes.append("  var REF_VERIF = '%s/%s/%s';" % (j, m, a))
    lignes.append(FIN)
    return '\n'.join(lignes)


def main():
    criteres, themes, verif, declencheurs = construire()
    html = HTML.read_text(encoding='utf-8')
    debut, fin = html.find(DEBUT), html.find(FIN)
    if debut < 0 or fin < debut:
        sys.exit('Marqueurs DEBUT_DONNEES / FIN_DONNEES introuvables dans ' + str(HTML))
    nouveau = html[:debut] + bloc(criteres, themes, verif, declencheurs) + html[fin + len(FIN):]
    nb_raam = sum(1 for c in criteres if not c.get('horsRaam'))
    resume = '%d critères RAAM (%d « si présent ») + %d bonnes pratiques' % (
        nb_raam, sum(1 for c in criteres if c.get('siPresent')), len(criteres) - nb_raam)
    if '--check' in sys.argv:
        if nouveau != html:
            sys.exit('src/ruxaam.html n\'est pas à jour : lancer python3 scripts/build_ruxaam.py')
        print('À jour : ' + resume)
        return
    if nouveau != html:
        HTML.write_text(nouveau, encoding='utf-8')
        print('src/ruxaam.html régénéré : ' + resume)
    else:
        print('Aucun changement : ' + resume)


if __name__ == '__main__':
    main()
