# AR - Fourniture Bureau

Module Odoo pour les demandes de fournitures de bureau avec validation N+1, traitement et reception.

## Objectif

Cette documentation explique le perimetre fonctionnel du module, les roles utilisateurs, le workflow, la configuration et les principaux objets techniques.

## Utilisateurs concernes

- Demandeur
- Manager N+1
- Traiteur fournitures
- Administrateur Odoo

## Workflow metier

1. Nouvelle
2. Validation N+1
3. Traitement
4. Livree
5. Refusee

## Fonctionnement operationnel

- Creer une demande avec articles et quantites.
- Soumettre au manager.
- Valider ou refuser.
- Traiter la preparation.
- Marquer comme livree.

## Configuration recommandee

- Creer les articles de fourniture.
- Creer les personnes de traitement.
- Verifier employes et managers.
- Configurer groupes et record rules.

## Dependances Odoo

- `base`
- `mail`
- `hr`

## Modeles principaux

- `ar.fb.demande`
- `ar.fb.demande.line`
- `ar.fb.article`
- `ar.fb.traiteur`
- `ar.fb.documentation`

## Structure importante du module

- `security/ir.model.access.csv`
- `security/record_rules.xml`
- `security/security.xml`
- `data/mail_templates.xml`
- `views/article_views.xml`
- `views/demande_views.xml`
- `views/documentation_views.xml`
- `views/menus.xml`
- `views/traite_person_views.xml`
- `models/__init__.py`
- `models/article.py`
- `models/demande.py`
- `models/documentation.py`
- `models/traite_person.py`

## Securite

Les droits sont geres par les fichiers du dossier `security`. Il faut verifier les groupes, les regles enregistrement et les acces CSV apres installation ou modification du module.

## Notifications et suivi

Les modules qui dependent de `mail` utilisent le chatter Odoo pour tracer les changements. Les templates mail presents dans le dossier `data` servent a notifier les acteurs concernes par les transitions.

## Installation

1. Copier le module dans le dossier addons Odoo.
2. Redemarrer le serveur Odoo si necessaire.
3. Mettre a jour la liste des applications.
4. Installer ou mettre a jour le module.
5. Verifier les droits utilisateurs et tester un dossier de bout en bout.

## Maintenance

- Ajouter toute nouvelle etape a la fois dans le modele Python, les vues XML, les droits et les notifications.
- Tester les workflows avec plusieurs roles utilisateurs.
- Mettre a jour les rapports et templates mail quand la procedure interne change.
- Eviter de modifier les donnees de production sans sauvegarde.
- Documenter toute evolution fonctionnelle dans ce README.
