#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Tests de bout en bout de src/ruxaweb.html (Playwright, Chromium sans interface).

Installation (une fois) :
  python3 -m pip install playwright
  python3 -m playwright install chromium
Lancement :
  python3 tests/test_ruxaweb.py
Code retour 0 si tout passe, 1 sinon. L'outil est ouvert en file:// : aucun serveur n'est nécessaire.
"""
import json
import openpyxl
import pathlib
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = (ROOT / 'src' / 'ruxaweb.html').as_uri()
DATA = ROOT / 'data'

NB_REF = len(json.loads((DATA / 'criteres-raweb.json').read_text(encoding='utf-8'))['criteres'])
NB_BP = len(json.loads((DATA / 'bonnes-pratiques-web.json').read_text(encoding='utf-8'))['bonnes_pratiques'])
NB = NB_REF + NB_BP

resultats = []


def verifier(nom, condition, detail=''):
    resultats.append((nom, bool(condition), detail))
    print(('OK    ' if condition else 'ÉCHEC ') + nom + ('' if condition else ' , ' + str(detail)))


def ouvrir(page):
    page.goto(URL)
    page.evaluate("localStorage.clear()")
    page.reload()


def creer_onglet(page, type_audit='sip-rapide', ecrans=('Accueil', 'Contact', 'Actualités')):
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


def telechargement_octets(page, action):
    """Comme telechargement, mais renvoie le chemin du fichier produit (fichier binaire), ou None."""
    try:
        with page.expect_download(timeout=1500) as dl:
            action()
        cible = pathlib.Path(tempfile.mkdtemp()) / dl.value.suggested_filename
        dl.value.save_as(cible)
        return str(cible), dl.value.suggested_filename
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
        for libelle in ('Tickets Jira (CSV)', 'Liste des critères (Excel)', 'Données (JSON)'):
            f = telechargement(page, lambda: exporter(page, libelle))
            verifier('Export « %s » sans onglet : pas de fichier' % libelle, f is None, f and f[:80])
            verifier('Export « %s » sans onglet : message' % libelle, 'aucun onglet' in message(page), message(page))
        f = telechargement(page, lambda: page.click('#btnExportEtat'))
        verifier('Sauvegarder sans onglet : pas de fichier', f is None)
        verifier('Sauvegarder sans onglet : message', 'Rien à sauvegarder' in message(page), message(page))

        # --- Page Référentiel
        page.click('#btnReferentiel')
        verifier('Référentiel : %d fiches' % NB, page.locator('.ref-card').count() == NB, page.locator('.ref-card').count())
        verifier('Référentiel : %d pastilles d\'étape' % NB, page.locator('.etape-chip').count() == NB, page.locator('.etape-chip').count())
        verifier('Référentiel : consignes sans nom de règle Axe', '(règle' not in page.locator('#main').inner_text() and 'Lance Axe' not in page.locator('#main').inner_text())
        verifier('Référentiel : 24 « si présent »', page.locator('.si-present-chip').count() == 24, page.locator('.si-present-chip').count())
        page.click('#btnAide')
        aide = page.locator('#main').inner_text()
        verifier('Aide : version 1.5', 'RUXAWEB, version 1.5' in aide)
        verifier('Aide : section « Protocole de test »', 'Protocole de test' in aide and '4. Navigation au clavier' in aide and 'NVDA' in aide and 'iOS' not in aide)
        verifier('Aide : section « Noter les éléments »', 'Noter les éléments' in aide and 'Écran[type "Libellé"]' in aide and 'Pages testées' not in aide)
        verifier('Aide : déclencheurs web', 'cadre' in aide and 'autre langue' in aide)
        verifier('Aide : mémoire des exports Jira documentée', 'tout réexporter' in aide and 'pas réexporté automatiquement' in aide)

        # --- Onglet RAWeb : « Contenu des pages » (tout désactivé au départ)
        creer_onglet(page)
        nb_coeur = NB - 24
        verifier('Contenu des écrans : %d critères visibles au départ' % nb_coeur, page.locator('.crit-row').count() == nb_coeur, page.locator('.crit-row').count())
        verifier('Contenu des écrans : 20 critères masqués annoncés', '24 critère(s)' in page.locator('.presence-masques').inner_text())
        interrupteurs = page.evaluate("""() => [...document.querySelectorAll('[role=switch]')].map(b => b.id)""")
        verifier('Contenu des pages : 8 × 3 interrupteurs, sans session', len(interrupteurs) == 24, len(interrupteurs))
        verifier('Interrupteur : nom accessible', page.locator('[role=switch][data-decl="formulaire"]').first.get_attribute('aria-label') == 'Formulaire (Accueil)')
        for i in interrupteurs:
            page.click('#' + i)
        verifier('Tous les interrupteurs activés : %d critères' % NB, page.locator('.crit-row').count() == NB, page.locator('.crit-row').count())
        verifier('Interrupteur : aria-checked', page.locator('#' + interrupteurs[0]).get_attribute('aria-checked') == 'true')
        page.click('[role=switch][data-decl="formulaire"][data-ecran="%s"]' % page.locator('[role=switch][data-decl="formulaire"]').nth(1).get_attribute('data-ecran'))
        ligne_91 = page.locator('.crit-row', has=page.locator('[data-crit="raweb-11-1"]')).first
        verifier('Page sans formulaire : cellule « Absent »', ligne_91.locator('.statut-absent').count() == 1, ligne_91.locator('.statut-absent').count())
        page.click('[role=switch][data-decl="formulaire"][data-ecran="%s"]' % page.locator('[role=switch][data-decl="formulaire"]').nth(1).get_attribute('data-ecran'))

        # --- Vue par thème / par étape (tout le contenu activé)
        verifier('Vue par thème : %d pastilles d\'étape' % NB, page.locator('.crit-row .etape-chip').count() == NB)
        page.click('[data-action="set-vue-liste"][data-vue="etapes"]')
        groupes = page.locator('.theme-group-name').all_inner_texts()
        verifier('Vue par étape : 4 groupes', len(groupes) == 4, groupes)
        verifier('Vue par étape : un encart par groupe', page.locator('.etape-encart').count() == 4, page.locator('.etape-encart').count())
        par_etape = page.evaluate("""() => [...document.querySelectorAll('.theme-group')].map(g => g.querySelectorAll('.crit-row').length)""")
        verifier('Vue par étape : 16 / 11 / 19 / 10', par_etape == [16, 11, 19, 10], par_etape)
        chips = page.locator('.crit-row .etape-chip').all_inner_texts()
        verifier('Vue par étape : pastilles seulement pour 3a / 3b (19)', len(chips) == 19 and all(c[:2] in ('3a', '3b') for c in chips), chips[:3])
        verifier('Vue par étape : choix de thématisation masqué', page.locator('[data-action="set-theming"]').count() == 0)
        page.click('[data-action="set-vue-liste"][data-vue="themes"]')
        verifier('Retour vue par thème : %d critères' % NB, page.locator('.crit-row').count() == NB)

        # --- Jira : tous NT, puis C, puis NC ; « Élément concerné » ; mémoire des exports
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira, tous NT : pas de fichier', f is None)
        verifier('Jira, tous NT : message', 'aucun critère n\'a encore été testé' in message(page), message(page))
        page.click('[data-action="set-statut-tous"][data-crit="raweb-6-1"][data-statut="C"]')
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira, aucun NC : message', f is None and 'aucun critère n\'est non conforme' in message(page), message(page))
        page.click('[data-action="set-statut-tous"][data-crit="raweb-6-2"][data-statut="NC"]')
        verifier('NC : champ « Ticket Jira » absent', page.locator('[data-action="set-ticket-jira"]').count() == 0)
        champ = page.locator('[data-action="set-element-critere"][data-crit="raweb-6-2"]').first
        verifier('NC : champ « Élément concerné »', champ.count() == 1)
        champ.fill('Accueil[button "Valider"] | (disabled)')
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Jira : élément concerné repris, | remplacé par /', f and 'Accueil[button ""Valider""] / (disabled)' in f, f and f[:300])
        verifier('Jira sans support : Desktop et Mobile', f and '- Desktop: <to be completed>' in f and '- Mobile (responsive): <to be completed>' in f)
        verifier('Jira : lien RAWeb 1.1 crit-6-2', f and 'https://accessibilite.public.lu/en/raweb1.1/criteres.html#crit-6-2' in f and 'RAWeb 1.1, Criterion 6.2:' in f)
        verifier('Jira sans plateforme : 7 colonnes', f and f.splitlines()[0].count(',') == 6, f and f.splitlines()[0])
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Mémoire Jira : second export sans fichier', f is None)
        verifier('Mémoire Jira : message « déjà exporté »', 'Aucun nouveau ticket : 1 critère(s) non conforme(s) déjà exporté(s)' in message(page), message(page))
        page.click('[data-action="set-statut-tous"][data-crit="raweb-11-1"][data-statut="NC"]')
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('Mémoire Jira : seul le nouveau ticket', f and f.count(',Task,') == 1 and 'RAWeb-11.1' in f, f and f.count(',Task,'))
        verifier('Mémoire Jira : message « N déjà exportés, M nouveaux »', '1 ticket(s) déjà exporté(s), 1 nouveau(x)' in message(page), message(page))
        verifier('Mémoire Jira : enregistrée dans l\'état', page.evaluate("Object.keys(JSON.parse(localStorage.getItem('atelier-ruxaweb-state')).exportesJira).sort().join()") == 'raweb-11-1,raweb-6-2')
        for code, ligne, etiquette in (('desktop', '- Desktop:', ',desktop,'), ('mobile', '- Mobile (responsive):', ',mobile-web,')):
            page.click('#plateformeToggle [data-plateforme="%s"]' % code)
            presse = page.locator('#plateformeToggle [data-plateforme="%s"]' % code).get_attribute('aria-pressed')
            f = telechargement(page, lambda: exporter(page, 'Tickets Jira : tout réexporter'))
            autres = [x for x in ('- Desktop:', '- Mobile (responsive):') if x != ligne]
            verifier('Jira %s (tout réexporter) : 2 tickets' % code, f and f.count(',Task,') == 2)
            verifier('Jira %s : bouton enfoncé' % code, presse == 'true')
            verifier('Jira %s : seule la plateforme choisie' % code, f and ligne in f and not any(x in f for x in autres))
            verifier('Jira %s : étiquette et colonne Labels en plus' % code, f and etiquette in f and f.splitlines()[0].count(',') == 7)
        page.click('#plateformeToggle [data-plateforme="mobile"]')  # second clic : désélection
        verifier('Plateforme : second clic désélectionne', page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxaweb-state')).plateforme") == '')

        # --- Aide « Noter les éléments » : aller et retour vers le champ
        champ_id = page.locator('[data-action="set-element-critere"][data-crit="raweb-6-2"]').first.get_attribute('id')
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

        # --- Gestion des pages en cours d'audit, affichage un par un au-delà de 6
        ouvrir(page)
        creer_onglet(page)
        page.click('summary:has-text("Écrans testés")')
        lignes = page.locator('.ecrans-ligne')
        verifier('pages : panneau ouvert, 3 lignes', lignes.count() == 3, lignes.count())
        verifier('Audit rapide : suppression bloquée à 3', page.locator('[data-action="delete-ecran"]').first.is_disabled())
        ajout = page.locator('[data-action="ecran-ajout-input"]')
        ajout.fill('Panier')
        page.click('[data-action="add-ecran-onglet"]')
        verifier('Ajout : 4 lignes, panneau resté ouvert', lignes.count() == 4, lignes.count())
        verifier('Ajout : focus sur le champ d\'ajout', page.evaluate("document.activeElement.dataset.action") == 'ecran-ajout-input')
        cellules = lambda: page.locator('.crit-row').first.locator('.statut-cell:not(.statut-cell-tous)').count()
        verifier('Ajout : 4 colonnes dans la grille', cellules() == 4, cellules())
        verifier('Ajout : message', 'Ajout de « Panier »' in message(page), message(page))
        ajout.fill('panier')
        ajout.press('Enter')
        verifier('Ajout : doublon refusé', lignes.count() == 4 and 'déjà utilisé' in message(page), message(page))
        premier = page.locator('[data-action="rename-ecran"]').first
        premier.fill('Accueil v2')
        premier.press('Enter')
        etat = page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxaweb-state'))")
        verifier('Renommage : enregistré', etat['onglets'][0]['ecrans'][0]['nom'] == 'Accueil v2', etat['onglets'][0]['ecrans'][0]['nom'])
        premier = page.locator('[data-action="rename-ecran"]').first
        premier.fill('')
        premier.press('Enter')
        verifier('Renommage : nom vide refusé', page.locator('[data-action="rename-ecran"]').first.input_value() == 'Accueil v2' and 'obligatoire' in message(page), message(page))
        page.locator('[data-action="set-statut"][data-crit="raweb-6-2"][data-statut="NC"]').nth(3).click()
        page.click('[data-action="valider-onglet"]')
        page.click('[data-action="modifier-onglet"]')
        page.click('summary:has-text("Écrans testés")') if not page.locator('.ecrans-panel').get_attribute('open') is not None else None
        suppr = page.locator('[data-action="delete-ecran"]').nth(3)
        suppr.click()
        verifier('Suppression : premier clic arme', page.locator('[data-action="delete-ecran"]').nth(3).inner_text() == 'Confirmer la suppression')
        page.locator('[data-action="delete-ecran"]').nth(3).click()
        etat = page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxaweb-state'))")
        o = etat['onglets'][0]
        verifier('Suppression : 3 pages', len(o['ecrans']) == 3 and lignes.count() == 3, len(o['ecrans']))
        verifier('Suppression : résultats effacés, plus de NC', not any(r.get('statut') == 'NC' for e in o['resultats'].values() for r in e.values()))
        verifier('Suppression : onglet repassé en brouillon', o['valide'] is False)
        verifier('Suppression : message', 'Suppression de « Panier »' in message(page) and 'Jira' in message(page), message(page))
        for nom in ('P4', 'P5', 'P6', 'P7'):
            page.locator('[data-action="ecran-ajout-input"]').fill(nom)
            page.click('[data-action="add-ecran-onglet"]')
        rangs = page.locator('.crit-row')
        barre = page.locator('.barre-audit')
        verifier('Sélecteur : dans la barre flottante (sticky)', barre.count() == 1 and barre.locator('.ecran-selecteur').count() == 1 and barre.evaluate("b => getComputedStyle(b).position") == 'sticky')
        page.locator('.crit-row').nth(25).scroll_into_view_if_needed()
        verifier('Sélecteur : visible après défilement', barre.bounding_box()['y'] >= 0 and barre.bounding_box()['y'] < 40, barre.bounding_box())
        page.click('.ecran-nav[data-nav="prec"]')
        verifier('Écran précédent : P6 affiché', page.locator('.ecran-selecteur [aria-pressed="true"]').inner_text().startswith('P6'))
        page.click('.ecran-nav[data-nav="suiv"]')
        verifier('Écran suivant : P7, bouton Suivant désactivé', page.locator('.ecran-selecteur [aria-pressed="true"]').inner_text().startswith('P7') and page.locator('.ecran-nav[data-nav="suiv"]').is_disabled())
        verifier('7 pages : sélecteur affiché', page.locator('.ecran-selecteur').count() == 1)
        verifier('7 pages : une seule colonne par critère', cellules() == 1, cellules())
        verifier('7 pages : statut consolidé sur chaque critère', page.locator('.statut-consolide').count() == rangs.count(), (page.locator('.statut-consolide').count(), rangs.count()))
        verifier('7 pages : écran ajouté affiché', page.locator('.ecran-selecteur [aria-pressed="true"]').inner_text().startswith('P7'))
        page.click('.ecran-selecteur .preset-chip >> nth=1')
        verifier('7 pages : choix d\'un autre', page.locator('.ecran-selecteur [aria-pressed="true"]').inner_text().startswith('Contact'))
        page.locator('[data-action="set-statut"][data-crit="raweb-6-2"][data-statut="NC"]').click()
        ligne = page.locator('.crit-row', has=page.locator('[data-crit="raweb-6-2"]')).first
        verifier('7 pages : consolidé NC', ligne.locator('.statut-consolide-val').inner_text() == 'NC' and '1 NC' in ligne.locator('.statut-consolide-detail').inner_text())
        verifier('7 pages : compteur NC sur le sélecteur', '1 NC' in page.locator('.ecran-selecteur [aria-pressed="true"]').inner_text())
        page.locator('[data-action="delete-ecran"]').last.click()
        page.locator('[data-action="delete-ecran"]').last.click()
        verifier('6 pages : retour à la grille', page.locator('.ecran-selecteur').count() == 0 and cellules() == 6, cellules())

        # --- Critère 13.11 : officiel, hors sélection du SIP, hors taux
        ouvrir(page)
        page.click('#btnReferentiel')
        verifier('13.11 : une fiche hors sélection au Référentiel', page.locator('.ref-card', has_text='Hors sélection SIP').count() == 1)
        verifier('Référentiel : compte « 52 critères + 1 hors sélection »', '52 critères du RAWeb 1.1 (audit simplifié du SIP) + 1 critère RAWeb hors sélection' in page.locator('#main').inner_text())
        creer_onglet(page)
        for b in page.locator('[data-action="set-statut-theme"][data-statut="C"]').all():
            b.click()
        taux_avant = page.locator('.taux-preview').inner_text()
        page.click('[data-action="set-statut-tous"][data-crit="raweb-13-11"][data-statut="NC"]')
        taux_apres = page.locator('.taux-preview').inner_text()
        verifier('13.11 NC : taux inchangé (100 %)', '100%' in taux_avant and '100%' in taux_apres, (taux_avant, taux_apres))
        ligne = page.locator('.crit-row', has=page.locator('[data-crit="raweb-13-11"]')).first
        verifier('13.11 : pastilles RAWeb 13.11 et hors sélection', 'RAWeb 13.11' in ligne.inner_text() and 'Hors sélection SIP' in ligne.inner_text())
        f = telechargement(page, lambda: exporter(page, 'Tickets Jira (CSV)'))
        verifier('13.11 : ticket Jira avec lien officiel', f and 'RAWeb-13.11' in f and 'criteres.html#crit-13-11' in f, f and f[:200])
        x = telechargement_octets(page, lambda: exporter(page, 'Liste des critères (Excel)'))
        valeurs = [c.value for r in openpyxl.load_workbook(x[0]).active.iter_rows() for c in r] if x else []
        verifier('13.11 : liste Excel marquée hors taux', '13.11 (hors sélection SIP, hors taux)' in valeurs)
        f = telechargement(page, lambda: exporter(page, 'Données (JSON)'))
        c1311 = [c for c in json.loads(f)['onglets'][0]['criteres'] if c['id'] == 'raweb-13-11'] if f else []
        verifier('13.11 : export JSON horsSelectionSip', c1311 and c1311[0]['horsSelectionSip'] is True and c1311[0]['statut'] == 'NC')

        # --- Export Excel de la liste, sans mention d'une application tierce
        ouvrir(page)
        creer_onglet(page)
        page.click('[data-action="set-statut-tous"][data-crit="raweb-10-10"][data-statut="NC"]')
        champ = page.locator('[data-action="set-commentaire-critere"][data-crit="raweb-10-10"]').first
        champ.fill('Défaut ; avec "guillemets", virgule\net retour à la ligne <balise> & esperluette')
        x = telechargement_octets(page, lambda: exporter(page, 'Liste des critères (Excel)'))
        verifier('Excel : fichier .xlsx produit', x and x[1].endswith('.xlsx'), x and x[1])
        if x:
            ws = openpyxl.load_workbook(x[0]).active
            entetes = [c.value for c in ws[1]]
            verifier('Excel : en-têtes', entetes[:3] == ["Onglet (type d'audit)", entetes[1], 'RAWeb'] and "Type d'audit" not in entetes and 'Gravité' in entetes and 'Statut' in entetes, entetes)
            verifier('Excel : une ligne par critère', ws.max_row == NB + 1, ws.max_row)
            col_ref, col_statut = entetes.index('RAWeb'), entetes.index('Statut')
            refs = [r[col_ref].value for r in ws.iter_rows(min_row=2)]
            verifier('Excel : numéros gardés en texte (10.1, 10.10…)', all(isinstance(v, str) for v in refs) and '10.10' in refs and '11.10' in refs, refs[:5])
            ligne = [r for r in ws.iter_rows(min_row=2) if r[col_statut].value == 'NC']
            verifier('Excel : statut NC coloré', ligne and ligne[0][col_statut].fill.fgColor.rgb == 'FFFBE5E2', ligne and ligne[0][col_statut].fill.fgColor.rgb)
            verifier('Excel : commentaire intact (caractères spéciaux, retour à la ligne)', ligne and ligne[0][-1].value == 'Accueil : Défaut ; avec "guillemets", virgule\net retour à la ligne <balise> & esperluette', ligne and ligne[0][-1].value)
            verifier('Excel : ligne d\'en-tête figée et filtre', ws.freeze_panes == 'A2' and ws.auto_filter.ref is not None, (ws.freeze_panes, ws.auto_filter.ref))
            verifier('Excel : largeur de la colonne Critère', ws.column_dimensions['G'].width >= 60, ws.column_dimensions['G'].width)
            verifier('Excel : onglet audit rapide sans type répété', ws['A2'].value == ws['A2'].value.split(' (')[0], ws['A2'].value)
        verifier('Messages sans mention de Claude', 'claude' not in message(page).lower(), message(page))
        page.click('#btnReferentiel')
        x = telechargement_octets(page, lambda: page.click('[data-action="export-ref-pdf"]'))
        verifier('PDF : téléchargé, message sans Claude', x and x[1].endswith('.pdf') and 'claude' not in page.locator('#refStatus').inner_text().lower(), page.locator('#refStatus').inner_text())
        verifier('Page : aucune mention de Claude', 'claude' not in page.content().lower())

        # --- Réinitialisation : la mémoire des exports est vidée
        page.click('#btnAide')
        page.click('[data-action="reset-audit"]')
        page.click('[data-action="reset-audit"]')
        etat = page.evaluate("JSON.parse(localStorage.getItem('atelier-ruxaweb-state'))")
        verifier('Réinitialisation : mémoire Jira vidée', etat.get('exportesJira') == {} and etat.get('onglets') == [])

        verifier('Aucune erreur JavaScript', not erreurs, erreurs)
        navigateur.close()

    echecs = [r for r in resultats if not r[1]]
    print('\n%d contrôles, %d échec(s)' % (len(resultats), len(echecs)))
    return 1 if echecs else 0


if __name__ == '__main__':
    sys.exit(main())
