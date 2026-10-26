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
    print(('OK    ' if condition else 'ÉCHEC ') + nom + ('' if condition else ' , ' + str(detail)))


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
        verifier('Aide : version 1.24', 'version 1.24' in aide)
        verifier('Aide : section « Protocole de test »', 'Protocole de test' in aide and '4. Navigation alternative' in aide)
        verifier('Aide : section « Noter les éléments »', 'Noter les éléments' in aide and 'Écran[type "Libellé"]' in aide)
        verifier('Aide : déclencheurs à jour', 'limite de session' in aide and 'lien coloré' not in aide)
        verifier('Aide : mémoire des exports Jira documentée', 'tout réexporter' in aide and 'pas réexporté automatiquement' in aide)

        # --- Onglet RAAM : « Contenu des écrans » (tout désactivé au départ)
        creer_onglet(page)
        nb_coeur = NB - 20
        verifier('Contenu des écrans : %d critères visibles au départ' % nb_coeur, page.locator('.crit-row').count() == nb_coeur, page.locator('.crit-row').count())
        verifier('Contenu des écrans : 20 critères masqués annoncés', '20 critère(s)' in page.locator('.presence-masques').inner_text())
        interrupteurs = page.evaluate("""() => [...document.querySelectorAll('[role=switch]')].map(b => b.id)""")
        verifier('Contenu des écrans : 5 × 3 interrupteurs + session', len(interrupteurs) == 16, len(interrupteurs))
        verifier('Interrupteur : nom accessible', page.locator('[role=switch][data-decl="formulaire"]').first.get_attribute('aria-label') == 'Formulaire (Accueil)')
        for i in interrupteurs:
            page.click('#' + i)
        verifier('Tous les interrupteurs activés : %d critères' % NB, page.locator('.crit-row').count() == NB, page.locator('.crit-row').count())
        verifier('Interrupteur : aria-checked', page.locator('#' + interrupteurs[0]).get_attribute('aria-checked') == 'true')
        page.click('[role=switch][data-decl="formulaire"][data-ecran="%s"]' % page.locator('[role=switch][data-decl="formulaire"]').nth(1).get_attribute('data-ecran'))
        ligne_91 = page.locator('.crit-row', has=page.locator('[data-crit="raam-9-1"]')).first
        verifier('Écran sans formulaire : cellule « Absent »', ligne_91.locator('.statut-absent').count() == 1, ligne_91.locator('.statut-absent').count())
        page.click('[role=switch][data-decl="formulaire"][data-ecran="%s"]' % page.locator('[role=switch][data-decl="formulaire"]').nth(1).get_attribute('data-ecran'))

        # --- Vue par thème / par étape (tout le contenu activé)
        verifier('Vue par thème : %d pastilles d\'étape' % NB, page.locator('.crit-row .etape-chip').count() == NB)
        page.click('[data-action="set-vue-liste"][data-vue="etapes"]')
        groupes = page.locator('.theme-group-name').all_inner_texts()
        verifier('Vue par étape : 4 groupes', len(groupes) == 4, groupes)
        verifier('Vue par étape : un encart par groupe', page.locator('.etape-encart').count() == 4, page.locator('.etape-encart').count())
        par_etape = page.evaluate("""() => [...document.querySelectorAll('.theme-group')].map(g => g.querySelectorAll('.crit-row').length)""")
        verifier('Vue par étape : 23 / 1 / 24 / 7', par_etape == [23, 1, 24, 7], par_etape)
        chips = page.locator('.crit-row .etape-chip').all_inner_texts()
        verifier('Vue par étape : pastilles seulement pour 3a / 3b (24)', len(chips) == 24 and all(c[:2] in ('3a', '3b') for c in chips), chips[:3])
        verifier('Vue par étape : choix de thématisation masqué', page.locator('[data-action="set-theming"]').count() == 0)
        page.click('[data-action="set-vue-liste"][data-vue="themes"]')
        verifier('Retour vue par thème : %d critères' % NB, page.locator('.crit-row').count() == NB)

        # --- Jira : tous NT, puis C, puis NC ; « Élément concerné » ; mémoire des exports
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira, tous NT : pas de fichier', f is None)
        verifier('Jira, tous NT : message', 'aucun critère n\'a encore été testé' in message(page), message(page))
        page.click('[data-action="set-statut-tous"][data-crit="raam-5-3"][data-statut="C"]')
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira, aucun NC : message', f is None and 'aucun critère n\'est non conforme' in message(page), message(page))
        page.click('[data-action="set-statut-tous"][data-crit="raam-5-1"][data-statut="NC"]')
        verifier('NC : champ « Ticket Jira » absent', page.locator('[data-action="set-ticket-jira"]').count() == 0)
        champ = page.locator('[data-action="set-element-critere"][data-crit="raam-5-1"]').first
        verifier('NC : champ « Élément concerné »', champ.count() == 1)
        champ.fill('Accueil[button "Valider"] | (disabled)')
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira : élément concerné repris, | remplacé par /', f and 'Accueil[button ""Valider""] / (disabled)' in f, f and f[:300])
        verifier('Jira sans plateforme : iOS et Android', f and '- iOS: <to be completed>' in f and '- Android: <to be completed>' in f)
        verifier('Jira sans plateforme : 7 colonnes', f and f.splitlines()[0].count(',') == 6, f and f.splitlines()[0])
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Mémoire Jira : second export sans fichier', f is None)
        verifier('Mémoire Jira : message « déjà exporté »', 'Aucun nouveau ticket : 1 critère(s) non conforme(s) déjà exporté(s)' in message(page), message(page))
        page.click('[data-action="set-statut-tous"][data-crit="raam-9-1"][data-statut="NC"]')
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Mémoire Jira : seul le nouveau ticket', f and f.count(',Task,') == 1 and 'RAAM-9.1' in f, f and f.count(',Task,'))
        verifier('Mémoire Jira : message « N déjà exportés, M nouveaux »', '1 ticket(s) déjà exporté(s), 1 nouveau(x)' in message(page), message(page))
        verifier('Mémoire Jira : enregistrée dans l\'état', page.evaluate("Object.keys(JSON.parse(localStorage.getItem('atelier-ruxal-state')).exportesJira).sort().join()") == 'raam-5-1,raam-9-1')
        for code, ligne, etiquette in (('ios', '- iOS:', ',ios,'), ('android', '- Android:', ',android,'), ('cross', '- Cross-platform:', ',multiplateforme,')):
            page.click('#plateformeToggle [data-plateforme="%s"]' % code)
            presse = page.locator('#plateformeToggle [data-plateforme="%s"]' % code).get_attribute('aria-pressed')
            f = telechargement(page, lambda: exporter(page, 'Tickets Jira : tout réexporter'))
            autres = [x for x in ('- iOS:', '- Android:', '- Cross-platform:') if x != ligne]
            verifier('Jira %s (tout réexporter) : 2 tickets' % code, f and f.count(',Task,') == 2)
            verifier('Jira %s : bouton enfoncé' % code, presse == 'true')
            verifier('Jira %s : seule la plateforme choisie' % code, f and ligne in f and not any(x in f for x in autres))
            verifier('Jira %s : étiquette et colonne Labels en plus' % code, f and etiquette in f and f.splitlines()[0].count(',') == 7)
        page.click('#plateformeToggle [data-plateforme="cross"]')  # second clic : désélection
        verifier('Plateforme : second clic désélectionne', page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxal-state')).plateforme") == '')

        # --- Aide « Noter les éléments » : aller et retour vers le champ
        champ_id = page.locator('[data-action="set-element-critere"][data-crit="raam-5-1"]').first.get_attribute('id')
        page.locator('[data-action="aide-notation"][data-focus="%s"]' % champ_id).click()
        verifier('Icône d\'aide : focus sur « Noter les éléments »', page.evaluate("document.activeElement.id") == 'aide-notation')
        verifier('Aide : deux boutons de retour', page.locator('[data-action="retour-champ"]').count() == 2)
        page.locator('[data-action="retour-champ"]').first.click()
        verifier('Retour : focus sur le champ d\'origine', page.evaluate("document.activeElement.id") == champ_id)

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
            'auditNom': 'Sauvegarde 1.21', 'ticketsJira': {'raam-1-1': 'ABC-1'}, 'filtreRetest': False, 'activeOngletId': None, 'view': 'dashboard',
            'onglets': [{'id': 'ong_a', 'nom': 'Audit rapide RAAM', 'scenario': 'sip-rapide', 'approches': ['SIP'],
                         'ecrans': [{'id': 'ec_1', 'nom': 'Accueil', 'commentaire': 'ancien'}], 'vue': 'audit', 'theming': 'sip',
                         'vueAudit': 'raam', 'heuristiques': {}, 'commentaireOnglet': '', 'valide': False,
                         'resultats': {'ec_1': {'raam-1-8': {'statut': 'NC', 'commentaire': ''}, 'raam-7-2': {'statut': 'C', 'commentaire': ''},
                                                'raam-1-1': {'statut': 'NC', 'commentaire': ''}, 'raam-9-1': {'statut': 'C', 'commentaire': ''},
                                                'raam-11-2': {'statut': 'C', 'commentaire': ''}}}}]}}
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as t:
            json.dump(ancienne, t)
        page.set_input_files('#inputImportEtat', t.name)
        page.wait_for_timeout(300)
        m = message(page)
        verifier('Import 1.21 : critères ignorés signalés', '2 critère(s)' in m and 'dont 1 non conforme' in m, m)
        verifier('Import 1.21 : plateforme vide', page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxal-state')).plateforme") == '')
        page.click('.tab-main')
        etat = page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxal-state'))")
        verifier('Import 1.21 : présences déduites (formulaire évalué)', etat['onglets'][0]['presences'].get('ec_1', {}).get('formulaire') is True, etat['onglets'][0].get('presences'))
        verifier('Import 1.21 : limite de session déduite du 11.2', etat.get('limiteSession') is True)
        verifier('Import 1.21 : critères évalués toujours visibles', page.locator('.crit-row', has=page.locator('[data-crit="raam-9-1"]')).count() == 1 and page.locator('.crit-row', has=page.locator('[data-crit="raam-11-2"]')).count() == 1)
        verifier('Import 1.21 : mémoire Jira vide', etat.get('exportesJira') == {})
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Import 1.21 : ancien « Ticket Jira » sans effet', f and 'RAAM-1.1' in f)

        # --- Gestion des écrans en cours d'audit, affichage un par un au-delà de 6
        ouvrir(page)
        creer_onglet(page)
        page.click('summary:has-text("Écrans testés")')
        lignes = page.locator('.ecrans-ligne')
        verifier('écrans : panneau ouvert, 3 lignes', lignes.count() == 3, lignes.count())
        verifier('Audit rapide : suppression bloquée à 3', page.locator('[data-action="delete-ecran"]').first.is_disabled())
        ajout = page.locator('[data-action="ecran-ajout-input"]')
        ajout.fill('Profil')
        page.click('[data-action="add-ecran-onglet"]')
        verifier('Ajout : 4 lignes, panneau resté ouvert', lignes.count() == 4, lignes.count())
        verifier('Ajout : focus sur le champ d\'ajout', page.evaluate("document.activeElement.dataset.action") == 'ecran-ajout-input')
        cellules = lambda: page.locator('.crit-row').first.locator('.statut-cell:not(.statut-cell-tous)').count()
        verifier('Ajout : 4 colonnes dans la grille', cellules() == 4, cellules())
        verifier('Ajout : message', 'Ajout de « Profil »' in message(page), message(page))
        ajout.fill('profil')
        ajout.press('Enter')
        verifier('Ajout : doublon refusé', lignes.count() == 4 and 'déjà utilisé' in message(page), message(page))
        premier = page.locator('[data-action="rename-ecran"]').first
        premier.fill('Accueil v2')
        premier.press('Enter')
        etat = page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxal-state'))")
        verifier('Renommage : enregistré', etat['onglets'][0]['ecrans'][0]['nom'] == 'Accueil v2', etat['onglets'][0]['ecrans'][0]['nom'])
        premier = page.locator('[data-action="rename-ecran"]').first
        premier.fill('')
        premier.press('Enter')
        verifier('Renommage : nom vide refusé', page.locator('[data-action="rename-ecran"]').first.input_value() == 'Accueil v2' and 'obligatoire' in message(page), message(page))
        page.locator('[data-action="set-statut"][data-crit="raam-5-1"][data-statut="NC"]').nth(3).click()
        page.click('[data-action="valider-onglet"]')
        page.click('[data-action="modifier-onglet"]')
        page.click('summary:has-text("Écrans testés")') if not page.locator('.ecrans-panel').get_attribute('open') is not None else None
        suppr = page.locator('[data-action="delete-ecran"]').nth(3)
        suppr.click()
        verifier('Suppression : premier clic arme', page.locator('[data-action="delete-ecran"]').nth(3).inner_text() == 'Confirmer la suppression')
        page.locator('[data-action="delete-ecran"]').nth(3).click()
        etat = page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxal-state'))")
        o = etat['onglets'][0]
        verifier('Suppression : 3 écrans', len(o['ecrans']) == 3 and lignes.count() == 3, len(o['ecrans']))
        verifier('Suppression : résultats effacés, plus de NC', not any(r.get('statut') == 'NC' for e in o['resultats'].values() for r in e.values()))
        verifier('Suppression : onglet repassé en brouillon', o['valide'] is False)
        verifier('Suppression : message', 'Suppression de « Profil »' in message(page) and 'Jira' in message(page), message(page))
        for nom in ('P4', 'P5', 'P6', 'P7'):
            page.locator('[data-action="ecran-ajout-input"]').fill(nom)
            page.click('[data-action="add-ecran-onglet"]')
        rangs = page.locator('.crit-row')
        verifier('7 écrans : sélecteur affiché', page.locator('.ecran-selecteur').count() == 1)
        verifier('7 écrans : une seule colonne par critère', cellules() == 1, cellules())
        verifier('7 écrans : statut consolidé sur chaque critère', page.locator('.statut-consolide').count() == rangs.count(), (page.locator('.statut-consolide').count(), rangs.count()))
        verifier('7 écrans : écran ajouté affiché', page.locator('.ecran-selecteur [aria-pressed="true"]').inner_text().startswith('P7'))
        page.click('.ecran-selecteur [data-action="set-ecran-actif"] >> nth=1')
        verifier('7 écrans : choix d\'un autre', page.locator('.ecran-selecteur [aria-pressed="true"]').inner_text().startswith('Connexion'))
        page.locator('[data-action="set-statut"][data-crit="raam-5-1"][data-statut="NC"]').click()
        ligne = page.locator('.crit-row', has=page.locator('[data-crit="raam-5-1"]')).first
        verifier('7 écrans : consolidé NC', ligne.locator('.statut-consolide-val').inner_text() == 'NC' and '1 NC' in ligne.locator('.statut-consolide-detail').inner_text())
        verifier('7 écrans : compteur NC sur le sélecteur', '1 NC' in page.locator('.ecran-selecteur [aria-pressed="true"]').inner_text())
        page.locator('[data-action="delete-ecran"]').last.click()
        page.locator('[data-action="delete-ecran"]').last.click()
        verifier('6 écrans : retour à la grille', page.locator('.ecran-selecteur').count() == 0 and cellules() == 6, cellules())

        # --- Réinitialisation : la mémoire des exports est vidée
        page.click('#btnAide')
        page.click('[data-action="reset-audit"]')
        page.click('[data-action="reset-audit"]')
        etat = page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxal-state'))")
        verifier('Réinitialisation : mémoire Jira vidée', etat.get('exportesJira') == {} and etat.get('onglets') == [])

        verifier('Aucune erreur JavaScript', not erreurs, erreurs)
        navigateur.close()

    echecs = [r for r in resultats if not r[1]]
    print('\n%d contrôles, %d échec(s)' % (len(resultats), len(echecs)))
    return 1 if echecs else 0


if __name__ == '__main__':
    sys.exit(main())
