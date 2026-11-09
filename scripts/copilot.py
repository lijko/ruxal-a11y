#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Génère les fichiers de connaissances des agents Copilot (docs/copilot/) à partir de data/.

- criteres-raam-raweb.txt : intitulés officiels EN et FR, thème RUXAL et lien de chaque critère (référence).
- points-de-controle-ruxaweb.txt : les points de contrôle de RUXAWEB, leurs types d'élément et leurs critères
  (référence ; facultatif comme connaissance de l'agent Observations).
- consigne-observations-ruxaweb.txt : consigne de l'agent « [A11Y] Observation -> RUXAWEB », à partir de
  modele-consigne-observations.txt (écrit à la main), liste des points de contrôle tirée de data/ (symptome_court si présent).

Fichiers écrits à la main, vérifiés seulement : consigne-observation-raweb.txt (« [A11Y] Observation -> RAWeb »),
consigne-ticket.txt (« [A11Y] JIRA Task ») et raweb-1.1-criteria.txt (connaissance des deux, tirée des dépôts du SIP).
Vérifications : 8 000 caractères au plus par consigne, aucun tiret long, et blocs partagés identiques mot pour mot
d'une consigne à l'autre (CHOOSING RAWEB CRITERIA, ELEMENT NOTATION, SPECIAL CASES).

Usage : python3 scripts/copilot.py            régénère les fichiers
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


LIMITE_INSTRUCTIONS = 8000  # champ Instructions d'Agent Builder (Microsoft 365 Copilot)


def consigne_observations():
    # Consigne complète, liste des points de contrôle comprise : l'agent n'a besoin d'aucun fichier de connaissances.
    d = charger('symptomes-ruxaweb.json')
    lignes = []
    for f in d['familles']:
        for s in [x for x in d['symptomes'] if x['famille'] == f['id']]:
            t = '- ' + s['controle'] + ' : ' + s.get('symptome_court', s['symptome'])
            if s.get('selon'):
                t += ' [' + ', '.join(x['element'] for x in s['selon']) + ']'
            lignes.append(t)
    modele = (SORTIE / 'modele-consigne-observations.txt').read_text(encoding='utf-8')
    t = modele.replace('{{POINTS}}', '\n'.join(lignes))
    if len(t) > LIMITE_INSTRUCTIONS:
        sys.exit('consigne-observations-ruxaweb.txt : %d caractères, au-delà de la limite de %d' % (len(t), LIMITE_INSTRUCTIONS))
    return t


CONSIGNES = ['consigne-observations-ruxaweb.txt', 'consigne-observation-raweb.txt', 'consigne-ticket.txt']
BLOCS = ['CHOOSING RAWEB CRITERIA', 'ELEMENT NOTATION', 'SPECIAL CASES']


def bloc(t, titre):
    i = t.find('\n' + titre + '\n')
    return None if i < 0 else t[i + 1:].split('\n\n')[0]


def verifier(textes):
    # Chaque bloc partagé doit être identique dans toutes les consignes qui le contiennent.
    for titre in BLOCS:
        vus = {n: bloc(t, titre) for n, t in textes.items() if bloc(t, titre) is not None}
        if len(set(vus.values())) > 1:
            sys.exit('Bloc « %s » différent selon les consignes : %s' % (titre, ', '.join(vus)))
    for n, t in textes.items():
        if len(t) > LIMITE_INSTRUCTIONS:
            sys.exit('%s : %d caractères, au-delà de la limite de %d' % (n, len(t), LIMITE_INSTRUCTIONS))


def main():
    fichiers = {'criteres-raam-raweb.txt': criteres(), 'points-de-controle-ruxaweb.txt': points(),
                'consigne-observations-ruxaweb.txt': consigne_observations()}
    manuels = {n: (SORTIE / n).read_text(encoding='utf-8') for n in CONSIGNES + ['raweb-1.1-criteria.txt'] if n not in fichiers}
    verifier({n: t for n, t in dict(fichiers, **manuels).items() if n in CONSIGNES})
    for nom, t in manuels.items():
        if '—' in t or '–' in t:
            sys.exit(nom + ' : tiret long ou demi-cadratin interdit')
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
