#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Tests de bout en bout de src/ruxaweb.html (RUXAWEB 2, audit par observations ; Playwright, Chromium).

Installation (une fois) :
  python3 -m pip install playwright openpyxl
  python3 -m playwright install chromium
Lancement :
  python3 tests/test_ruxaweb.py
Code retour 0 si tout passe, 1 sinon.
"""
import csv
import io
import json
import pathlib
import sys
import tempfile

import openpyxl
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = (ROOT / 'src' / 'ruxaweb.html').as_uri()
resultats = []


def verifier(nom, condition, detail=''):
    resultats.append(bool(condition))
    print(('OK    ' if condition else 'ÉCHEC ') + nom + ('' if condition else ' , ' + str(detail)))


def aller_audit(page):
    """Vue Observation de l'onglet en cours, depuis n'importe quelle vue (onglet courant dans la ligne des onglets)."""
    page.click('#onglet-nav .onglet-tab[aria-current="page"]')


def statut(page, ecran, crit):
    """Statut d'un critère sur un écran (par index), lu dans la grille."""
    aller_audit(page)
    page.click('[data-action="vue"][data-vue="grille"]')
    ligne = page.locator('tr', has=page.locator('[data-action="critere"][data-id="%s"]' % crit))
    return ligne.locator('td.statut').nth(ecran).locator('.pastille').inner_text().split('\n')[0].replace(' !', '').strip()


def _symptomes():
    import re as _re
    html = (ROOT / 'src' / 'ruxaweb.html').read_text(encoding='utf-8')
    return {x['id']: x for x in json.loads(_re.search(r'var SYMPTOMES = (\[.*?\]);\n', html, _re.S).group(1))}


SYMPTOMES = _symptomes()


def chercher(page, point=None, element=None, crit=None):
    # Recherche du formulaire : une ligne par critère. Un point de contrôle (et son type) donne ses critères, ajoutés un à un.
    if crit:
        crits = [crit]
    else:
        sy = SYMPTOMES[point]
        crits = list(sy['criteres']) + (list(sy['selon'][element]['criteres']) if element is not None else [])
    for c in crits:
        page.evaluate("document.getElementById('det-ajout').open = true")
        page.fill('#obs-ajout', page.locator('#liste-criteres option[data-crit="%s"]' % c).first.get_attribute('value'))
        page.wait_for_timeout(50)


def observer(page, texte, point=None, element=None, partage=None, crit=None):
    aller_audit(page)
    page.fill('#obs-texte', texte)
    if point:
        chercher(page, point, element)
    if crit:
        chercher(page, crit=crit)
    if partage:
        nom, quels = partage
        if nom:
            page.fill('#obs-partage-nom', nom)
        cases = page.locator('[data-ecran-partage]').all()
        for i, cb in enumerate(cases):
            if quels is None or i in quels:
                cb.check()
    page.click('[data-action="enregistrer-nouvelle"]')


def aller_etape(page, etape):
    """Étape du protocole, par la liste des étapes du panneau."""
    aller_audit(page)
    page.click('#liste-etapes [data-etape="%s"]' % etape)


def ecran(page, i):
    aller_audit(page)
    page.locator('.ecrans [data-action="ecran"]').nth(i).click()


def telecharger(page, action):
    with page.expect_download() as d:
        page.click('#btn-menu')
        page.click('[data-action="%s"]' % action)
    chemin = pathlib.Path(tempfile.mkdtemp()) / d.value.suggested_filename
    d.value.save_as(chemin)
    return chemin


