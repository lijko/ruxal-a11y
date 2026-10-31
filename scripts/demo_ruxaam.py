#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Génère exemples/donnees-fictives-ruxaam.json : une sauvegarde RUXAAM de démonstration, données fictives.

L'audit est saisi dans l'outil lui-même (Playwright), comme le ferait un testeur, puis sauvegardé
par le bouton « Sauvegarder » : le fichier a donc toujours le format attendu par la version courante.
Usage : python3 scripts/demo_ruxaam.py
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = (ROOT / 'src' / 'ruxaam.html').as_uri()
SORTIE = ROOT / 'exemples' / 'donnees-fictives-ruxaam.json'

# Non-conformités fictives : critère -> (élément, commentaire, écrans touchés, None = tous)
NC = {
    'raam-5-1': ('[Menu principal]', 'Le bouton menu est annoncé « bouton » sans nom par TalkBack.', None),
    'raam-2-1': ('Accueil[link "Promotions"]', "Les promotions actives ne sont signalées que par la couleur rouge du libellé.", [0]),
    'raam-10-1': ('Profil[button "Enregistrer"]', "Après enregistrement, le focus revient en haut de l'écran au lieu du message de confirmation.", [2]),
    'raam-11-9': ('Connexion', "L'écran reste bloqué en portrait : en paysage, le formulaire est tronqué.", [1]),
}


def main():
    with sync_playwright() as p:
        page = p.chromium.launch().new_page(viewport={'width': 1360, 'height': 900}, accept_downloads=True)
        page.goto(URL)
        page.evaluate('localStorage.clear()')
        page.reload()
        page.fill('#auditNomInput', 'Appli Démo (données fictives)')
        page.locator('#auditNomInput').blur()
        page.click('#plateformeToggle [data-plateforme="android"]')

        # Audit rapide RAAM sur trois écrans.
        page.click('#btnDashboard')
        page.click('[data-action="goto-scenario"]')
        page.click('[data-scenario="sip-rapide"]')
        champs = page.locator('input[placeholder^="Nom de l"]')
        for i, nom in enumerate(('Accueil', 'Connexion', 'Profil')):
            while champs.count() <= i:
                page.get_by_role('button', name='+ Ajouter un écran').click()
            champs.nth(i).fill(nom)
        page.get_by_role('button', name="Créer l'onglet").click()

        # Tout ce qui est visible passe conforme, sauf les non-conformités ci-dessus.
        crits = page.evaluate("[...new Set([...document.querySelectorAll('[data-action=\"set-statut-tous\"][data-statut=\"C\"]')].map(b => b.dataset.crit))]")
        for c in crits:
            if c in NC:
                continue
            page.click('[data-action="set-statut-tous"][data-crit="%s"][data-statut="C"]' % c)
        absents = [c for c in NC if c not in crits]
        if absents:
            print('Non-conformités ignorées (critères non affichés) :', absents)
        for c, (element, commentaire, ecrans) in NC.items():
            if c not in crits:
                continue
            if ecrans is None:
                page.click('[data-action="set-statut-tous"][data-crit="%s"][data-statut="NC"]' % c)
            else:
                for i in ecrans:
                    page.locator('[data-action="set-statut"][data-crit="%s"][data-statut="NC"]' % c).nth(i).click()
            el = page.locator('[data-action="set-element-critere"][data-crit="%s"]' % c)
            if el.count():
                el.first.fill(element)
                el.first.blur()
            com = page.locator('[data-action="set-commentaire-critere"][data-crit="%s"]' % c)
            if com.count():
                com.first.fill(commentaire)
                com.first.blur()

        # Scénario : parcours de souscription, lecture POUR/UX.
        page.click('#btnDashboard')
        page.click('[data-action="goto-scenario"]')
        page.click('[data-scenario="flow"]')
        page.fill('input[placeholder^="Ex. Souscription"]', 'Souscription à une offre')
        champs = page.locator('input[placeholder^="Nom de l\'étape"]')
        for i, nom in enumerate(('Offres', 'Formulaire', 'Paiement', 'Confirmation')):
            while champs.count() <= i:
                page.get_by_role('button', name='+ Ajouter une étape').click()
            champs.nth(i).fill(nom)
        page.get_by_role('button', name="Créer l'onglet").click()
        # Un défaut de parcours côté RAAM, sur l'étape Paiement.
        b = page.locator('[data-action="set-statut"][data-crit="raam-10-1"][data-statut="NC"]')
        if b.count() >= 3:
            b.nth(2).click()
            el = page.locator('[data-action="set-element-critere"][data-crit="raam-10-1"]')
            if el.count():
                el.first.fill('Formulaire -> Paiement')
                el.first.blur()
        page.click('[data-action="set-vue-audit"][data-vue="pourux"]')
        heur = page.evaluate("[...new Set([...document.querySelectorAll('[data-action=\"set-heur\"]')].map(b => b.dataset.h))]")
        valeurs = page.evaluate("[...new Set([...document.querySelectorAll('[data-action=\"set-heur\"]')].map(b => b.dataset.v))]")
        for i, h in enumerate(heur):
            v = valeurs[0] if i % 4 else (valeurs[1] if len(valeurs) > 1 else valeurs[0])
            page.click('[data-action="set-heur"][data-h="%s"][data-v="%s"]' % (h, v))
            com = page.locator('[data-action="set-commentaire-heur"][data-h="%s"]' % h)
            if com.count():
                com.first.fill("Étape Paiement : le retour arrière vide le formulaire, il faut tout ressaisir.")
                com.first.blur()

        with page.expect_download() as dl:
            page.click('#btnExportEtat')
        SORTIE.parent.mkdir(exist_ok=True)
        dl.value.save_as(SORTIE)
        print('Écrit :', SORTIE.relative_to(ROOT), '(%d critères conformes, %d non-conformités)' % (len(crits) - len([c for c in NC if c in crits]), len([c for c in NC if c in crits])))


if __name__ == '__main__':
    main()
