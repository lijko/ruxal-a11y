#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Bertrand Kempf
# SPDX-License-Identifier: EUPL-1.2
"""Génère exemples/donnees-fictives-ruxaweb.json : un projet RUXAWEB de démonstration, données fictives.

Le projet est saisi dans l'outil lui-même (Playwright), comme le ferait un testeur : fonctions primaires,
audit simple sur 3 écrans, scénario d'achat, observations, statuts posés dans la grille, puis sauvegarde
par Fichier > Sauvegarder le projet. Le fichier a donc toujours le format de la version courante.
Usage : python3 scripts/demo_ruxaweb.py
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = (ROOT / 'src' / 'ruxaweb.html').as_uri()
SORTIE = ROOT / 'exemples' / 'donnees-fictives-ruxaweb.json'


def audit(page):
    page.click('#onglet-nav .onglet-tab[aria-current="page"]')


def ecran(page, i):
    audit(page)
    page.locator('.ecrans [data-action="ecran"]').nth(i).click()


def fonction(page, fid):
    audit(page)
    page.click('.ecrans [data-action="cible-fonction"][data-id="%s"]' % fid)


def observer(page, texte, point=None, element=None, type_el=None, tag='nc', attendu='', crit=None, ecrans=()):
    page.fill('#obs-texte', texte)
    if point:
        page.select_option('#obs-point', point)
    if type_el is not None and page.locator('#obs-element').count():
        page.select_option('#obs-element', str(type_el))
    if crit:
        page.select_option('#obs-ajout', crit)
    if element and page.locator('#obs-partage-nom').count():
        page.fill('#obs-partage-nom', element)
    for i in ecrans:
        page.locator('[data-ecran-partage]').nth(i).check()
    if attendu:
        page.fill('#obs-attendu', attendu)
    page.click('[data-action="tag"][data-tag="%s"]' % tag)
    page.click('#form-obs button[type=submit]')


def main():
    with sync_playwright() as p:
        page = p.chromium.launch().new_page(viewport={'width': 1360, 'height': 900}, accept_downloads=True)
        page.goto(URL)
        page.evaluate('localStorage.clear()')
        page.reload()
        page.fill('#audit-nom', 'Boutique Démo (données fictives)')
        page.locator('#audit-nom').blur()
        for f in ('nav', 'recherche', 'pied', 'modale'):
            page.click('.liste-fonctions [data-id="%s"]' % f)

        # Audit simple : accueil, connexion, fiche produit.
        page.click('[data-action="nouvel-onglet"][data-type="rapide"]')
        page.fill('#onglet-nom', 'Audit des pages clés')
        page.locator('#onglet-nom').blur()
        for i, nom in enumerate(('Accueil', 'Connexion', 'Fiche produit')):
            champ = page.locator('[data-ecran-nom]').nth(i)
            champ.fill(nom)
            champ.blur()
        page.click('[data-action="contenu"][data-d="formulaire"] >> nth=1')
        page.click('[data-action="contenu"][data-d="image-complexe"] >> nth=2')
        page.locator('[data-fonction-ecran="modale"]').nth(2).uncheck()
        page.click('main [data-action="vue"][data-vue="audit"]')

        # Fonctions primaires : testées une fois pour tout le projet.
        fonction(page, 'nav')
        observer(page, 'On ne voit pas où se trouve le focus en tabulant dans le menu principal.', point='focus-invisible',
                 attendu='Un indicateur de focus visible, contrasté, sur chaque lien du menu.')
        observer(page, "L'état « page en cours » du menu n'est signalé que par la couleur.", point='couleur-seule')
        fonction(page, 'recherche')
        observer(page, 'Le bouton loupe est annoncé « bouton » sans nom par le lecteur d\'écran.', point='nom-absent', type_el=5,
                 attendu='Le bouton est annoncé « Rechercher ».')
        fonction(page, 'pied')
        observer(page, 'Les liens du pied de page sont explicites et le contraste est suffisant.', point='nom-non-pertinent', type_el=2, tag='c')
        fonction(page, 'modale')
        observer(page, 'Impossible de sortir de la fenêtre de connexion au clavier.', point='piege',
                 attendu='Échap ferme la fenêtre et le focus revient sur le bouton « Se connecter ».')

        # Écrans.
        ecran(page, 0)
        observer(page, 'Le carrousel de promotions défile seul, sans bouton pause.', point='mouvement', element='Carrousel promotions')
        observer(page, 'Texte gris clair sur fond blanc dans le bandeau « Livraison offerte », presque illisible.', point='contraste', type_el=0,
                 element='Bandeau livraison', attendu='Un contraste d\'au moins 4,5:1.')
        observer(page, 'Le titre de la page est « Accueil » sans le nom du site.', point='titre-ecran', tag='nc')
        ecran(page, 1)
        observer(page, "Le champ e-mail n'a pas d'étiquette, seulement un texte indicatif qui disparaît à la saisie.", point='etiquette',
                 element='input "E-mail"', attendu='Une étiquette visible « Adresse e-mail », liée au champ.')
        observer(page, "Le message « mot de passe incorrect » s'affiche mais n'est pas restitué par le lecteur d'écran.", point='message-non-restitue',
                 type_el=0)
        ecran(page, 2)
        observer(page, 'Le graphique des avis clients n\'a pas de description détaillée.', point='image-complexe', element='Graphique des avis')
        observer(page, 'Pas de tableau de données sur cet écran.', crit='raweb-5-6', tag='na')
        observer(page, 'Note : vérifier avec l\'équipe si la zone « Vous aimerez aussi » est chargée après coup.', tag='nc')

        # Grille : quelques critères posés conformes sans observation.
        audit(page)
        page.click('[data-action="vue"][data-vue="grille"]')
        for cid in ('raweb-8-1', 'raweb-8-3', 'raweb-8-5', 'raweb-9-2'):
            ligne = page.locator('tbody tr', has=page.locator('[data-action="critere"][data-id="%s"]' % cid))
            if not ligne.count():
                continue
            ligne.locator('[data-action="critere"]').click()
            if page.locator('#dlg [data-action="clo-tous"]').count():
                page.click('#dlg [data-action="clo-tous"]')
            page.click('#dlg [data-action="fermer-dlg"]')

        # Scénario : tunnel d'achat.
        page.click('[data-action="accueil"]')
        page.click('[data-action="nouvel-onglet"][data-type="scenario"]')
        page.fill('#onglet-nom', 'Achat d\'un produit')
        page.locator('#onglet-nom').blur()
        page.click('[data-action="ajout-ecran"]')
        for i, nom in enumerate(('Panier', 'Livraison', 'Paiement', 'Confirmation')):
            champ = page.locator('[data-ecran-nom]').nth(i)
            champ.fill(nom)
            champ.blur()
        page.click('[data-action="contenu"][data-d="formulaire"] >> nth=1')
        page.click('[data-action="contenu"][data-d="formulaire"] >> nth=2')
        page.click('main [data-action="vue"][data-vue="audit"]')
        ecran(page, 1)
        page.fill('#obs-texte', 'Après « Continuer », le focus reste sur le bouton au lieu de passer au titre de l\'étape Paiement.')
        page.select_option('#obs-point', 'ordre-focus')
        page.select_option('#obs-vers', index=2)
        page.click('#form-obs button[type=submit]')
        ecran(page, 2)
        observer(page, 'La session expire au bout de 5 minutes sans avertissement, le panier est vidé.', point='limite-temps',
                 attendu='Un avertissement avant expiration, avec la possibilité de prolonger.')
        # Lecture UX/POUR.
        audit(page)
        if page.locator('#parcours-liste').is_hidden():
            page.click('[data-action="parcours-bascule"]')
        page.click('#parcours-liste [data-vue="ux"]')
        n = page.locator('[data-action="heur"][data-v="succes"]').count()
        for i in range(n):
            v = 'difficile' if i in (2, 5) else 'succes'
            page.locator('[data-action="heur"][data-v="%s"]' % v).nth(i).click()
        com = page.locator('textarea[data-heur-com]')
        for i in (2, 5):
            if com.count() > i:
                com.nth(i).fill('Le retour arrière depuis Paiement vide le formulaire de livraison.')
                com.nth(i).blur()

        with page.expect_download() as dl:
            page.click('#btn-menu')
            page.click('[data-action="export-json"]')
        SORTIE.parent.mkdir(exist_ok=True)
        dl.value.save_as(SORTIE)
        etat = page.evaluate('RUXAWEB.state()')
        print('Écrit :', SORTIE.relative_to(ROOT), '(%d onglets, %d observations d\'écran, %d observations de fonctions)' % (
            len(etat['onglets']), sum(len(o['obs']) for o in etat['onglets']), len(etat.get('obsF', []))))


if __name__ == '__main__':
    main()
