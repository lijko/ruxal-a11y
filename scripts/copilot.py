#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Génère les fichiers de connaissances des agents Copilot (docs/copilot/) à partir de data/.

- criteres-raam-raweb.txt : intitulés officiels EN et FR, thème RUXAL et lien de chaque critère (agent Tickets A11Y).
- points-de-controle-ruxaweb.txt : les points de contrôle de RUXAWEB, leurs types d'élément et leurs critères
  (agent Observations RUXAWEB, qui convertit des notes au format du collage).
Les consignes des deux agents (consigne-*.txt) sont écrites à la main dans le même dossier.

Usage : python3 scripts/copilot.py            régénère les deux fichiers
        python3 scripts/copilot.py --check    vérifie qu'ils sont à jour (code retour 1 sinon)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, SORTIE = ROOT / 'data', ROOT / 'docs' / 'copilot'
URL = {'raam': 'https://accessibilite.public.lu/en/raam1.1/referentiel-technique.html#criterion-',
       'raweb': 'https://accessibilite.public.lu/en/raweb1.1/criteres.html#crit-'}


def charger(nom):
    return json.loads((DATA / nom).read_text(encoding='utf-8'))


def tri(n):
    return [int(x) for x in str(n).split('.')]


def criteres():
    l = ['Official criteria titles of RAAM 1.1 and RAWeb 1.1 (Service information et presse, Luxembourg, CC BY 3.0 LU),',
         'taken from the official repositories github.com/accessibility-luxembourg.',
         'Each criterion: reference, official English title (EN), official French title (FR), RUXAL theme for the ticket title, link.',
         'Copy the titles unchanged in the Reference section, never translate or rephrase them.',
         'This list covers the criteria of the RUXAL quick audits. For any other criterion, the full referentials are on accessibilite.public.lu.', '']
    for cle, lab in (('raam', 'RAAM 1.1'), ('raweb', 'RAWeb 1.1')):
        cs = charger('criteres-%s.json' % cle)['criteres']
        l.append('== %s (%d criteria) ==' % (lab, len(cs)))
        for c in sorted(cs, key=lambda c: tri(c[cle])):
            n = str(c[cle])
            l += ['%s, Criterion %s' % (lab, n), 'EN: ' + c['intitule_en'], 'FR: ' + c['intitule'],
                  'Theme: ' + c['theme_ruxal'], URL[cle] + n.replace('.', '-'), '']
    return '\n'.join(l)


def points():
    d = charger('symptomes-ruxaweb.json')
    en = {c['raweb']: c['intitule_en'] for c in charger('criteres-raweb.json')['criteres']}
    fam = {f['id']: f['libelle'] for f in d['familles']}
    ref = lambda ns: ', '.join('%s (%s)' % (n, en.get(n, '?')) for n in sorted(ns, key=tri))
    l = ['RUXAWEB checkpoints (points de contrôle). Text by Bertrand Kempf, CC BY 4.0.',
         'Copy the checkpoint name exactly as written after "Checkpoint:" (in French), in the 4th field of each line.',
         'If the checkpoint lists element types, add the type in parentheses, written exactly as below, e.g. Présence d\'un nom (lien).',
         'The RAWeb criteria are given for information only: never write them in the line, the tool deduces them from the checkpoint.', '']
    for f in d['familles']:
        l.append('== %s ==' % f['libelle'])
        for s in [x for x in d['symptomes'] if x['famille'] == f['id']]:
            l += ['Checkpoint: ' + s['controle'], 'Symptom: ' + s['symptome']]
            if s.get('selon'):
                l.append('Element types:')
                l += ['- (%s): RAWeb %s' % (x['element'], ref(x['criteres'])) for x in s['selon']]
            if s.get('criteres'):
                l.append('RAWeb criteria: ' + ref(s['criteres']))
            if s.get('bonnes_pratiques'):
                l.append('Good practices: ' + ', '.join(s['bonnes_pratiques']))
            l.append('')
    return '\n'.join(l)


def main():
    fichiers = {'criteres-raam-raweb.txt': criteres(), 'points-de-controle-ruxaweb.txt': points()}
    for nom, t in fichiers.items():
        if '—' in t or '–' in t:
            sys.exit(nom + ' : tiret long ou demi-cadratin interdit')
    if '--check' in sys.argv:
        vieux = [n for n, t in fichiers.items() if not (SORTIE / n).exists() or (SORTIE / n).read_text(encoding='utf-8') != t]
        if vieux:
            sys.exit('À régénérer (python3 scripts/copilot.py) : ' + ', '.join(vieux))
        print('À jour : ' + ', '.join(fichiers))
        return
    SORTIE.mkdir(parents=True, exist_ok=True)
    for nom, t in fichiers.items():
        (SORTIE / nom).write_text(t, encoding='utf-8')
        print('Écrit : docs/copilot/%s (%d caractères)' % (nom, len(t)))


if __name__ == '__main__':
    main()
