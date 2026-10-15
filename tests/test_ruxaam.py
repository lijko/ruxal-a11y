#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Tests de bout en bout de src/ruxaam.html (Playwright, Chromium sans interface).

Installation (une fois) :
  python3 -m pip install playwright
  python3 -m playwright install chromium
Lancement :
  python3 tests/test_ruxaam.py
Code retour 0 si tout passe, 1 sinon. L'outil est ouvert en file:// : aucun serveur n'est nécessaire.
"""
import json
import pathlib
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = (ROOT / 'src' / 'ruxaam.html').as_uri()
DATA = ROOT / 'data'

NB_RAAM = len(json.loads((DATA / 'criteres-raam.json').read_text(encoding='utf-8'))['criteres'])
NB_BP = len(json.loads((DATA / 'bonnes-pratiques.json').read_text(encoding='utf-8'))['bonnes_pratiques'])
NB = NB_RAAM + NB_BP

resultats = []


def verifier(nom, condition, detail=''):
    resultats.append((nom, bool(condition), detail))
    print(('OK    ' if condition else 'ÉCHEC ') + nom + ('' if condition else '  — ' + str(detail)))


def ouvrir(page):
    page.goto(URL)
    page.evaluate("localStorage.clear()")
    page.reload()


def creer_onglet(page, type_audit='sip-rapide', ecrans=('Accueil', 'Connexion', 'Panier')):
    page.click('#btnDashboard')
    page.click('[data-action="goto-scenario"]')
    page.click('[data-scenario="%s"]' % type_audit)
    champs = page.locator('input[placeholder^="Nom de l"]')
    while champs.count() < len(ecrans):
        page.get_by_role('button', name='+ Ajouter un écran').click()
    for i, nom in enumerate(ecrans):
        champs.nth(i).fill(nom)
    page.get_by_role('button', name="Créer l'onglet").click()


def message(page):
    return page.locator('#importStatus').inner_text()


def telechargement(page, action):
    """Exécute action ; renvoie le texte du fichier produit, ou None si aucun fichier n'est produit."""
    try:
        with page.expect_download(timeout=1500) as dl:
            action()
        return pathlib.Path(dl.value.path()).read_text(encoding='utf-8')
    except Exception:
        return None


def exporter(page, libelle):
    page.click('#btnExportMenu')
    page.locator('.menu-item', has_text=libelle).click()


