#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Contrôle de data/symptomes-ruxaweb.json (aucune dépendance).

Vérifie que chaque critère cité existe dans la sélection RUXAWEB, que chaque critère de la sélection
est atteignable par au moins un point de contrôle, que les critères « hors sélection » ne sont pas dans
la sélection, et que les identifiants, familles et bonnes pratiques sont cohérents.
Lancement :
  python3 tests/test_symptomes_ruxaweb.py
Code retour 0 si tout passe, 1 sinon.
"""
import json
import pathlib
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / 'data'


def charger(nom):
    return json.loads((DATA / nom).read_text(encoding='utf-8'))


def main():
    selection = {c['raweb'] for c in charger('criteres-raweb.json')['criteres']}
    bps = {b['id'] for b in charger('bonnes-pratiques-web.json')['bonnes_pratiques']}
    table = charger('symptomes-ruxaweb.json')
    familles = {f['id'] for f in table['familles']}
    erreurs = []
    couverts = set()
    ids = set()

    for s in table['symptomes']:
        sid = s['id']
        if sid in ids:
            erreurs.append(sid + ' : identifiant en double')
        ids.add(sid)
        if s['famille'] not in familles:
            erreurs.append(sid + ' : famille inconnue ' + s['famille'])
        refs = list(s.get('criteres', []))
        for cas in s.get('selon', []):
            refs += cas['criteres']
        for r in refs:
            if r not in selection:
                erreurs.append(sid + ' : critère ' + r + ' absent de la sélection')
            couverts.add(r)
        for r in s.get('hors_selection', []):
            if r in selection:
                erreurs.append(sid + ' : critère ' + r + ' marqué hors sélection mais présent dans la sélection')
        for b in s.get('bonnes_pratiques', []):
            if b not in bps:
                erreurs.append(sid + ' : bonne pratique inconnue ' + b)
        if not refs and not s.get('hors_selection') and not s.get('bonnes_pratiques'):
            erreurs.append(sid + ' : aucun critère ni bonne pratique')
        texte = json.dumps(s, ensure_ascii=False)
        if '–' in texte or '—' in texte:
            erreurs.append(sid + ' : tiret cadratin ou demi-cadratin')

    manquants = sorted(selection - couverts, key=lambda x: [int(n) for n in x.split('.')])
    for r in manquants:
        erreurs.append('critère ' + r + ' atteint par aucun point de contrôle')

    print('%d points de contrôle, %d/%d critères couverts' % (len(ids), len(couverts & selection), len(selection)))
    for e in erreurs:
        print('ÉCHEC', e)
    return 1 if erreurs else 0


if __name__ == '__main__':
    sys.exit(main())
