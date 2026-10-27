#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Injecte les données de data/ dans src/ruxaweb2.html (RUXAWEB 2, audit par observations).

Reprend les critères, textes, thèmes et déclencheurs de RUXAWEB 1 (mêmes contrôles, voir build_ruxaweb.py)
et y ajoute la table symptôme vers critères (data/symptomes-ruxaweb.json) et la correspondance des règles
axe-core et Lighthouse vers les critères (data/axe-raweb.json).

Usage :
  python3 scripts/build_ruxaweb2.py          régénère src/ruxaweb2.html
  python3 scripts/build_ruxaweb2.py --check  vérifie que le fichier est à jour (code retour 1 sinon)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ruxaweb as v1  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'src' / 'ruxaweb2.html'
DEBUT = '  // <<< DEBUT_DONNEES : généré par scripts/build_ruxaweb2.py depuis data/, ne pas modifier à la main >>>'
FIN = '  // <<< FIN_DONNEES >>>'


def bloc():
    criteres, themes, verif, declencheurs = v1.construire()
    # Critères WCAG de chaque critère RAWeb (numéros seuls), pour rapprocher une règle axe absente de la table.
    wcag = {c['raweb']: [w.split(' ')[0] for w in c.get('wcag', [])] for c in v1.charger('criteres-raweb.json')['criteres']}
    criteres = [dict(c, wcag=wcag.get(c['ref'], [])) if c.get('ref') else c for c in criteres]
    symptomes = v1.charger('symptomes-ruxaweb.json')
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
            'selon': [{'element': x['element'], 'criteres': conv(x['criteres'])} for x in s.get('selon', [])],
        })
    axe = {}
    for regle, refs in v1.charger('axe-raweb.json')['regles'].items():
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
    j = v1.js
    lignes = [DEBUT, '  var CRITERES = [']
    lignes += ['    ' + j(c) + ',' for c in criteres]
    lignes[-1] = lignes[-1].rstrip(',')
    lignes += ['  ];',
               '  var THEMES_RUXAL = ' + j(themes) + ';',
               '  var DECLENCHEURS = ' + j(declencheurs) + ';',
               '  var FAMILLES = ' + j(symptomes['familles']) + ';',
               '  var SYMPTOMES = ' + j(sortie) + ';',
               '  var AXE_RAWEB = ' + j(axe) + ';',
               '  var URL_CRITERE = ' + j(v1.URL_CRITERE) + ';',
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
            sys.exit('src/ruxaweb2.html n\'est pas à jour : lancer python3 scripts/build_ruxaweb2.py')
        print('À jour : ' + resume)
        return
    if nouveau != html:
        HTML.write_text(nouveau, encoding='utf-8')
        print('src/ruxaweb2.html régénéré : ' + resume)
    else:
        print('Aucun changement : ' + resume)


if __name__ == '__main__':
    main()
