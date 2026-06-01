# AR - Fourniture Bureau


> Documentation du module de demande de fournitures de bureau.


## Vue d?ensemble

Le module permet aux collaborateurs de demander des fournitures, avec validation manager N+1 puis traitement par les personnes habilit?es. Il contient un catalogue d?articles, des lignes de demande, des traiteurs et une documentation m?tier.

## Utilisateurs concern?s

- Demandeur : cr?e et soumet la demande.
- Manager N+1 : approuve ou refuse.
- Traiteur : pr?pare et livre les fournitures.
- Administrateur : maintient articles et personnes de traitement.

## Workflow m?tier

1. Nouvelle
2. Validation N+1
3. Traitement
4. Livr?e
5. Refus?e

## Fonctionnement op?rationnel

- Cr?er une demande avec les articles et quantit?s.
- Soumettre au manager.
- Le manager approuve ou refuse.
- Le traiteur prend en charge la pr?paration.
- Marquer la demande comme livr?e apr?s r?ception.

## Configuration recommand?e

- Cr?er les articles de fourniture.
- Cr?er les personnes habilit?es au traitement.
- V?rifier la relation employ?-utilisateur-manager.
- Configurer les groupes et r?gles d?enregistrement.

## D?pendances Odoo

- `base`
- `hr`
- `mail`

## Mod?les techniques

- `ar.fb.article` : Article fourniture bureau (`models/article.py`)
- `ar.fb.demande` : Demande fourniture bureau (`models/demande.py`)
- `ar.fb.demande.line` : Ligne demande fourniture (`models/demande.py`)
- `ar.fb.documentation` : FB - Documentation (`models/documentation.py`)
- `ar.fb.traiteur` : Personnes qui traitent (`models/traite_person.py`)

## ?tats d?tect?s dans le code

- `models/demande.py` : `new` (Nouvelle), `n1` (Validation N+1), `processing` (Traitement), `received` (Livrée), `refused` (Refusée)

## Actions serveur principales

- `action_submit_n1` (`models/demande.py`)
- `action_approve_n1` (`models/demande.py`)
- `action_refuse` (`models/demande.py`)
- `action_received` (`models/demande.py`)

## Fichiers charg?s par le manifest

- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`
- `data/mail_templates.xml`
- `views/article_views.xml`
- `views/traite_person_views.xml`
- `views/demande_views.xml`
- `views/documentation_views.xml`
- `views/menus.xml`

## S?curit? et droits

Le module s?appuie sur les fichiers suivants pour d?finir les groupes, r?gles d?enregistrement et droits d?acc?s :

- `security/ir.model.access.csv`
- `security/record_rules.xml`
- `security/security.xml`

## Assets et interface

- `static/src/js/fourniture_bureau_animations.js`
- `static/src/scss/fourniture_bureau_kanban.scss`

## Bonnes pratiques d?utilisation

- V?rifier que chaque utilisateur Odoo est li? au bon employ? lorsque le module d?pend de `hr.employee`.
- Tester le workflow avec un dossier de test avant utilisation en production.
- Contr?ler les groupes de s?curit? apr?s installation afin que seuls les bons r?les voient les boutons de validation.
- Garder les templates e-mail et rapports align?s avec les proc?dures internes.
- Sauvegarder la base avant toute modification structurelle du module.

## Maintenance

- Les ?volutions fonctionnelles doivent ?tre ajout?es dans les mod?les Python, les vues XML et les r?gles de s?curit? correspondantes.
- Apr?s modification des vues, mettre ? jour le module depuis Odoo ou red?marrer le serveur selon le type de changement.
- Apr?s modification des assets, vider le cache navigateur et recompiler les assets si n?cessaire.
- Toute nouvelle ?tape de workflow doit ?tre accompagn?e des droits, boutons, notifications et filtres correspondants.
