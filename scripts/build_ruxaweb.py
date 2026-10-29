#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Injecte les données de data/ dans src/ruxaweb.html (audit par observations, outil autonome, un seul fichier).

Le bloc situé entre les marqueurs DEBUT_DONNEES et FIN_DONNEES de src/ruxaweb.html est
remplacé à chaque exécution : ne pas le modifier à la main, modifier les fichiers JSON.

Sources :
  data/criteres-raweb.json       intitulés officiels RAWeb 1.1 (SIP, CC BY 3.0 LU), sélection de l'audit simplifié du SIP
  data/bonnes-pratiques-web.json bonnes pratiques hors RAWeb
  data/themes-ruxal.json         ordre et noms des thèmes RUXAL (communs à toute la famille)
  data/textes-ruxaweb.json       impact, explication, gravité, questions des déclencheurs (textes originaux)
  data/symptomes-ruxaweb.json    points de contrôle et critères proposés pour une observation
  data/axe-raweb.json            correspondance des règles axe-core et Lighthouse vers les critères

Usage :
  python3 scripts/build_ruxaweb.py          régénère src/ruxaweb.html
  python3 scripts/build_ruxaweb.py --check  vérifie que le fichier est à jour (code retour 1 sinon)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'src' / 'ruxaweb.html'
DEBUT = '  // <<< DEBUT_DONNEES : généré par scripts/build_ruxaweb.py depuis data/, ne pas modifier à la main >>>'
FIN = '  // <<< FIN_DONNEES >>>'
GRAVITES = {'critique', 'serieux', 'modere', 'mineur'}  # voir docs/gravite.md
# Liste fermée des déclencheurs des critères « si présent » (questions posées pour chaque page).
DECLENCHEURS = ['captcha', 'image-complexe', 'media-temporel', 'media-non-temporel', 'tableau-donnees', 'cadre',
                'formulaire', 'changement-langue']
# Protocole de test RUXAWEB en 4 étapes (champ etape : étape principale, ou sous-étape 3a / 3b du lecteur d'écran).
ETAPES = {'1': 'Usage standard', '2': 'Code et outils', '3': "Lecteur d'écran", '4': 'Navigation au clavier'}
ETAPES_VALIDES = {'1', '2', '3a', '3b', '4'}
# Liens officiels vers un critère du RAWeb 1.1 (ancres « crit-x-y » du site du SIP).
URL_CRITERE = 'https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-'


def charger(nom):
    return json.loads((ROOT / 'data' / nom).read_text(encoding='utf-8'))