def main():
    with sync_playwright() as p:
        nav = p.chromium.launch()
        page = nav.new_page(viewport={'width': 1360, 'height': 950}, accept_downloads=True)
        erreurs = []
        page.on('pageerror', lambda e: erreurs.append(str(e)))
        page.goto(URL)
        verifier('Colonnes latérales : barres de défilement fines', page.evaluate("getComputedStyle(document.getElementById('panneau-etapes')).scrollbarWidth") == 'thin')
        verifier('En-tête : version de l\'outil affichée depuis la constante', page.inner_text('#version') == page.evaluate('RUXAWEB.version'), page.inner_text('#version'))
        h1 = page.locator('h1').first; h1.evaluate('h => { h.setAttribute("tabindex", "-1"); h.focus(); }')
        verifier('Titre focalisé par programme : pas d\'anneau de focus', h1.evaluate('h => getComputedStyle(h).outlineStyle') == 'none')
        verifier('Ouverture : page Projet', page.locator('h1').inner_text().startswith('Projet A11Y') and page.locator('#t-nouveau').count() == 1 and page.locator('#t-fonctions').count() == 1)
        verifier('Panneau des étapes présent, déplié sur le tableau de bord, titre masqué', page.locator('#panneau-etapes .liste-etapes li').count() >= 9 and page.locator('#liste-etapes').is_visible() and 'Étapes' in page.locator('#panneau-etapes-titre').inner_text() and 'sr' in (page.get_attribute('#panneau-etapes-titre', 'class') or ''))
        txt = page.content().lower()
        verifier('Aucune mention de Claude', 'claude' not in txt and 'anthropic' not in txt)

        page.fill('#audit-nom', 'Boutique test')
        page.locator('#audit-nom').blur()
        page.click('[data-action="nouvel-onglet"]')
        verifier('Nouvel onglet : 3 écrans par défaut', page.locator('[data-ecran-nom]').count() == 3)
        verifier('Projet A11Y : titre de la page', page.title().startswith('Projet A11Y - Boutique test') or 'Projet A11Y - Boutique test' in page.title(), page.title())
        verifier('Projet A11Y : préfixe et nom du projet', 'Projet A11Y -' in page.inner_text('.barre') and page.get_attribute('#audit-nom', 'placeholder').startswith('Nom du projet'))
        verifier('Modules : Audit complet affiché à venir, non sélectionnable', page.locator('input[name="onglet-type"][value="complet"][disabled]').count() == 1)
        page.click('[data-action="ajout-ecran"]')
        page.click('[data-action="ajout-ecran"]')
        verifier('Audit simple : 5 écrans au plus', page.locator('[data-ecran-nom]').count() == 5 and page.locator('[data-action="ajout-ecran"]').count() == 0 and '5 écrans au plus' in page.inner_text('main'))
        for _ in range(2):
            page.locator('[data-action="suppr-ecran"]').last.click()
            page.locator('[data-action="suppr-ecran"]').last.click()
        verifier('Audit simple : retour à 3 écrans', page.locator('[data-ecran-nom]').count() == 3)
        # Écran 1 : formulaire présent ; les autres sans formulaire.
        page.click('[data-action="contenu"][data-d="formulaire"] >> nth=0')
        sw = page.locator('[data-action="contenu"][data-d="formulaire"]').first
        verifier('Contenu des écrans : interrupteur activé', sw.get_attribute('role') == 'switch' and sw.get_attribute('aria-checked') == 'true')
        page.click('[data-action="vue"][data-vue="audit"] >> nth=-1')
        verifier('Audit : formulaire d\'observation', page.locator('#form-obs').count() == 1)
        # Panneau des étapes : la liste seule, à partir de « Avant », toujours affichée ; on change d'étape en cliquant dessus.
        verifier('Panneau des étapes : la liste seule, toujours affichée', page.locator('#liste-etapes').is_visible() and page.locator('#panneau-etapes .phase').first.text_content().strip() == 'Avant' and page.locator('#panneau-etapes .points, #panneau-etapes [data-action="etapes-bascule"]').count() == 0)
        verifier('Aide : étape Tour à vide en cours', 'Tour à vide' in page.locator('#liste-etapes [aria-current="step"]').inner_text())
        page.click('#liste-etapes [data-etape="1"]')
        verifier('Liste des étapes : clic sur l\'étape 1', 'Usage standard' in page.locator('#liste-etapes [aria-current="step"]').inner_text())
        page.click('#liste-etapes [data-etape="vide"]')
        verifier('Liste des étapes : retour au tour à vide', 'Tour à vide' in page.locator('#liste-etapes [aria-current="step"]').inner_text())
        # Menu de gauche : stylo « Modifier les écrans » sur le titre de la liste ; « Ce que contient l'écran » dans la ligne de l'écran.
        stylo = page.locator('.ecrans .titre-liste [data-vue="preparer"]')
        verifier('Écrans : stylo sur le titre de la liste, libellé et bulle', stylo.count() == 1 and stylo.get_attribute('aria-label') == 'Modifier les écrans' and stylo.get_attribute('data-bulle') == 'Modifier les écrans')
        centres = page.evaluate("""Array.prototype.map.call(document.querySelectorAll('.btn-icone'), function(b){ var r = b.getBoundingClientRect(), i = b.querySelector('svg').getBoundingClientRect();
          return Math.round(Math.abs((i.left + i.right) / 2 - (r.left + r.right) / 2) + Math.abs((i.top + i.bottom) / 2 - (r.top + r.bottom) / 2)); })""")
        verifier('Boutons icône : icône centrée dans le bouton (étapes, stylo)', len(centres) == 2 and max(centres) == 0, centres)
        verifier('Écrans : plus de liens sous la liste', page.locator('.ecrans [data-action="configurer"]').count() == 0)
        verifier('Ligne de l\'écran : « Ce que contient l\'écran » en lien, avec le nom et le badge', page.locator('.tete-ecran > span:first-child .ref-btn[data-action="configurer"]').inner_text().strip() == 'Ce que contient l\'écran')

        page.click('[data-action="vue"][data-vue="grille"]')
        groupes = page.locator('tr.theme').all_inner_texts()
        verifier('Grille : thématiques officielles par défaut', groupes[0].startswith('1. Images') and groupes[-1].startswith('Bonnes pratiques'), groupes[:2])
        page.click('[data-action="theming"][data-v="ruxal"]')
        verifier('Grille : thèmes RUXAL au choix', page.locator('tr.theme').first.inner_text() == 'Navigation & structure')
        page.click('[data-action="theming"][data-v="officiel"]')
        verifier('Configurateur : 11.1 NA sans formulaire', statut(page, 1, 'raweb-11-1') == 'NA')
        verifier('Configurateur : 11.1 NT avec formulaire', statut(page, 0, 'raweb-11-1') == 'NT')

        # Partout #nc : NC sur les écrans cochés.
        observer(page, 'Menu principal : focus invisible.', point='focus-invisible', partage=('Menu principal', None))
        verifier('Élément répété, #nc : NC sur les 3 écrans', [statut(page, i, 'raweb-10-7') for i in range(3)] == ['NC', 'NC', 'NC'])
        vu = page.locator('[data-action="ecran"] .petit').first.inner_text()
        lu = page.evaluate("Array.from(document.querySelectorAll('[data-action=\"ecran\"] .petit .sr')).map(function(x){ return x.textContent; }).join(' / ')")
        verifier('Compteur du menu : « N NC » affiché, critères non conformes lus en clair', ' NC' in vu and 'non conforme' in lu, vu + ' | ' + lu)
        # Une observation décrit un défaut : pas de choix de résultat dans le formulaire (C dans la grille, NA par le contenu de l'écran).
        aller_audit(page)
        verifier('Observation : pas de boutons C / NC / NA', page.locator('#form-obs [data-action="tag"]').count() == 0)
        # Sans écran coché, l'observation reste propre à l'écran ; sur un écran sans formulaire, le critère reste NA.
        observer(page, 'Étiquette du champ e-mail absente.', point='etiquette')
        verifier('Sans autre écran coché : 11.1 NC sur cet écran seulement', [statut(page, i, 'raweb-11-1') for i in range(3)] == ['NC', 'NA', 'NA'])
        observer(page, 'Erreur non restituée.', point='erreur-saisie', partage=(None, None))
        verifier('Aussi sur, sans nom : 11.10 NA là où le formulaire est absent', [statut(page, i, 'raweb-11-10') for i in range(3)] == ['NC', 'NA', 'NA'])
        observer(page, 'Menu : état ouvert non annoncé.', point='role-etat', partage=('Menu', [0]))
        verifier('Aussi sur un seul écran : 7.1 NC sur les deux, NT sur le troisième', [statut(page, i, 'raweb-7-1') for i in range(3)] == ['NC', 'NC', 'NT'])
        aller_audit(page)
        verifier('Éléments répétés : liste unique à gauche', 'éléments répétés' in page.locator('nav.ecrans').inner_text().lower() and 'Menu principal' in page.locator('nav.ecrans').inner_text())

        # Noms d'élément : casse, accents et espaces ne créent pas un nouvel élément.
        ecran(page, 1)
        observer(page, 'Lien du menu sans nom.', point='nom-absent', element=1, partage=('  menu   PRINCIPAL ', []))
        derniere = page.evaluate('RUXAWEB.state().onglets[0].obs.slice(-1)[0]')
        verifier('Élément : nom ramené à l\'orthographe existante', derniere.get('elementNom') == 'Menu principal', derniere.get('elementNom'))
        aller_audit(page)
        verifier('Éléments répétés : pas de doublon', page.locator('nav.ecrans .elt', has_text='Menu principal').count() == 1)
        ecran(page, 0)

        # Note libre : aucun statut.
        avant = page.evaluate('RUXAWEB.state().onglets[0].obs.length')
        observer(page, 'Page chargée lentement.')
        verifier('Note libre enregistrée sans critère', page.evaluate('RUXAWEB.state().onglets[0].obs.slice(-1)[0].criteres.length') == 0 and page.evaluate('RUXAWEB.state().onglets[0].obs.length') == avant + 1)
        page.fill('#obs-texte', '')
        page.click('[data-action="enregistrer-nouvelle"]')
        verifier('Observation vide : message', 'Écris l\'observation' in page.locator('#statut').inner_text())

        # Retest (#nt).
        page.click('[data-action="vue"][data-vue="grille"]')
        page.click('[data-action="critere"][data-id="raweb-10-7"]')
        page.locator('#dlg [data-action="retest"]').first.click()
        page.click('[data-action="fermer-dlg"]')
        verifier('Retest : 10.7 repasse NT sur cet écran', statut(page, 0, 'raweb-10-7') == 'NT')
        verifier('Retest : les autres écrans gardent NC', statut(page, 1, 'raweb-10-7') == 'NC')
        ecran(page, 0)
        verifier('Retest : observation barrée', page.locator('.obs.invalide').count() >= 1)

        # Taux : hors sélection (7.1 NC) ne change que le taux élargi.
        oid = page.evaluate('RUXAWEB.state().onglets[0].id')
        page.click('[data-action="vue"][data-vue="grille"]')
        verifier('Grille : colonne Résultat (et non Onglet)', 'Résultat' in page.locator('thead').inner_text() and 'Onglet' not in page.locator('thead').inner_text())
        verifier('Grille : les cases d\'écran sont des boutons', page.locator('td.statut [data-action="cellule"]').count() > 0)
        page.click('[data-action="grille-filtre"][data-v="definir"]')
        verifier('Grille : filtre NA proposé', page.locator('[data-action="grille-filtre"][data-v="na"]').count() == 1)
        page.click('[data-action="grille-filtre"][data-v="na"]')
        verifier('Grille : filtre NA, chaque ligne a un NA', page.locator('tbody tr:not(.theme)').count() > 0 and all(page.locator('tbody tr:not(.theme)').nth(i).locator('.s-NA').count() > 0 for i in range(page.locator('tbody tr:not(.theme)').count())))
        page.click('[data-action="grille-filtre"][data-v="definir"]')
        verifier('Grille : filtre NT, chaque ligne a encore un NT', all(page.locator('tbody tr:not(.theme)').nth(i).locator('.s-NT, .s-AC').count() > 0 for i in range(page.locator('tbody tr:not(.theme)').count())))
        verifier('Grille : filtre libellé NT', page.locator('[data-action="grille-filtre"][data-v="definir"]').inner_text().startswith('NT ('))
        n_nc = int(page.locator('[data-action="grille-filtre"][data-v="nc"]').inner_text().split('(')[1].rstrip(')'))
        page.click('[data-action="grille-filtre"][data-v="nc"]')
        lignes_nc = page.locator('tbody tr:not(.theme)')
        ok_nc = (lignes_nc.count() == n_nc and all(lignes_nc.nth(i).locator('td.statut .s-NC').count() > 0 for i in range(n_nc))) if n_nc else 'Aucun critère non conforme' in page.inner_text('main')
        verifier('Grille : filtre NC, autant de lignes qu\'annoncé, chacune avec un NC', ok_nc, (n_nc, lignes_nc.count()))
        page.click('[data-action="grille-filtre"][data-v="definir"]')
        nt = page.locator('td.statut [data-action="cellule"]:has(.s-NT)').first
        eid = nt.get_attribute('data-ecran')
        nt.click()
        verifier('Case : la fiche s\'ouvre sur l\'écran cliqué', page.evaluate("document.getElementById('dlg').open") and page.locator('#dlg .cible-fiche[data-bloc-ecran="%s"]' % eid).count() == 1)
        page.locator('#dlg [data-bloc-ecran="%s"] [data-action="statut"][data-tag="c"]' % eid).click()
        verifier('Case : C posé, la fiche reste ouverte', page.locator('#dlg [data-bloc-ecran="%s"] [data-action="statut"][data-tag="c"][aria-pressed="true"]' % eid).count() == 1)
        page.locator('#dlg [data-bloc-ecran="%s"] [data-action="statut"][data-tag="na"]' % eid).click()
        verifier('Case : choix modifiable (NA)', page.locator('#dlg [data-bloc-ecran="%s"] [data-action="statut"][data-tag="na"][aria-pressed="true"]' % eid).count() == 1)
        # Tous les écrans : un NC commun devient une seule observation partagée.
        tous = page.locator('#dlg [data-bloc-ecran="tous"]')
        verifier('Fiche : ligne Tous les écrans', tous.count() == 1)
        avant = page.evaluate('RUXAWEB.state().onglets[0].obs.length')
        tous.locator('[data-action="statut-nc"]').click()
        page.fill('#statut-txt', 'Défaut présent sur tous les écrans.')
        page.click('#dlg [data-action="statut-nc-ok"]')
        dern = page.evaluate('RUXAWEB.state().onglets[0].obs.slice(-1)[0]')
        verifier('Tous les écrans (NC) : une seule observation partagée', dern['tag'] == 'nc' and dern['partage'] and len(dern['partage']['ecrans']) >= 1)
        verifier('Tous les écrans (NC) : NC allumé partout', page.locator('#dlg [data-action="statut-nc"][aria-pressed="true"]').count() >= 3)
        tous.locator('[data-action="statut"][data-tag="na"]').click()
        verifier('Tous les écrans (NA) : remplace le NC partagé', page.locator('#dlg [data-action="statut"][data-tag="na"][aria-pressed="true"]').count() >= 3 and page.locator('#dlg [data-action="statut-nc"][aria-pressed="true"]').count() == 0)
        page.click('#dlg [data-action="fermer-dlg"]')
        for _ in range(600):
            c = page.locator('td.statut [data-action="cellule"]:has(.s-NT), td.statut [data-action="cellule"]:has(.s-AC)').first
            if c.count() == 0:
                break
            c.click()
            t = page.locator('#dlg [data-bloc-ecran="tous"] [data-action="statut"][data-tag="c"]')
            if t.count():
                t.click()
            else:
                page.locator('#dlg .cible-fiche [data-action="statut"][data-tag="c"]').click()
            page.click('#dlg [data-action="fermer-dlg"]')
        verifier('Grille : plus rien à définir', 'Tous les critères ont un statut' in page.locator('main').inner_text())
        sel = page.evaluate('RUXAWEB.taux("%s")' % oid)
        ela = page.evaluate('RUXAWEB.taux("%s", true)' % oid)
        verifier('Grille complète : plus rien à définir', sel['complet'] and ela['complet'], (sel, ela))
        verifier('Taux sélection SIP : 5 NC (6.2, 10.7, 11.1, 11.2, 11.10), sans 7.1', sel['C'] == sel['total'] - 5, sel)
        verifier('Taux élargi : 7.1 en plus', ela['C'] == ela['total'] - 6, ela)
        page.click('[data-action="valider"]')
        verifier('Avant validation : points à vérifier affichés', page.locator('#t-alertes').count() == 1)
        page.click('#t-alertes ~ .rangee [data-action="valider"]')
        verifier('Validation : résumé', page.locator('h1').inner_text().startswith('Résumé'))
        verifier('Résumé : deux taux', 'Taux sélection SIP' in page.locator('main').inner_text() and 'Taux élargi' in page.locator('main').inner_text())
        verifier('Résumé : niveau du taux écrit et coloré', page.locator('main .niveau[class*="niv-"]').count() >= 1)

        # Exports.
        x = telecharger(page, 'export-xlsx')
        ws = openpyxl.load_workbook(x).active
        lignes = list(ws.iter_rows(values_only=True))
        verifier('Excel : une ligne par critère', len(lignes) == 1 + 62, len(lignes))
        verifier('Excel : numéro gardé en texte', any(r[1] == '10.10' for r in lignes))
        verifier('Excel : 10.7 NC', any(r[1] == '10.7' and r[6] == 'NC' for r in lignes))
        j = telecharger(page, 'export-jira')
        rows = list(csv.reader(io.StringIO(j.read_text(encoding='utf-8-sig'))))
        menu = [r for r in rows[1:] if 'focus invisible' in r[0]]
        verifier('Jira : un seul ticket pour l\'observation valable sur 3 écrans', len(menu) == 1, [r[0] for r in rows[1:]])
        verifier('Jira : référence RAWeb', 'RAWeb 1.1, Criterion 10.7' in menu[0][1] if menu else False)
        verifier('Jira : intitulé officiel anglais dans la référence', ('RAWeb 1.1, Criterion 10.7: On each web page, for each element receiving keyboard focus, is the focus visible?' in menu[0][1]) if menu else False, menu[0][1][-400:] if menu else '')
        verifier('Jira : observation retestée sur un seul écran toujours exporté (encore NC ailleurs)', len(menu) == 1)
        # Mémoire des exports Jira : rien ne repart, sauf « tout réexporter ».
        page.click('#btn-menu')
        page.click('[data-action="export-jira"]')
        verifier('Jira : second export sans nouveau ticket, message', 'déjà été export' in page.locator('#statut').inner_text(), page.locator('#statut').inner_text())
        tout = telecharger(page, 'export-jira-tout')
        verifier('Jira : tout réexporter reprend les mêmes tickets', len(list(csv.reader(io.StringIO(tout.read_text(encoding='utf-8-sig'))))) == len(rows))
        s = telecharger(page, 'export-json')
        sauvegarde = json.loads(s.read_text(encoding='utf-8'))
        verifier('Sauvegarde : version 2', sauvegarde.get('v') == 2)

        # Import : sauvegarde relue, autre format refusé avec un message.
        page.click('#btn-menu')
        page.click('[data-action="reinit"]')
        page.click('[data-action="reinit"]')
        verifier('Nouvel audit : vide', page.evaluate('RUXAWEB.state().onglets.length') == 0)
        page.set_input_files('#fichier-import', str(s))
        page.wait_for_timeout(300)
        verifier('Import v2 : onglet restauré', page.evaluate('RUXAWEB.state().onglets.length') == 1)
        # Ancienne notation (Écran[type "Libellé"].état) convertie à l'ouverture.
        vieux = json.loads(json.dumps(sauvegarde))
        o0 = vieux['onglets'][0]; nomE = o0['ecrans'][0]['nom']
        o0['obs'][0]['elementNom'] = nomE + '[button"Connexion"] disabled'
        o0['obs'][1]['elementNom'] = 'bottom menu[switch "Dark mode"]'
        fv = pathlib.Path(tempfile.mkdtemp()) / 'notation.json'
        fv.write_text(json.dumps(vieux), encoding='utf-8')
        page.set_input_files('#fichier-import', str(fv))
        page.wait_for_timeout(300)
        noms = page.evaluate('RUXAWEB.state().onglets[0].obs.slice(0, 2).map(function(x){ return x.elementNom; })')
        verifier('Ancienne notation convertie à l\'ouverture', noms == ['[button "Connexion"] (disabled)', 'bottom menu[switch "Dark mode"]'], str(noms))
        ancien = pathlib.Path(tempfile.mkdtemp()) / 'ancien.json'
        ancien.write_text(json.dumps({'onglets': [], 'auditNom': 'ancien'}), encoding='utf-8')
        page.set_input_files('#fichier-import', str(ancien))
        page.wait_for_timeout(300)
        verifier('Import ancien format : refusé avec un message', 'pas une sauvegarde' in page.locator('#statut').inner_text())
        # Sauvegarde 1.x (statuts critère par critère) : convertie, score repris.
        ecr = [{'id': 'e%d' % i, 'nom': 'Écran %d' % i} for i in range(3)]
        res = {}
        for e in ecr:
            res[e['id']] = {'raweb-1-1': {'statut': 'C', 'commentaire': ''}, 'raweb-8-2': {'statut': 'NA', 'commentaire': ''},
                            'raweb-3-1': {'statut': 'NC', 'commentaire': 'Liens du pied de page sans indication visuelle.', 'element': '[pied de page]'},
                            'raweb-6-1': {'statut': 'C', 'commentaire': 'The button is not read by the screen reader.'},
                            'raweb-10-7': {'statut': 'NC', 'commentaire': 'Focus peu visible.'}}
        v1 = pathlib.Path(tempfile.mkdtemp()) / 'v1.json'
        v1.write_text(json.dumps({'outil': 'RUXAWEB-etat', 'version': 1, 'outilVersion': '1.6', 'state': {'auditNom': 'v1', 'onglets': [
            {'id': 'o1', 'nom': 'Audit rapide', 'scenario': 'sip-rapide', 'ecrans': ecr, 'presences': {}, 'resultats': res}], 'exportesJira': {'raweb-3-1': True}}}), encoding='utf-8')
        page.set_input_files('#fichier-import', str(v1))
        page.wait_for_timeout(300)
        verifier('Import 1.x : converti avec un message', 'convertie' in page.locator('#statut').inner_text())
        o1 = page.evaluate('RUXAWEB.state().onglets[0]')
        nc31l = [x for x in o1['obs'] if x['tag'] == 'nc' and x['criteres'] == ['raweb-3-1']]
        verifier('Import 1.x : une seule observation NC partagée sur les 3 écrans', len(nc31l) == 1 and len(nc31l[0]['partage']['ecrans']) == 2)
        verifier('Import 1.x : C et NA repris écran par écran', len([x for x in o1['obs'] if x['tag'] in ('c', 'na')]) == 9)
        nc31 = [x['id'] for x in o1['obs'] if x['tag'] == 'nc' and x['criteres'] == ['raweb-3-1']][0]
        verifier('Import 1.x : mémoire Jira reprise (3.1 déjà exporté, 10.7 non)', page.evaluate('RUXAWEB.state().exportesJira') == ['o1:' + nc31])
        al = page.evaluate('RUXAWEB.alertes("o1")')
        verifier('Avant validation : C au texte de défaut signalé', sum(1 for x in al if x.startswith('raweb-6-1|') and 'défaut' in x) == 3, al)
        verifier('Avant validation : NC sans élément signalé', any(x.startswith('raweb-10-7|') and 'sans élément' in x for x in al), al)
        page.locator('#onglet-nav .onglet-tab').nth(1).click()
        verifier('Import 1.x : statuts dans la grille', statut(page, 0, 'raweb-1-1') == 'C' and statut(page, 2, 'raweb-3-1') == 'NC' and statut(page, 1, 'raweb-8-2') == 'NA')
        # Grille au clavier : un seul arrêt Tab, puis les flèches.
        page.click('[data-action="vue"][data-vue="grille"]')
        verifier('Clavier : une seule case dans l\'ordre de tabulation', page.locator('.cel-btn[tabindex="0"]').count() == 1)
        verifier('Grille : pas de compteur en double dans l\'en-tête', 'à définir sur l\'ensemble' not in page.locator('.titre-onglet').inner_text())
        verifier('Grille : un tbody par thème', page.locator('table tbody').count() == page.locator('tr.theme').count() and page.locator('th[scope="rowgroup"]').count() > 0)
        page.locator('.cel-btn[tabindex="0"]').focus()
        d0 = page.evaluate('[document.activeElement.dataset.id, document.activeElement.dataset.ecran]')
        page.keyboard.press('ArrowRight')
        d1 = page.evaluate('[document.activeElement.dataset.id, document.activeElement.dataset.ecran]')
        verifier('Clavier : flèche droite, écran suivant', d1[0] == d0[0] and d1[1] != d0[1], (d0, d1))
        page.keyboard.press('ArrowDown')
        d2 = page.evaluate('[document.activeElement.dataset.id, document.activeElement.dataset.ecran]')
        verifier('Clavier : flèche bas, même écran, critère suivant', d2[1] == d1[1] and d2[0] != d1[0], (d1, d2))
        page.keyboard.press('Control+End')
        verifier('Clavier : Ctrl+Fin, dernière case', page.evaluate('document.activeElement') and page.evaluate('document.activeElement === Array.from(document.querySelectorAll(".cel-btn")).pop()'))
        page.keyboard.press('Enter')
        verifier('Clavier : Entrée ouvre la fiche', page.evaluate("document.getElementById('dlg').open"))
        page.keyboard.press('Escape')
        page.wait_for_timeout(100)
        verifier('Clavier : retour sur la case à la fermeture', page.evaluate('document.activeElement.classList.contains("cel-btn")'))
        # Contenus de l'écran, à tout moment, dans une fenêtre (depuis la ligne de l'écran).
        aller_audit(page)
        page.click('.tete-ecran [data-action="configurer"]')
        nom_ecran = page.locator('.tete-ecran h2.titre-ecran').inner_text().strip()
        verifier('Ce que contient l\'écran : l\'écran en cours seulement, nommé dans le titre', page.inner_text('#dlg-titre') == 'Ce que contient ' + nom_ecran and page.locator('#dlg [data-action="contenu"]').count() == 8 and page.locator('#dlg [data-action="config-ecran"], #dlg [data-fonction-ecran]').count() == 0)
        verifier('Ce que contient l\'écran : consigne « Active ce que l\'écran contient »', 'Active ce que l\'écran contient' in page.inner_text('#dlg'))
        sw_c = page.locator('#dlg [data-action="contenu"][data-d="captcha"]')
        desc = page.locator('#' + sw_c.get_attribute('aria-describedby')).inner_text()
        verifier('Ce que contient l\'écran : description et critères visibles, liés à l\'interrupteur', page.locator('#' + sw_c.get_attribute('aria-labelledby')).inner_text() == 'CAPTCHA' and 'Critères 1.4, 1.5' in desc, desc)
        verifier('Préparer : même consigne et descriptions sans info-bulle', 'title=' not in page.evaluate("(document.querySelector('.contenus-table') || {outerHTML:''}).outerHTML"))
        sw = page.locator('#dlg [data-action="contenu"][data-d="formulaire"]').first
        etat = sw.get_attribute('aria-checked')
        sw.click()
        sw2 = page.locator('#dlg [data-action="contenu"][data-d="formulaire"]').first
        verifier('Configuration : interrupteur basculé, fenêtre à jour, focus gardé', sw2.get_attribute('aria-checked') != etat and page.evaluate('document.activeElement.closest("#dlg") !== null && document.activeElement.dataset.d === "formulaire"'))
        sw2.click()
        page.keyboard.press('Escape')
        page.wait_for_timeout(100)
        verifier('État d\'interface jamais enregistré', page.evaluate('["ficheEcran","grilleFiltre","confirmation","panneauReduit","parcoursOuvert"].every(function(k){ return !(k in RUXAWEB.state()); })'))
        # Sauvegarde 2.0 ou 2.1 : statuts de clôture et nom de partage normalisés à l'ouverture.
        v20 = pathlib.Path(tempfile.mkdtemp()) / 'v20.json'
        v20.write_text(json.dumps({'v': 2, 'auditNom': 'v20', 'support': 'desktop', 'vue': 'cloture', 'compteur': 2, 'exportesJira': [], 'grilleFiltre': 'definir',
            'onglets': [{'id': 'oa', 'nom': 'A', 'type': 'rapide', 'valide': False, 'ecrans': [{'id': 'ea', 'nom': 'A', 'contenus': {}, 'etapes': {}}, {'id': 'eb', 'nom': 'B', 'contenus': {}, 'etapes': {}}],
                'obs': [{'id': 'x1', 'n': 1, 'ecran': 'ea', 'etape': 'cloture', 'texte': 'Vérifié à la clôture', 'attendu': '', 'point': '', 'criteres': ['raweb-1-1'], 'tag': 'c', 'partage': None},
                        {'id': 'x2', 'n': 2, 'ecran': 'ea', 'etape': '1', 'texte': 'Défaut', 'attendu': '', 'point': '', 'criteres': ['raweb-3-1'], 'tag': 'nc', 'partage': {'nom': 'Menu', 'ecrans': ['eb']}}]}]}), encoding='utf-8')
        page.set_input_files('#fichier-import', str(v20))
        page.wait_for_timeout(300)
        ob = page.evaluate('RUXAWEB.state().onglets[0].obs')
        verifier('Sauvegarde 2.0 : statut de clôture devenu statut de grille, sans texte figé', ob[0]['etape'] == 'grille' and ob[0]['texte'] == '')
        verifier('Sauvegarde 2.0 : partage sans nom en double', ob[1]['partage'] == {'ecrans': ['eb']})
        verifier('Sauvegarde 2.0 : état d\'interface retiré', 'grilleFiltre' not in page.evaluate('RUXAWEB.state()') and page.evaluate('RUXAWEB.state().vue') == 'projet')
        page.set_input_files('#fichier-import', str(s))  # retour au projet de test
        page.wait_for_timeout(300)

        # Scénario : transition entre deux écrans.
        page.click('[data-action="projet"]')
        page.click('[data-action="nouvel-onglet"]')
        page.check('input[name="onglet-type"][value="scenario"]')
        page.click('[data-action="vue"][data-vue="audit"] >> nth=-1')
        verifier('Scénario : champ Transition vers', page.locator('#obs-vers').count() == 1)
        page.fill('#obs-texte', 'Le focus reste sur le bouton Continuer après le passage à l\'étape suivante.')
        chercher(page, 'ordre-focus')
        page.select_option('#obs-vers', index=1)
        page.click('[data-action="enregistrer-nouvelle"]')
        verifier('Scénario : transition affichée Écran -> Écran', ' -> ' in page.locator('#t-obs').locator('xpath=..').inner_text())
        page.click('[data-action="vue"][data-vue="ux"]')
        verifier('Scénario : onglet POUR/UX avec 8 questions', page.locator('[data-action="heur"][data-v="succes"]').count() == 8)
        for i in range(6):
            page.locator('[data-action="heur"][data-v="succes"]').nth(i).click()
        page.locator('[data-action="heur"][data-v="echec"]').nth(6).click()
        page.locator('[data-action="heur"][data-v="na"]').nth(7).click()
        page.fill('textarea[data-heur-com="h7"]', 'Six étapes pour une simple commande.')
        page.locator('textarea[data-heur-com="h7"]').blur()
        oid2 = page.evaluate('RUXAWEB.state().ongletId')
        verifier('POUR/UX : score 86 % (6 succès sur 7), hors taux', '86 %' in page.locator('main').inner_text())
        verifier('POUR/UX : commentaire gardé', page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id==="%s"})[0].heuristiques.h7.commentaire' % oid2) == 'Six étapes pour une simple commande.')
        page.click('[data-action="vue"][data-vue="resume"]')
        verifier('Résumé du scénario : pas de taux élargi', 'Taux élargi' not in page.locator('main').inner_text() and 'Taux sélection SIP' in page.locator('main').inner_text())
        verifier('Résumé du scénario : score POUR/UX à part', 'Score POUR/UX' in page.locator('main').inner_text())
        x2 = telecharger(page, 'export-xlsx')
        verifier('Excel : lignes POUR/UX du scénario', sum(1 for r in openpyxl.load_workbook(x2).active.iter_rows(values_only=True) if str(r[1] or '').startswith('POUR/UX')) == 8)
        jira = telecharger(page, 'export-jira')
        verifier('Scénario : ticket avec la transition', any(' -> ' in r[0] for r in csv.reader(io.StringIO(jira.read_text(encoding='utf-8-sig')))))
        page.click('[data-action="projet"]')
        page.locator('[data-action="ouvrir"]').first.click()

        # Import d'un rapport axe-core puis Lighthouse : des résultats à reprendre, jamais un statut.
        aller_audit(page)
        ecran(page, 1)
        axe = {'testEngine': {'name': 'axe-core', 'version': '4.13.0'}, 'url': 'https://exemple.lu/',
               'violations': [{'id': 'image-alt', 'help': 'Images must have alternative text', 'tags': ['wcag2a', 'wcag111'],
                               'nodes': [{'target': ['#logo']}, {'target': ['.promo img']}]},
                              {'id': 'regle-inconnue', 'help': 'Contraste insuffisant (test)', 'tags': ['wcag2aa', 'wcag143'],
                               'nodes': [{'target': ['p.note']}]}],
               'incomplete': [{'id': 'color-contrast', 'help': 'Contrast to review', 'tags': ['wcag143'], 'nodes': [{'target': ['h2']}]}],
               'passes': [{'id': 'document-title', 'tags': ['wcag242'], 'nodes': [{'target': ['html']}]}]}
        f = pathlib.Path(tempfile.mkdtemp()) / 'axe.json'
        f.write_text(json.dumps(axe), encoding='utf-8')
        avant = statut(page, 1, 'raweb-1-1')
        aller_etape(page, 'vide')
        verifier('Tour à vide : invitation à importer axe ou Lighthouse', page.locator('#t-import-vide').count() == 1)
        page.set_input_files('#fichier-auto', str(f))
        page.wait_for_timeout(300)
        ouvertes = lambda: [c for c in page.evaluate('RUXAWEB.state().onglets[0].candidats') if c['etat'] == 'ouvert' and c.get('source') != 'collage']
        verifier('axe : 3 pistes rangées (2 échecs, 1 incomplet)', len(ouvertes()) == 3)
        verifier('Tour à vide : pistes rangées, pas affichées', page.locator('[data-action="reprendre"]').count() == 0 and '3 pistes' in page.inner_text('#t-import-vide ~ p, section[aria-labelledby="t-import-vide"]'))
        verifier('axe : règle réussie ignorée', 'document-title' not in page.locator('main').inner_text())
        verifier('axe : rien de compté avant reprise', statut(page, 1, 'raweb-1-1') == avant)
        cands = page.evaluate('RUXAWEB.state().onglets[0].candidats')
        par = {c['regle']: c['criteres'] for c in cands}
        verifier('axe : image-alt vers 1.1 (table RUXAL)', par.get('image-alt') == ['raweb-1-1'], par)
        verifier('axe : règle hors table rapprochée par WCAG 1.4.3 (3.2)', par.get('regle-inconnue') == ['raweb-3-2'], par)
        aller_etape(page, '1')
        verifier('Étape 1 : les 2 pistes de contraste (3.2)', page.locator('[data-action="reprendre"]').count() == 2)
        aller_etape(page, '2')
        verifier('Étape 2 : la piste image-alt (1.1)', page.locator('[data-action="reprendre"]').count() == 1)
        page.locator('[data-action="reprendre"]').first.click()
        verifier('Reprendre : observation préremplie', 'Images must have alternative text' in page.input_value('#obs-texte'))
        page.click('[data-action="enregistrer-nouvelle"]')
        derniere = page.evaluate('RUXAWEB.state().onglets[0].obs.slice(-1)[0]')
        verifier('Reprendre : observation #nc avec sa source', derniere['tag'] == 'nc' and derniere.get('source', {}).get('regle') == 'image-alt', derniere)
        verifier('Reprendre : 1.1 NC', statut(page, 1, 'raweb-1-1') == 'NC')
        aller_etape(page, '2')
        verifier('Reprendre : piste retirée de la liste', page.locator('[data-action="reprendre"]').count() == 0 and len(ouvertes()) == 2)
        aller_etape(page, '1')
        page.locator('[data-action="ecarter"]').first.click()
        verifier('Écarter : piste retirée', page.locator('[data-action="reprendre"]').count() == 1 and len(ouvertes()) == 1)
        lh = {'lighthouseVersion': '13.5.0', 'categories': {'accessibility': {'auditRefs': [{'id': 'button-name'}, {'id': 'html-has-lang'}, {'id': 'focus-traps'}]}},
              'audits': {'button-name': {'id': 'button-name', 'title': 'Buttons do not have an accessible name', 'score': 0, 'scoreDisplayMode': 'binary',
                                         'details': {'items': [{'node': {'selector': 'button.close'}}]}},
                         'html-has-lang': {'id': 'html-has-lang', 'title': 'html has lang', 'score': 1, 'scoreDisplayMode': 'binary'},
                         'focus-traps': {'id': 'focus-traps', 'title': 'Manual', 'score': None, 'scoreDisplayMode': 'manual'}}}
        f2 = f.parent / 'lh.json'
        f2.write_text(json.dumps(lh), encoding='utf-8')
        page.set_input_files('#fichier-auto', str(f2))
        page.wait_for_timeout(300)
        cands = ouvertes()
        verifier('Lighthouse : un seul échec, réussites et contrôles manuels ignorés', len(cands) == 1 and cands[0]['titre'].startswith('Buttons do not have'), cands)
        verifier('Lighthouse : button-name vers 7.1 et 11.9', cands and cands[0]['criteres'] == ['raweb-7-1', 'raweb-11-9'], cands)
        aller_etape(page, '3a')
        verifier('Étape 3a : la piste button-name (7.1)', page.locator('[data-action="reprendre"]').count() == 1 and 'Buttons do not have' in page.locator('main').inner_text())
        # Export de l'extension axe DevTools (Chrome) : JSON à plat puis CSV.
        # Même structure qu'un vrai export de l'extension (failedRules et needsReview avant allIssues).
        ext = {'url': 'https://exemple.lu/', 'extensionVersion': '4.140.0', 'axeVersion': '4.13.0',
               'failedRules': [{'name': 'image-alt', 'count': 2, 'mode': 'automated'}], 'needsReview': [],
               'source': {'productName': 'axe-devtools-html', 'productComponentName': 'extension-chrome'}, 'allIssues': [
            {'ruleId': 'link-name', 'help': 'Ignored', 'tags': ['wcag244'], 'selector': ['a.x'], 'needsReview': False, 'isIgnored': True},
            {'ruleId': 'image-alt', 'help': 'Images must have alternative text', 'tags': ['wcag111'], 'selector': ['#logo'], 'needsReview': False},
            {'ruleId': 'image-alt', 'help': 'Images must have alternative text', 'tags': ['wcag111'], 'selector': ['.promo img'], 'needsReview': False},
            {'ruleId': 'color-contrast', 'help': 'Contrast to review', 'tags': ['wcag143'], 'selector': ['h2'], 'needsReview': True}]}
        f4 = f.parent / 'axe-devtools.json'
        f4.write_text(json.dumps(ext), encoding='utf-8')
        page.set_input_files('#fichier-auto', str(f4))
        page.wait_for_timeout(300)
        cands = [c for c in page.evaluate('RUXAWEB.state().onglets[0].candidats') if c['etat'] == 'ouvert']
        verifier('Extension axe (JSON) : 2 règles, éléments regroupés', len(cands) == 2 and [c['nb'] for c in cands] == [2, 1] and cands[1]['type'] == 'incomplet', cands)
        verifier('Extension axe : version du moteur et pluriels', 'axe DevTools (axe-core 4.13.0) : 1 échec et 1 point à vérifier' in page.locator('#statut').inner_text(), page.locator('#statut').inner_text())
        verifier('Extension axe (JSON) : image-alt vers 1.1', cands and cands[0]['criteres'] == ['raweb-1-1'], cands)
        f5 = f.parent / 'axe-devtools.csv'
        f5.write_text('\ufeffRule ID;Description;Selector;Needs Review\nimage-alt;Images must have alternative text;#logo;false\nbutton-name;"Buttons must have; discernible text";button.close;false\n', encoding='utf-8')
        page.set_input_files('#fichier-auto', str(f5))
        page.wait_for_timeout(300)
        cands = [c for c in page.evaluate('RUXAWEB.state().onglets[0].candidats') if c['etat'] == 'ouvert']
        verifier('Extension axe (CSV) : 2 règles reconnues', [c['regle'] for c in cands] == ['image-alt', 'button-name'], cands)
        f3 = f.parent / 'autre.json'
        f3.write_text(json.dumps({'foo': 1}), encoding='utf-8')
        page.set_input_files('#fichier-auto', str(f3))
        page.wait_for_timeout(300)
        verifier('Import d\'un autre fichier : refusé avec un message', 'ni un rapport axe' in page.locator('#statut').inner_text())

        # Référentiel : toutes les fiches, avec gravité, étape, consigne, et la notation des éléments.
        page.click('#btn-ref')
        nb = page.evaluate('RUXAWEB.state() && document.querySelectorAll(".ref-fiche").length')
        verifier('Référentiel : une fiche par critère et bonne pratique (62)', nb == 62, nb)
        txt = page.locator('main').inner_text()
        verifier('Référentiel : consigne, impact, gravité, étape', all(k in txt for k in ('Comment vérifier', 'Impact', 'gravité', 'étape 2 Code et outils')))
        verifier('Référentiel : section Noter les éléments', 'Noter les éléments' in txt and 'Écran.zone[type "libellé"] (état)' in txt and 'All.footer[links]' in txt)
        verifier('Référentiel : bouton PDF par impression', page.locator('[data-action="imprimer-ref"]').count() == 1)
        verifier('Référentiel : bouton du haut marqué page courante', page.get_attribute('#btn-ref', 'aria-current') == 'page')
        page.click('[data-action="theming"][data-v="ruxal"]')
        verifier('Référentiel : regroupement par thèmes RUXAL', page.locator('.ref-groupe h2').first.inner_text().startswith('Navigation & structure'))
        page.click('[data-action="theming"][data-v="officiel"]')
        page.emulate_media(media='print')
        verifier('Impression : en-tête et Parcours masqués', page.locator('.barre').is_hidden() and page.locator('#panneau-etapes').is_hidden())
        page.emulate_media(media='screen')
        page.locator('[data-action="ouvrir"]').first.click()
        aller_audit(page)
        verifier('Observation : rappel de notation sous Élément', 'sans l\'écran' in page.locator('#aide-element').inner_text().lower() and page.get_attribute('#obs-partage-nom', 'aria-describedby') == 'aide-element apercu-ticket')
        page.fill('#obs-partage-nom', 'pied de page[lien "écrivez-nous"] (désactivé)')
        verifier('Élément : aperçu du ticket en direct, écran ajouté et traduit en anglais (libellé intact)', page.locator('#apercu-ticket code').first.inner_text().endswith('.footer[link "écrivez-nous"] (disabled)'), page.inner_text('#apercu-ticket'))
        page.fill('#obs-partage-nom', '')
        page.click('[data-action="vue"][data-vue="grille"]')
        verifier('Grille : gravité affichée par critère', page.locator('tbody .grav').count() == 62)

        # Ordre « étape d'abord » : une étape sur tous les écrans, puis l'étape suivante.
        page.click('[data-action="projet"]')
        page.click('[data-action="nouvel-onglet"]')
        page.click('[data-action="vue"][data-vue="audit"] >> nth=-1')
        def en_cours():
            return page.locator('#liste-etapes [aria-current="step"]').inner_text(), page.locator('.ecrans [aria-current="true"]').inner_text()
        verifier('Étape d\'abord : départ Tour à vide sur le premier écran', 'Tour à vide' in en_cours()[0] and 'Accueil' in en_cours()[1], en_cours())
        verifier('Étape d\'abord : bouton vers l\'écran suivant', 'Valider puis passer à : Écran avec formulaire' in page.locator('[data-action="etape-faite"]').inner_text())
        page.click('[data-action="etape-faite"]')
        verifier('Étape d\'abord : même étape, écran suivant', 'Tour à vide' in en_cours()[0] and 'formulaire' in en_cours()[1], en_cours())
        verifier('Étape d\'abord : premier écran coché pour l\'étape', page.locator('.ecrans [data-action="ecran"]').first.locator('.coche').count() == 1)
        page.locator('.ecrans [data-action="ecran"]').first.click()
        verifier('Étape d\'abord : changer d\'écran garde l\'étape', 'Tour à vide' in en_cours()[0])
        page.locator('.ecrans [data-action="ecran"]').nth(2).click()
        verifier('Étape d\'abord : dernier écran, bouton vers l\'étape suivante', 'Valider puis passer à : Écran avec formulaire' in page.locator('[data-action="etape-faite"]').inner_text())
        page.click('[data-action="etape-faite"]')
        verifier('Étape d\'abord : bouton vers l\'étape suivante', 'Valider puis passer à : étape Usage standard' in page.locator('[data-action="etape-faite"]').inner_text())
        page.click('[data-action="etape-faite"]')
        verifier('Étape d\'abord : étape suivante sur le premier écran', 'Usage standard' in en_cours()[0] and 'Accueil' in en_cours()[1], en_cours())
        verifier('Étape d\'abord : Tour à vide fait (3/3 validés)', '3/3 validés' in page.locator('#liste-etapes').inner_text() and '(fait)' in page.locator('#liste-etapes [data-etape="vide"]').inner_text())

        page.click('[data-action="vue"][data-vue="grille"]')
        # Grille : un critère se pose conforme sans observation, depuis sa fiche.
        ligne = page.locator('tbody tr', has=page.locator('td.statut .s-NT')).first
        cid = ligne.locator('[data-action="critere"]').get_attribute('data-id')
        ligne.locator('[data-action="critere"]').click()
        verifier('Fiche (grille) : boutons C / NC / NA par écran', page.locator('#dlg [data-action="statut"][data-tag="c"]').count() >= 1)
        page.locator('#dlg [data-bloc-ecran]:not([data-bloc-ecran="tous"]) [data-action="statut"][data-tag="c"]:not([disabled])').first.click()
        verifier('Fiche (grille) : C posé, la fiche reste ouverte et à jour', page.evaluate("document.getElementById('dlg').open") and page.locator('#dlg [data-action="statut"][data-tag="c"][aria-pressed="true"]').count() == 1)
        page.click('#dlg [data-action="fermer-dlg"]')
        page.wait_for_timeout(100)
        verifier('Fiche fermée : contenu vidé', page.locator('#dlg-corps').inner_html() == '')
        ligne2 = page.locator('tbody tr', has=page.locator('[data-action="critere"][data-id="%s"]' % cid))
        verifier('Grille : critère conforme sans observation', 'C' in [x.strip() for x in ligne2.locator('td.statut .pastille').all_inner_texts()])
        # Modifier une observation : une note devient non conforme avec un critère.
        aller_audit(page)
        page.fill('#obs-texte', 'Un seul facteur pour montrer l\'état actif.')
        page.click('[data-action="enregistrer-nouvelle"]')
        note = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs.slice(-1)[0]')
        verifier('Note enregistrée sans critère', note['criteres'] == [])
        page.click('[data-action="modif-obs"][data-id="%s"]' % note['id'])
        verifier('Modifier : observation chargée, titre et boutons', page.input_value('#obs-texte').startswith('Un seul facteur') and page.inner_text('#form-obs-titre') == 'Modifier l\'observation' and page.locator('[data-action="dupliquer-obs"]').count() == 1 and page.locator('[data-action="nouvelle-obs"]').count() == 1)
        chercher(page, crit='raweb-3-1')
        page.click('[data-action="enregistrer-nouvelle"]')
        obs = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs')
        modif = [x for x in obs if x['id'] == note['id']]
        verifier('Modifier : même observation, critère ajouté, pas de doublon', len(modif) == 1 and modif[0]['criteres'] == ['raweb-3-1'] and modif[0]['n'] == note['n'] and len(obs) == len([x for x in obs if x['id'] != note['id']]) + 1)
        verifier('Modifier : formulaire revenu en saisie', 'Nouvelle observation' in page.inner_text('#form-obs-titre') and page.input_value('#obs-texte') == '')
        page.click('[data-action="modif-obs"][data-id="%s"]' % note['id'])
        page.click('[data-action="nouvelle-obs"]')
        verifier('Nouvelle observation sans modification : formulaire vidé sans question', 'Nouvelle observation' in page.inner_text('#form-obs-titre') and page.locator('#quitter-obs').count() == 0 and page.input_value('#obs-texte') == '')
        # Enregistrer : on reste sur l'observation, qui passe en modification (un second Enregistrer ne crée pas de doublon).
        nb0 = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs.length')
        page.fill('#obs-texte', 'Bouton Fermer sans nom accessible.')
        page.fill('#obs-partage-nom', '"Close" button')
        chercher(page, crit='raweb-7-1')
        page.click('#form-obs button[type=submit]')
        verifier('Enregistrer : reste sur l\'observation, en modification, heure affichée', page.input_value('#obs-texte').startswith('Bouton Fermer') and page.inner_text('#form-obs-titre') == 'Modifier l\'observation' and 'Enregistrée à' in page.inner_text('#obs-info'))
        page.click('#form-obs button[type=submit]')
        obsR = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs')
        verifier('Enregistrer deux fois : une seule observation', len(obsR) == nb0 + 1)
        orig = obsR[-1]
        # Dupliquer : copie à compléter, même élément, sans texte ni critère.
        page.click('[data-action="dupliquer-obs"]')
        verifier('Dupliquer : copie avec le même élément, texte et critères vides', 'copie' in page.inner_text('#form-obs-titre') and page.input_value('#obs-partage-nom') == '[button "Close"]' and page.input_value('#obs-texte') == '' and page.locator('.crit-retenus').count() == 0, (page.inner_text('#form-obs-titre'), page.input_value('#obs-partage-nom'), page.input_value('#obs-texte'), page.locator('.crit-retenus').count()))
        page.fill('#obs-texte', 'Bouton Fermer trop petit.')
        page.click('[data-action="enregistrer-nouvelle"]')
        obsD = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs')
        verifier('Dupliquer puis enregistrer : nouvelle observation, même élément, original intact', len(obsD) == nb0 + 2 and obsD[-1]['elementNom'] == orig['elementNom'] and obsD[-1]['id'] != orig['id'] and [x for x in obsD if x['id'] == orig['id']][0]['texte'] == orig['texte'])
        # Modifications non enregistrées : question avant de quitter (Annuler, Ne pas enregistrer, Enregistrer).
        page.click('[data-action="modif-obs"][data-id="%s"]' % orig['id'])
        page.fill('#obs-texte', 'Texte modifié non enregistré.')
        page.click('[data-action="nouvelle-obs"]')
        verifier('Quitter avec des modifications : question posée, focus dessus', page.locator('#quitter-obs').count() == 1 and page.evaluate("document.activeElement.id") == 'quitter-obs')
        page.click('[data-action="quitter-obs"][data-choix="annuler"]')
        verifier('Annuler : on reste, texte gardé', page.input_value('#obs-texte') == 'Texte modifié non enregistré.' and page.locator('#quitter-obs').count() == 0)
        page.click('[data-action="nouvelle-obs"]')
        page.click('[data-action="quitter-obs"][data-choix="abandon"]')
        verifier('Ne pas enregistrer : formulaire vidé, observation inchangée', page.input_value('#obs-texte') == '' and [x for x in page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs') if x['id'] == orig['id']][0]['texte'] == orig['texte'])
        page.click('[data-action="modif-obs"][data-id="%s"]' % orig['id'])
        page.fill('#obs-texte', 'Bouton Fermer sans nom, lu « bouton ».')
        page.click('[data-action="dupliquer-obs"]')
        page.click('[data-action="quitter-obs"][data-choix="enregistrer"]')
        verifier('Enregistrer puis dupliquer : modification gardée, copie ouverte', [x for x in page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs') if x['id'] == orig['id']][0]['texte'].startswith('Bouton Fermer sans nom, lu') and 'copie' in page.inner_text('#form-obs-titre'))
        page.click('[data-action="nouvelle-obs"]')

        # Panneau des étapes masquable : un seul bouton, dans le bandeau de l'onglet, toujours au même endroit.
        lm = page.evaluate("document.getElementById('main').getBoundingClientRect().width")
        pos = page.evaluate("(function(){var r=document.getElementById('btn-etapes').getBoundingClientRect();return [r.x,r.y];})()")
        verifier('Bouton du panneau : visible dans le bandeau de l\'onglet, panneau ouvert', page.locator('#btn-etapes').is_visible() and page.get_attribute('#btn-etapes', 'aria-expanded') == 'true' and page.locator('#panneau-etapes [data-action="panneau-bascule"]').count() == 0)
        page.click('#btn-etapes')
        verifier('Panneau masqué : disparu, contenu élargi, focus gardé, libellé avec l\'étape en cours', page.locator('#panneau-etapes').is_hidden() and page.evaluate("document.getElementById('main').getBoundingClientRect().width") > lm + 200 and page.evaluate("document.activeElement.id") == 'btn-etapes' and page.get_attribute('#btn-etapes', 'aria-expanded') == 'false' and '/' in page.get_attribute('#btn-etapes', 'aria-label'))
        apres_pos = page.evaluate("(function(){var r=document.getElementById('btn-etapes').getBoundingClientRect();return [r.x,r.y];})()")
        verifier('Bouton du panneau : même position ouvert ou fermé', apres_pos == pos, (pos, apres_pos, page.evaluate("window.scrollY")))
        page.click('[data-action="vue"][data-vue="grille"]') if page.locator('[data-action="vue"][data-vue="grille"]').count() else None
        verifier('Panneau masqué : le reste pendant l\'audit (grille)', page.locator('#panneau-etapes').is_hidden() and page.get_attribute('#btn-etapes', 'aria-expanded') == 'false')
        page.click('#btn-ref')
        verifier('Référentiel : panneau toujours affiché, sans bouton', page.locator('#panneau-etapes').is_visible() and page.locator('#btn-etapes').is_hidden())
        page.click('#onglet-nav .onglet-tab[data-id="%s"]' % page.evaluate('RUXAWEB.state().ongletId'))
        aller_audit(page)
        page.click('#btn-etapes')
        verifier('Panneau rouvert : focus gardé sur le bouton', page.locator('#panneau-etapes').is_visible() and page.evaluate("document.activeElement.id") == 'btn-etapes' and page.get_attribute('#btn-etapes', 'aria-label') == 'Masquer les étapes' and page.get_attribute('#btn-etapes', 'data-bulle') == 'Masquer les étapes' and page.get_attribute('#btn-etapes', 'title') is None)
        # Deuxième cycle : l'animation d'ouverture est rejouée, le bouton ne doit pas bouger pour autant.
        page.click('#btn-etapes'); page.click('#btn-etapes')
        rouvert_pos = page.evaluate("(function(){var r=document.getElementById('btn-etapes').getBoundingClientRect();return [r.x,r.y];})()")
        verifier('Bouton du panneau : même position à chaque réouverture, pendant l\'animation du panneau', rouvert_pos == pos, (pos, rouvert_pos))
        # Bandeau : « Observation » au lieu de « Saisie », compteur collé à la bascule, bulle au survol fermée par Échap.
        verifier('Bascule de vue : Observation et Grille', page.locator('.titre-onglet [data-vue="audit"]').inner_text().strip() == 'Observation')
        bx = page.evaluate("(function(){var a=document.querySelector('.titre-onglet .tags').getBoundingClientRect(),i=document.querySelector('.titre-onglet .tags + .doux');return i ? Math.round(i.getBoundingClientRect().left - a.right) : -1;})()")
        verifier('Compteur juste à droite de la bascule', 0 <= bx <= 24, bx)
        page.hover('#btn-etapes'); page.wait_for_timeout(50)
        bulle = page.evaluate("getComputedStyle(document.getElementById('btn-etapes'), '::after').display")
        page.keyboard.press('Escape'); page.wait_for_timeout(50)
        apres = page.evaluate("getComputedStyle(document.getElementById('btn-etapes'), '::after').display")
        verifier('Bulle du bouton des étapes : au survol, fermée par Échap', bulle == 'block' and apres == 'none', (bulle, apres))
        page.mouse.move(0, 0)
        verifier('Formulaire : « Qu\'as-tu observé ? », un seul bouton Enregistrer, aide sans critère', "Qu'as-tu observé ?" in page.text_content('#form-obs h3.sous-titre-form') and page.inner_text('#form-obs button[type=submit]').strip() == 'Enregistrer' and page.locator('#aide-sans-critere').count() == 1)

        # Suggestions pendant la frappe.
        aller_audit(page)
        page.fill('#obs-texte', 'On ne voit pas le focus quand je tabule dans le menu')
        page.wait_for_timeout(400)
        verifier('Suggestions : Visibilité du focus proposée', 'Visibilité du focus' in page.inner_text('#obs-sugg'), page.inner_text('#obs-sugg'))
        page.locator('#obs-sugg [data-point="focus-invisible"]').click()
        verifier('Suggestion choisie : point de contrôle et critère 10.7', page.locator('[data-action="retirer-crit"][data-retirer="raweb-10-7"]').count() == 1 and page.input_value('#obs-texte').startswith('On ne voit pas'))
        page.click('[data-action="retirer-crit"][data-retirer="raweb-10-7"]')
        verifier('Retirer un critère : il passe en « Retiré », avec Remettre', page.locator('[data-action="retirer-crit"][data-retirer="raweb-10-7"]').count() == 0 and page.locator('[data-action="remettre-crit"][data-retirer="raweb-10-7"]').count() == 1)
        page.click('[data-action="remettre-crit"][data-retirer="raweb-10-7"]')
        verifier('Remettre un critère retiré', page.locator('[data-action="retirer-crit"][data-retirer="raweb-10-7"]').count() == 1 and 'Visibilité du focus' in page.inner_text('.crit-retenus'))
        verifier('Observation : recherche repliée (correction) et renvoi vers la grille', page.evaluate("document.getElementById('det-ajout').open") is False and 'Va dans la grille' in page.inner_text('#form-obs'))
        verifier('Recherche : une seule ligne par critère (pas de doublon)', page.evaluate("(function(){var v=[].map.call(document.querySelectorAll('#liste-criteres option'),function(o){return o.getAttribute('data-crit')});return v.length===new Set(v).size && v.length>50})()"))
        verifier('Formulaire : plus de champ Point de contrôle ni de résultat, deux questions, aide NC', page.locator('#obs-point').count() == 0 and page.locator('#form-obs h3.sous-titre-form').count() == 2 and 'non conformes' in page.inner_text('#aide-resultat'))
        page.click('#form-obs details summary')
        verifier('Attendu : aide sur le ticket Jira', 'Expected behavior' in page.inner_text('#aide-attendu'))
        verifier('Champs obligatoires : Observation marquée, Attendu facultatif', page.get_attribute('#obs-texte', 'aria-required') == 'true' and page.locator('label[for="obs-texte"] .oblig').count() == 1 and 'facultatif' in page.inner_text('label[for="obs-attendu"]') and page.locator('label[for="obs-attendu"] .oblig').count() == 0)
        page.fill('#obs-texte', '')
        page.click('#form-obs button[type=submit]')
        verifier('Champ obligatoire vide : marqué invalide', page.get_attribute('#obs-texte', 'aria-invalid') == 'true')
        page.fill('#obs-texte', 'x')
        verifier('Champ rempli : plus invalide', page.get_attribute('#obs-texte', 'aria-invalid') is None)
        page.fill('#obs-texte', '')

        # Coller des observations : format lisible, changement d'écran, critères proposés si absents.
        page.click('[data-action="coller-obs"]')
        verifier('Coller : fenêtre avec consigne pour une IA', page.locator('#dlg #coller-texte').count() == 1 and 'RAWeb 1.1' in page.input_value('#consigne-dlg') and 'element | observation | criteria' in page.input_value('#consigne-dlg') and 'status |' not in page.input_value('#consigne-dlg') and '13.11 pointer action can be cancelled' in page.input_value('#consigne-dlg') and 'SCREENS OF THIS AUDIT' in page.input_value('#consigne-dlg'))
        cons_agent = (pathlib.Path(__file__).parent.parent / 'docs' / 'copilot' / 'consigne-observation-ruxaweb.txt').read_text(encoding='utf-8').strip()
        verifier('Consigne IA : identique à celle de l\'agent Copilot RUXAWEB', page.input_value('#consigne-dlg').startswith(cons_agent))
        verifier('Consigne IA : anglais par défaut et cas particuliers', all(k in page.input_value('#consigne-dlg') for k in ('Always write in English', 'special cases')))
        noms = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].ecrans.map(function(e){return e.nom})')
        page.fill('#coller-texte', 'NC | Menu principal | Focus invisible dans le menu. | 10.7\n- C | | Les titres sont bien hiérarchisés. |\nÉcran : %s\nLe contraste du texte gris clair est trop faible\nbutton "Payer" | Bouton sans nom. | 99.9' % noms[1])
        page.click('[data-action="coller-ok"]')
        page.wait_for_timeout(100)
        pistes = [k for k in page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].candidats') if k.get('source') == 'collage']
        verifier('Coller : 3 pistes lues (ligne C écartée, signalée)', len(pistes) == 3 and 'C ignoré' in page.inner_text('#statut'), [p['titre'] for p in pistes])
        verifier('Coller : statut, élément, critère lus', pistes[0]['tag'] == 'nc' and pistes[0]['element'] == 'Menu principal' and pistes[0]['criteres'] == ['raweb-10-7'])
        verifier('Coller : ligne sans statut (format actuel) lue comme un défaut', pistes[2]['tag'] == 'nc' and pistes[2]['element'] == 'button "Payer"')
        verifier('Coller : « Écran : » change d\'écran, critère proposé par mots-clés', pistes[1]['ecran'] != pistes[0]['ecran'] and pistes[1]['propose'] and 'raweb-3-2' in pistes[1]['criteres'], pistes[1])
        verifier('Coller : critère inconnu signalé', '99.9' in page.inner_text('#statut'))
        # Lignes rendues par une IA avec la consigne : point de contrôle (et type) à la place des critères.
        page.click('[data-action="coller-obs"]')
        page.fill('#coller-texte', open(pathlib.Path(__file__).parent / 'collage-points-de-controle.txt', encoding='utf-8').read())
        page.click('[data-action="coller-ok"]')
        page.wait_for_timeout(100)
        attendus = json.loads((pathlib.Path(__file__).parent / 'collage-points-de-controle.json').read_text(encoding='utf-8'))
        pc = [k for k in page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].candidats') if k.get('source') == 'collage'][-len(attendus):]
        bons = [k['point'] == a[0] and set('raweb-' + r.replace('.', '-') for r in a[1]) <= set(k['criteres']) for k, a in zip(pc, attendus)]
        verifier('Coller (points de contrôle) : %d lignes, critères déduits' % len(attendus), all(bons) and len(pc) == len(attendus), [k['point'] for k, b in zip(pc, bons) if not b])
        verifier('Coller (points de contrôle) : type d\'élément gardé', any(k['point'] == 'nom-absent' and k['typeElement'] != '' for k in pc))
        verifier('Coller (points de contrôle) : type de contraste déduit des mots (case à cocher : 3.3 seul)', [k['criteres'] for k in pc[-3:-1]] == [['raweb-3-3'], ['raweb-3-3']], [k['criteres'] for k in pc[-3:]])
        # Réponse entière de l'exemple de l'agent Copilot (bloc de code, puis « Criteria: »), plus une ligne avec une bonne
        # pratique et une question finale : 3 pistes, critères lus en numéros et codes BP, explications et question ignorées.
        cons = (pathlib.Path(__file__).parent.parent / 'docs' / 'copilot' / 'consigne-observation-ruxaweb.txt').read_text(encoding='utf-8')
        ex = cons.split('Answer:\n')[1].strip().replace('Écran : Login\n', '').replace('\n```\nCriteria:', '\nNC | "Login" dialog | Focus does not return to the opener. | 12.8, BP3\n```\nCriteria:')
        # Titre « Criteria: » oublié par l'agent : seul le bloc de code est lu, les explications ne deviennent pas des pistes.
        ex = ex.replace('\nCriteria:\n', '\n')
        avantC = len(page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].candidats || []'))
        page.click('[data-action="coller-obs"]')
        page.fill('#coller-texte', ex + '\nTo clarify:\n- "page lente" : which element and what happens?')
        page.click('[data-action="coller-ok"]')
        page.wait_for_timeout(100)
        ajout = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].candidats')[avantC:]
        verifier('Agent Copilot : réponse entière collée (3 pistes, critères exacts, explications et question ignorées)', len(ajout) == 3 and [k['criteres'] for k in ajout] == [['raweb-3-3'], ['raweb-7-1', 'raweb-7-3'], ['raweb-12-8', 'bp3']] and not any(k['propose'] for k in ajout), [(k['titre'][:30], k['criteres']) for k in ajout])
        for k in ajout:
            page.locator('[data-action="ecarter"]').last.click()
        page.locator('[data-action="reprendre"]').first.click()
        verifier('Reprendre une piste collée : formulaire rempli', page.input_value('#obs-texte') == 'Focus invisible dans le menu.' and page.input_value('#obs-partage-nom') == 'Menu principal' and page.locator('[data-action="retirer-crit"][data-retirer="raweb-10-7"]').count() == 1)
        page.fill('#obs-texte', '')
        # Lignes NC identiques sur plusieurs écrans : une seule piste, écrans cochés à la reprise.
        avantF = len(page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].candidats || []'))
        page.click('[data-action="coller-obs"]')
        page.fill('#coller-texte', 'Écran : %s\nNC | Main navigation | Focus lost in the menu. | Visibilité du focus\nÉcran : %s\nNC | main navigation | Focus lost in the menu. | Visibilité du focus\nNC | "Pay" button | Focus lost in the menu. | Visibilité du focus' % (noms[0], noms[1]))
        page.click('[data-action="coller-ok"]')
        page.wait_for_timeout(100)
        fus = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].candidats')[avantF:]
        ids = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].ecrans.map(function(e){return e.id})')
        verifier('Coller : lignes NC identiques regroupées (2 pistes pour 3 lignes)', len(fus) == 2 and fus[0]['autresEcrans'] == [ids[1]] and fus[1]['autresEcrans'] == [] and 'regroupée' in page.inner_text('#statut'), [(k['element'], k.get('autresEcrans')) for k in fus])
        page.locator('[data-action="ecran"][data-id="%s"]' % ids[0]).first.click()
        page.locator('[data-action="reprendre"][data-id="%s"]' % fus[0]['id']).click()
        verifier('Reprendre une piste regroupée : autres écrans cochés', page.locator('[data-ecran-partage="%s"]:checked' % ids[1]).count() == 1)
        # Une observation partagée se modifie depuis n'importe lequel de ses écrans, sans perdre ses écrans.
        page.fill('#obs-texte', 'Focus lost in the menu.')
        page.click('[data-action="enregistrer-nouvelle"]')
        page.wait_for_timeout(100)
        xs = page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs')
        xp = xs[-1]
        page.locator('[data-action="ecran"][data-id="%s"]' % ids[1]).first.click()
        verifier('Observation partagée : Modifier sur un autre écran, Supprimer seulement sur son écran', page.locator('[data-action="modif-obs"][data-id="%s"]' % xp['id']).count() == 1 and page.locator('[data-action="suppr-obs"][data-id="%s"]' % xp['id']).count() == 0)
        page.locator('[data-action="modif-obs"][data-id="%s"]' % xp['id']).click()
        page.fill('#obs-partage-nom', 'Main navigation')
        page.click('[data-action="enregistrer-nouvelle"]')
        page.wait_for_timeout(100)
        xa = [x for x in page.evaluate('RUXAWEB.state().onglets.filter(function(o){return o.id===RUXAWEB.state().ongletId})[0].obs') if x['id'] == xp['id']][0]
        verifier('Observation partagée modifiée ailleurs : mêmes écrans, élément changé', xa['ecran'] == xp['ecran'] and sorted(xa['partage']['ecrans']) == sorted(xp['partage']['ecrans']) and xa['elementNom'] == 'Main navigation', xa)
        page.locator('[data-action="ecran"][data-id="%s"]' % ids[0]).first.click()
        page.fill('#obs-texte', '')
        page.click('#btn-ref')
        verifier('Référentiel : consigne pour une IA', page.locator('#consigne-ref').count() == 1 and 'Convertir des notes' in page.inner_text('main'))
        verifier('Icônes : décoratives, sur Fichier et Référentiel', page.locator('#btn-menu svg[aria-hidden="true"]').count() == 1 and page.locator('#btn-ref svg[aria-hidden="true"]').count() == 1)
        page.locator('[data-action="ouvrir"]').first.click()

        # L'en-tête défile avec la page ; le panneau des étapes glisse avec le contenu, sans saut, puis colle sous le bandeau.
        hauts, dessous = [], []
        for y in range(0, 400, 10):
            page.evaluate('window.scrollTo(0, %d)' % y)
            hauts.append(page.evaluate("document.getElementById('panneau-etapes').getBoundingClientRect().top"))
            dessous.append(round(hauts[-1] - page.evaluate("document.querySelector('.titre-onglet').getBoundingClientRect().bottom")))
        ecarts = [a - b for a, b in zip(hauts, hauts[1:])]
        cale = round(hauts[-1] - float(page.evaluate("parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--tete-h'))")))
        verifier('Défilement : panneau des étapes sans saut, collé sous le bandeau', all(-0.5 <= e <= 10.5 for e in ecarts) and cale == 24, (max(ecarts), cale))
        verifier('Défilement : le haut du panneau des étapes ne passe jamais sous le bandeau', min(dessous) >= 0, min(dessous))
        bandeau = page.evaluate("document.querySelector('.titre-onglet').getBoundingClientRect().top")
        entete = page.evaluate("document.querySelector('header.barre').getBoundingClientRect().bottom")
        verifier('Défilement : l\'en-tête part avec la page, le bandeau de l\'onglet colle en haut', round(bandeau) == 0 and entete <= 0, (bandeau, entete))
        page.evaluate('window.scrollTo(0, 0)')
        # Jusqu'en bas de page, sur chaque vue, le panneau des étapes reste sous le bandeau de l'onglet.
        tops = {}
        for nom, aller in (('saisie', lambda: aller_audit(page)), ('grille', lambda: page.click('[data-action="vue"][data-vue="grille"]')),
                           ('projet', lambda: page.click('[data-action="projet"]')), ('referentiel', lambda: page.click('#btn-ref'))):
            aller()
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(80)
            tops[nom] = round(page.evaluate("document.getElementById('panneau-etapes').getBoundingClientRect().top - parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--tete-h'))"))
        verifier('Panneau des étapes collé sous le bandeau jusqu\'en bas de page, sur toutes les vues', all(v >= 16 for v in tops.values()), tops)
        # En bas de page, les deux colonnes latérales sont alignées.
        page.locator('#onglet-nav .onglet-tab').nth(1).click()
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        bas = page.evaluate('(function(){var a=document.getElementById("panneau-etapes").getBoundingClientRect(),e=document.querySelector("nav.ecrans").getBoundingClientRect();return [Math.round(a.top),Math.round(e.top)];})()')
        verifier('Défilement : panneau des étapes et colonne des écrans alignés', bas[0] == bas[1], bas)
        page.evaluate('window.scrollTo(0, 0)')
        page.evaluate('window.scrollTo(0, 0)')
        page.click('[data-action="vue"][data-vue="grille"]') if page.locator('[data-action="vue"][data-vue="grille"]').count() else None
        page.click('#btn-ref')
        page.evaluate('window.scrollTo(0, 3000)')
        page.wait_for_timeout(100)
        verifier('Haut de page : bouton affiché après défilement, en bas à gauche', page.locator('#btn-haut').is_visible() and page.evaluate("document.getElementById('btn-haut').getBoundingClientRect().left") < 40)
        page.click('#btn-haut')
        page.wait_for_function('scrollY < 5', timeout=5000)
        verifier('Haut de page : retour en haut, focus sur le titre', page.evaluate('scrollY') < 5 and page.evaluate('document.activeElement.tagName') == 'H1')
        page.locator('[data-action="ouvrir"]').first.click() if page.locator('[data-action="ouvrir"]').count() else page.click('[data-action="projet"]')
        page.click('[data-action="projet"]')
        page.locator('[data-action="ouvrir"]').first.click()

        # Fonctions primaires : configurateur au niveau du projet, testées avant les écrans, observations communes.
        page.click('[data-action="projet"]')
        verifier('Page Projet : 7 fonctions préréglées (En-tête, Navigation avec le burger, Fil d\'Ariane à part, plus de Menu ni de Formulaire type)', page.locator('[data-action="fonction-presente"]').count() >= 7 and all(n in page.inner_text('.liste-fonctions') for n in ('En-tête', 'navigation principale, menu burger', 'Fil d\'Ariane', 'Fenêtre modale (ouverture, fermeture)')) and not any(n in page.inner_text('.liste-fonctions') for n in ('Formulaire type', 'Retour ou fil', 'Menu ou menu burger')))
        page.click('[data-action="fonction-presente"][data-id="nav"]')
        page.fill('#fonction-nouvelle', 'Bandeau cookies')
        page.click('[data-action="fonction-ajout"]')
        verifier('Page Projet : fonction libre ajoutée et active', 'Bandeau cookies' in page.inner_text('.liste-fonctions'))
        verifier('Page Projet : seule une fonction ajoutée peut être supprimée', page.locator('.liste-fonctions [data-action="suppr-fonction"]').count() == 1)
        page.fill('#fonction-nouvelle', 'Fonction jetable')
        page.click('[data-action="fonction-ajout"]')
        fj = page.evaluate('RUXAWEB.state().fonctions.filter(function(f){ return f.nom === "Fonction jetable"; })[0].id')
        page.click('[data-action="suppr-fonction"][data-id="%s"]' % fj)
        verifier('Supprimer une fonction : confirmation demandée', 'Confirmer' in page.inner_text('[data-action="suppr-fonction"][data-id="%s"]' % fj))
        page.click('[data-action="suppr-fonction"][data-id="%s"]' % fj)
        verifier('Supprimer une fonction : retirée du projet et des onglets', 'Fonction jetable' not in page.inner_text('.liste-fonctions') and page.evaluate('RUXAWEB.state().onglets.every(function(o){ return !o.fonctionsEcrans || !("%s" in o.fonctionsEcrans); })' % fj))
        # Panneau masqué dans un onglet : un nouvel onglet l'ouvre quand même, et le réglage ne part pas dans la sauvegarde.
        page.locator('#onglet-nav .onglet-tab').nth(1).click()
        if page.get_attribute('#btn-etapes', 'aria-expanded') == 'true': page.click('#btn-etapes')
        verifier('Panneau masqué : réglage d\'affichage, hors sauvegarde', not page.evaluate('"panneauReduit" in RUXAWEB.state()'))
        page.click('[data-action="projet"]')
        page.click('[data-action="nouvel-onglet"]')
        oidF = page.evaluate('RUXAWEB.state().ongletId')
        verifier('Nouvel onglet : panneau des étapes ouvert par défaut', page.locator('#panneau-etapes').is_visible())
        verifier('Nouvel onglet : fonctions actives sur tous ses écrans', page.locator('[data-fonction-ecran="nav"]:checked').count() == 3)
        page.locator('[data-fonction-ecran="nav"]').nth(2).uncheck()
        page.click('main [data-action="vue"][data-vue="audit"]')
        verifier('Étape d\'abord : la fonction primaire passe avant les écrans', page.inner_text('h2.titre-ecran') == 'Navigation' and page.locator('.ecrans [data-action="cible-fonction"][aria-current="true"]').count() == 1)
        verifier('Fonction : pas de bloc Où, recap sur la fonction', page.locator('#obs-partage-nom').count() == 0)
        page.fill('#obs-texte', 'Focus invisible dans la navigation principale.')
        chercher(page, 'focus-invisible')
        page.click('[data-action="enregistrer-nouvelle"]')
        st = lambda i: statut(page, i, 'raweb-10-7')
        verifier('Fonction NC : NC sur les écrans cochés, pas sur les autres', [st(0), st(1), st(2)] == ['NC', 'NC', 'NT'], [st(0), st(1), st(2)])
        page.click('[data-action="projet"]')
        verifier('Page Projet : état de la fonction', '1 NC (10.7)' in page.inner_text('.liste-fonctions'))
        page.click('[data-action="nouvel-onglet"][data-type="scenario"]')
        verifier('Nouvel onglet (scénario) : fonction du projet déjà cochée', page.locator('[data-fonction-ecran="nav"]:checked').count() == 3 and '1 NC (10.7)' in page.inner_text('main'))
        page.locator('.onglet-tab.ajout').click()
        verifier('+ Nouvel onglet : page Projet, focus sur le choix du module', page.evaluate('document.activeElement.id') == 't-nouveau')
        page.locator('[data-action="ouvrir"]').last.click()
        oidS = page.evaluate('RUXAWEB.state().ongletId')
        verifier('Fonction commune : NC aussi dans le scénario', page.evaluate("(function(){var s=RUXAWEB.state();return true})()") and statut(page, 0, 'raweb-10-7') == 'NC')
        page.click('[data-action="ouvrir"][data-id="%s"]' % oidF)
        aller_audit(page)
        page.click('.ecrans [data-action="cible-fonction"][data-id="nav"]')
        verifier('Fonction : bouton de fin vers la fonction suivante', 'Valider puis passer à : Bandeau cookies' in page.inner_text('[data-action="etape-faite"]'))
        page.click('[data-action="etape-faite"]')
        page.click('[data-action="etape-faite"]')
        verifier('Après les fonctions : premier écran', page.inner_text('h2.titre-ecran') == 'Accueil' and 'Fonctions primaires sur cet écran' in page.inner_text('main'))
        page.click('.ecrans [data-action="cible-fonction"][data-id="nav"]')
        page.click('[data-action="retest-fonction"]')
        verifier('Retest de la fonction : NT dans tous les onglets', st(0) == 'NT')
        page.click('[data-action="ouvrir"][data-id="%s"]' % oidS)
        verifier('Retest de la fonction : NT aussi dans le scénario', statut(page, 0, 'raweb-10-7') == 'NT')
        page.click('[data-action="ouvrir"][data-id="%s"]' % oidF)
        aller_audit(page)
        page.click('.ecrans [data-action="cible-fonction"][data-id="nav"]')
        page.fill('#obs-texte', 'Focus toujours invisible sur le lien Contact du menu.')
        chercher(page, 'focus-invisible')
        page.click('[data-action="enregistrer-nouvelle"]')
        jf = telecharger(page, 'export-jira')
        lignesF = [r for r in csv.reader(io.StringIO(jf.read_text(encoding='utf-8-sig')))][1:]
        tf = [r for r in lignesF if 'All.Navigation' in r[0]]
        tm = [r for r in lignesF if '; ' in r[0].split(' | ')[3]]
        verifier('Jira : plusieurs écrans, titre avec « ; », une ligne par écran dans le corps', len(tm) >= 1 and all(any(l.startswith(x) for l in tm[0][1].split('\n')) for x in [x.strip() for x in tm[0][0].split(' | ')[3].split(':')[0].split(';')]), [r[0] for r in tm])
        verifier('Jira : tags indicatifs design ou code dans les labels', all(('design' in r or 'code' in r) for r in lignesF[1:]) and len(lignesF[0]) == 10, lignesF[0])
        verifier('Jira : fonction primaire notée All.Navigation, thème anglais', len(tf) == 1 and 'All.Navigation: ' in tf[0][0] and '| Navigation & structure |' in tf[0][0], [r[0] for r in lignesF])
        verifier('Jira : un ticket pour la fonction, avec ses écrans des deux onglets', len(tf) == 1 and 'Navigation' in tf[0][1] and any(l.startswith('Screens: ') and ' : ' in l for l in tf[0][1].split('\n')), [r[0] for r in lignesF])
        aller_audit(page)
        page.click('#liste-etapes [data-vue="resume"]')
        verifier('Résumé : état des fonctions primaires', 'Fonctions primaires' in page.inner_text('main') and '1 NC (10.7)' in page.inner_text('main'), page.inner_text('main')[:300])

        # Suppression d'un onglet en deux clics, depuis le tableau de bord.
        page.click('[data-action="projet"]')
        avant = page.evaluate('RUXAWEB.state().onglets.length')
        verifier('Carte d\'onglet : un menu d\'actions par carte, fermé', page.locator('.tuile-onglet [data-action="menu-onglet"][aria-expanded="false"]').count() == page.locator('.tuile-onglet').count() > 0)
        kebab = page.locator('[data-action="menu-onglet"]').last
        oid = kebab.get_attribute('data-id')
        kebab.click()
        verifier('Menu d\'onglet : ouvert, focus sur la première action', page.locator('[data-action="menu-onglet"][data-id="%s"][aria-expanded="true"]' % oid).count() == 1 and page.evaluate('document.activeElement.dataset.action') == 'gerer-ecrans')
        page.keyboard.press('Escape')
        verifier('Menu d\'onglet : Échap le referme et rend le focus au bouton', page.locator('#menu-%s' % oid).is_hidden() and page.evaluate('document.activeElement.dataset.action') == 'menu-onglet')
        page.click('[data-action="menu-onglet"][data-id="%s"]' % oid)
        page.click('#menu-%s [data-action="suppr-onglet"]' % oid)
        verifier('Menu d\'onglet : le menu reste ouvert pour confirmer', page.locator('#menu-%s' % oid).is_visible())
        verifier('Supprimer un onglet : confirmation demandée', page.evaluate('RUXAWEB.state().onglets.length') == avant and 'Confirmer' in page.locator('[data-action="suppr-onglet"][data-id="%s"]' % oid).inner_text())
        page.click('[data-action="suppr-onglet"][data-id="%s"]' % oid)
        verifier('Supprimer un onglet : onglet retiré', page.evaluate('RUXAWEB.state().onglets.length') == avant - 1 and 'supprimé' in page.locator('#statut').inner_text())
        page.locator('[data-action="ouvrir"]').first.click()
        page.click('.ecrans [data-action="vue"][data-vue="preparer"]')
        verifier('Page des écrans : suppression de l\'onglet dans la carte de l\'onglet', page.locator('main section[aria-label="Onglet"] [data-action="suppr-onglet"]').count() == 1)

        page.emulate_media(color_scheme='dark')
        page.click('[data-action="projet"]')
        verifier('Mode sombre : pas d\'erreur', not erreurs, erreurs)
        verifier('Aucune erreur JavaScript', not erreurs, erreurs)
        nav.close()
    echecs = resultats.count(False)
    print('\n%d contrôles, %d échec(s)' % (len(resultats), echecs))
    return 1 if echecs else 0


if __name__ == '__main__':
    sys.exit(main())
