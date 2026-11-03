#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Ajoute l'intitulé officiel anglais (champ intitule_en) aux critères de data/criteres-raam.json et data/criteres-raweb.json.

Les intitulés viennent des dépôts officiels du SIP (en/json/criteres.json), nettoyés des liens de glossaire comme
les intitulés français. Ils servent aux exports en anglais (tickets Jira) ; l'interface garde les intitulés français.

Usage :
  python3 scripts/intitules_en.py <dossier ReferentielAccessibiliteMobile> <dossier ReferentielAccessibiliteWeb>
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data'


def propre(t):
    t = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', t)
    t = t.replace('`', '').replace(' ', ' ')
    return re.sub(r'\s+', ' ', t).strip()


def titres(depot):
    d = json.loads((Path(depot) / 'en' / 'json' / 'criteres.json').read_text(encoding='utf-8'))
    return {'%s.%s' % (th['number'], c['criterium']['number']): propre(c['criterium']['title'])
            for th in d['topics'] for c in th['criteria']}


def completer(fichier, cle, depot):
    chemin = DATA / fichier
    d = json.loads(chemin.read_text(encoding='utf-8'))
    en = titres(depot)
    for c in d['criteres']:
        c['intitule_en'] = en[str(c[cle])]
    chemin.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(fichier, ':', len(d['criteres']), 'intitulés anglais')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    completer('criteres-raam.json', 'raam', sys.argv[1])
    completer('criteres-raweb.json', 'raweb', sys.argv[2])