def construire():
    raweb = charger('criteres-raweb.json')['criteres']
    bps = charger('bonnes-pratiques-web.json')['bonnes_pratiques']
    themes = [t['nom'] for t in charger('themes-ruxal.json')['themes']]
    textes = charger('textes-ruxaweb.json')
    erreurs = []
    declencheurs = textes.get('declencheurs', [])
    if [d['id'] for d in declencheurs] != DECLENCHEURS:
        erreurs.append('déclencheurs de textes-ruxaweb.json différents de la liste fermée : ' + ', '.join(DECLENCHEURS))

    criteres = []
    for c in raweb:
        cid = 'raweb-' + c['raweb'].replace('.', '-')
        t = textes['criteres'].get(cid)
        if not t:
            erreurs.append(cid + ' : aucun texte dans textes-ruxaweb.json')
            continue
        criteres.append({
            'id': cid,
            'ref': c['raweb'],
            'theme_ruxal': c['theme_ruxal'],
            'theme_ref': '%d. %s' % (c['theme_raweb_numero'], c['theme_raweb']),
            'niveau': t['gravite'],
            'niveau_wcag': c['niveau'],
            'siPresent': c['statut'] == 'si présent',
            # Critère officiel hors sélection de l'audit simplifié du SIP : évalué, mais exclu du taux.
            'horsSelection': bool(c.get('hors_selection')),
            'declencheur': c.get('declencheur', ''),
            'etape': c.get('etape', ''),
            'libelle': c['intitule'],
            'impact': t['impact'],
            'explication': t['explication'],
        })
    for b in bps:
        t = textes['bonnes_pratiques'].get(b['id'])
        if not t:
            erreurs.append(b['id'] + ' : aucun texte dans textes-ruxaweb.json')
            continue
        criteres.append({
            'id': b['id'],
            'horsRef': True,
            'ref': '',
            'theme_ruxal': b['theme_ruxal'],
            'theme_ref': 'Hors référentiel RAWeb, bonne pratique',
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
    orphelins = (set(textes['criteres']) | set(textes['bonnes_pratiques'])) - set(ids)
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
        for champ in ('libelle', 'impact', 'explication', 'note'):
            if '\u2014' in c.get(champ, '') or '\u2013' in c.get(champ, ''):
                erreurs.append('%s : tiret cadratin ou demi-cadratin dans « %s »' % (c['id'], champ))
    utilises = {c['declencheur'] for c in criteres if c.get('siPresent')}
    if utilises != set(DECLENCHEURS):
        erreurs.append('déclencheurs sans critère : ' + ', '.join(sorted(set(DECLENCHEURS) - utilises)))
    if erreurs:
        sys.exit('Données invalides :\n- ' + '\n- '.join(erreurs))
    return criteres, themes, textes.get('verification_sources', ''), declencheurs


def js(valeur):
    # « </ » fermerait la balise <script> si un texte en contenait un.
    return json.dumps(valeur, ensure_ascii=False).replace('</', '<\\/')


def bloc():
    criteres, themes, verif, declencheurs = construire()
    # Critères WCAG de chaque critère RAWeb (numéros seuls), pour rapprocher une règle axe absente de la table.
    wcag = {c['raweb']: [w.split(' ')[0] for w in c.get('wcag', [])] for c in charger('criteres-raweb.json')['criteres']}
    criteres = [dict(c, wcag=wcag.get(c['ref'], [])) if c.get('ref') else c for c in criteres]
    symptomes = charger('symptomes-ruxaweb.json')
    ids = {c['id'] for c in criteres}
    par_ref = {c['ref']: c['id'] for c in criteres if c.get('ref')}
    erreurs = []
    sortie = []
    for s in symptomes['symptomes']:
        def conv(refs):
            out = []
            for r in refs:
                if r not in par_ref:
                    erreurs.append('%s : critère %s inconnu' % (s['id'], r))
                else:
                    out.append(par_ref[r])
            return out
        bps = [b for b in s.get('bonnes_pratiques', []) if b in ids]
        sortie.append({
            'id': s['id'], 'famille': s['famille'], 'controle': s['controle'], 'symptome': s['symptome'],
            'criteres': conv(s.get('criteres', [])) + bps,
            'mots': s.get('mots', []),
            'selon': [{'element': x['element'], 'criteres': conv(x['criteres']), 'mots': x.get('mots', [])} for x in s.get('selon', [])],
        })
    axe = {}
    for regle, refs in charger('axe-raweb.json')['regles'].items():
        cible = []
        for r in refs:
            if r in ids:
                cible.append(r)
            elif r in par_ref:
                cible.append(par_ref[r])
            else:
                erreurs.append('axe-raweb.json, %s : critère %s inconnu' % (regle, r))
        axe[regle] = cible
    if erreurs:
        sys.exit('Données invalides :\n- ' + '\n- '.join(erreurs))
    j = js
    lignes = [DEBUT, '  var CRITERES = [']
    lignes += ['    ' + j(c) + ',' for c in criteres]
    lignes[-1] = lignes[-1].rstrip(',')
    lignes += ['  ];',
               '  var THEMES_RUXAL = ' + j(themes) + ';',
               '  var DECLENCHEURS = ' + j(declencheurs) + ';',
               '  var FAMILLES = ' + j(symptomes['familles']) + ';',
               '  var SYMPTOMES = ' + j(sortie) + ';',
               '  var AXE_RAWEB = ' + j(axe) + ';',
               '  var URL_CRITERE = ' + j(URL_CRITERE) + ';',
               FIN]
    nb_sel = sum(1 for c in criteres if c.get('horsSelection'))
    nb_ref = sum(1 for c in criteres if not c.get('horsRef')) - nb_sel
    resume = '%d critères RAWeb + %d hors sélection SIP + %d bonnes pratiques, %d points de contrôle, %d règles axe' % (
        nb_ref, nb_sel, len(criteres) - nb_ref - nb_sel, len(sortie), len(axe))
    return '\n'.join(lignes), resume


def main():
    donnees, resume = bloc()
    html = HTML.read_text(encoding='utf-8')
    debut, fin = html.find(DEBUT), html.find(FIN)
    if debut < 0 or fin < debut:
        sys.exit('Marqueurs DEBUT_DONNEES / FIN_DONNEES introuvables dans ' + str(HTML))
    nouveau = html[:debut] + donnees + html[fin + len(FIN):]
    if '--check' in sys.argv:
        if nouveau != html:
            sys.exit('src/ruxaweb.html n\'est pas à jour : lancer python3 scripts/build_ruxaweb.py')
        print('À jour : ' + resume)
        return
    if nouveau != html:
        HTML.write_text(nouveau, encoding='utf-8')
        print('src/ruxaweb.html régénéré : ' + resume)
    else:
        print('Aucun changement : ' + resume)


if __name__ == '__main__':
    main()