def main():
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        page = navigateur.new_page(accept_downloads=True)
        erreurs = []
        page.on('pageerror', lambda e: erreurs.append(str(e)))
        ouvrir(page)

        # --- Exports sans onglet : un message, aucun fichier
        for libelle in ('Tickets Jira (CSV)', 'Liste des critères (CSV)', 'Données (JSON)'):
            f = telechargement(page, lambda: exporter(page, libelle))
            verifier('Export « %s » sans onglet : pas de fichier' % libelle, f is None, f and f[:80])
            verifier('Export « %s » sans onglet : message' % libelle, 'aucun onglet' in message(page), message(page))
        f = telechargement(page, lambda: page.click('#btnExportEtat'))
        verifier('Sauvegarder sans onglet : pas de fichier', f is None)
        verifier('Sauvegarder sans onglet : message', 'Rien à sauvegarder' in message(page), message(page))

        # --- Page Référentiel : 55 pastilles d'étape, version 1.22
        page.click('#btnReferentiel')
        verifier('Référentiel : %d fiches' % NB, page.locator('.ref-card').count() == NB, page.locator('.ref-card').count())
        verifier('Référentiel : %d pastilles d\'étape' % NB, page.locator('.etape-chip').count() == NB, page.locator('.etape-chip').count())
        verifier('Référentiel : 20 « si présent »', page.locator('.si-present-chip').count() == 20, page.locator('.si-present-chip').count())
        page.click('#btnAide')
        aide = page.locator('#main').inner_text()
        verifier('Aide : version 1.22', 'version 1.22' in aide)
        verifier('Aide : section « Protocole de test »', 'Protocole de test' in aide and '4. Navigation alternative' in aide)
        verifier('Aide : déclencheurs à jour', 'limite de session' in aide and 'lien coloré' not in aide)

        # --- Onglet RAAM : vue par thème / par étape
        creer_onglet(page)
        verifier('Onglet : %d lignes de critères' % NB, page.locator('.crit-row').count() == NB, page.locator('.crit-row').count())
        verifier('Vue par thème : %d pastilles d\'étape' % NB, page.locator('.crit-row .etape-chip').count() == NB)
        page.click('[data-action="set-vue-liste"][data-vue="etapes"]')
        groupes = page.locator('.theme-group-name').all_inner_texts()
        verifier('Vue par étape : 4 groupes', len(groupes) == 4, groupes)
        verifier('Vue par étape : %d critères' % NB, page.locator('.crit-row').count() == NB, page.locator('.crit-row').count())
        verifier('Vue par étape : un encart par groupe', page.locator('.etape-encart').count() == 4, page.locator('.etape-encart').count())
        par_etape = page.evaluate("""() => [...document.querySelectorAll('.theme-group')].map(g => g.querySelectorAll('.crit-row').length)""")
        verifier('Vue par étape : 23 / 1 / 24 / 7', par_etape == [23, 1, 24, 7], par_etape)
        chips = page.locator('.crit-row .etape-chip').all_inner_texts()
        verifier('Vue par étape : pastilles seulement pour 3a / 3b (24)', len(chips) == 24 and all(c[:2] in ('3a', '3b') for c in chips), chips[:3])
        verifier('Vue par étape : choix de thématisation masqué', page.locator('[data-action="set-theming"]').count() == 0)
        page.click('[data-action="set-vue-liste"][data-vue="themes"]')
        verifier('Retour vue par thème : %d critères' % NB, page.locator('.crit-row').count() == NB)

        # --- Jira : tous NT, puis C, puis NC selon la plateforme
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira, tous NT : pas de fichier', f is None)
        verifier('Jira, tous NT : message', 'aucun critère n\'a encore été testé' in message(page), message(page))
        page.click('[data-action="set-statut-tous"][data-crit="raam-5-3"][data-statut="C"]')
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira, aucun NC : message', f is None and 'aucun critère n\'est non conforme' in message(page), message(page))
        page.click('[data-action="set-statut-tous"][data-crit="raam-5-1"][data-statut="NC"]')
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira sans plateforme : iOS et Android', f and '- iOS: <to be completed>' in f and '- Android: <to be completed>' in f)
        verifier('Jira sans plateforme : 7 colonnes', f and f.splitlines()[0].count(',') == 6, f and f.splitlines()[0])
        for code, ligne, etiquette in (('ios', '- iOS:', ',ios,'), ('android', '- Android:', ',android,'), ('cross', '- Cross-platform:', ',multiplateforme,')):
            page.click('#plateformeToggle [data-plateforme="%s"]' % code)
            presse = page.locator('#plateformeToggle [data-plateforme="%s"]' % code).get_attribute('aria-pressed')
            f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
            autres = [x for x in ('- iOS:', '- Android:', '- Cross-platform:') if x != ligne]
            verifier('Jira %s : bouton enfoncé' % code, presse == 'true')
            verifier('Jira %s : seule la plateforme choisie' % code, f and ligne in f and not any(x in f for x in autres))
            verifier('Jira %s : étiquette et colonne Labels en plus' % code, f and etiquette in f and f.splitlines()[0].count(',') == 7)
        page.click('#plateformeToggle [data-plateforme="cross"]')  # second clic : désélection
        verifier('Plateforme : second clic désélectionne', page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxal-state')).plateforme") == '')

        # --- Notes par écran supprimées ; export JSON : écrans sans commentaire
        verifier('Notes par écran retirées', page.locator('textarea[data-action="set-commentaire-ecran"]').count() == 0)
        f = telechargement(page, lambda: exporter(page, 'Données (JSON)'))
        ecrans = json.loads(f)['onglets'][0]['ecrans'] if f else None
        verifier('Export JSON : écrans = {nom}', ecrans and all(list(e.keys()) == ['nom'] for e in ecrans), ecrans)

        # --- Onglets UX·POUR seuls (possibles seulement dans une ancienne sauvegarde) : pas d'export RAAM
        ouvrir(page)
        uxpour = {'outil': 'RUXAAM-etat', 'version': 1, 'state': {'auditNom': 'UX seul', 'ticketsJira': {}, 'filtreRetest': False,
                  'view': 'dashboard', 'onglets': [{'id': 'ong_u', 'nom': 'Parcours', 'scenario': 'flow', 'approches': ['OSAPS'],
                  'ecrans': [{'id': 'ec_u', 'nom': 'Étape 1'}], 'vue': 'audit', 'theming': 'ruxal', 'vueAudit': 'pourux',
                  'resultats': {'ec_u': {}}, 'heuristiques': {}, 'commentaireOnglet': '', 'valide': False}]}}
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as t:
            json.dump(uxpour, t)
        page.set_input_files('#inputImportEtat', t.name)
        page.wait_for_timeout(300)
        for libelle in ('Liste des critères (CSV)', 'Tickets Jira (CSV)'):
            f = telechargement(page, lambda: exporter(page, libelle))
            verifier('UX·POUR seul, « %s » : pas de fichier, message' % libelle, f is None and 'aucun onglet RAAM' in message(page), message(page))

        # --- Import d'une sauvegarde 1.21 (critères retirés, ancienne thématisation, pas de plateforme)
        ancienne = {'outil': 'RUXAAM-etat', 'version': 1, 'outilVersion': '1.21', 'state': {
            'auditNom': 'Sauvegarde 1.21', 'ticketsJira': {}, 'filtreRetest': False, 'activeOngletId': None, 'view': 'dashboard',
            'onglets': [{'id': 'ong_a', 'nom': 'Audit rapide RAAM', 'scenario': 'sip-rapide', 'approches': ['SIP'],
                         'ecrans': [{'id': 'ec_1', 'nom': 'Accueil', 'commentaire': 'ancien'}], 'vue': 'audit', 'theming': 'sip',
                         'vueAudit': 'raam', 'heuristiques': {}, 'commentaireOnglet': '', 'valide': False,
                         'resultats': {'ec_1': {'raam-1-8': {'statut': 'NC', 'commentaire': ''}, 'raam-7-2': {'statut': 'C', 'commentaire': ''},
                                                'raam-1-1': {'statut': 'C', 'commentaire': ''}}}}]}}
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as t:
            json.dump(ancienne, t)
        page.set_input_files('#inputImportEtat', t.name)
        page.wait_for_timeout(300)
        m = message(page)
        verifier('Import 1.21 : critères ignorés signalés', '2 critère(s)' in m and 'dont 1 non conforme' in m, m)
        verifier('Import 1.21 : plateforme vide', page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxal-state')).plateforme") == '')
        page.click('.tab-main')
        verifier('Import 1.21 : onglet affiché (thématisation officielle)', page.locator('.crit-row').count() == NB)

        verifier('Aucune erreur JavaScript', not erreurs, erreurs)
        navigateur.close()

    echecs = [r for r in resultats if not r[1]]
    print('\n%d contrôles, %d échec(s)' % (len(resultats), len(echecs)))
    return 1 if echecs else 0


if __name__ == '__main__':
    sys.exit(main())
