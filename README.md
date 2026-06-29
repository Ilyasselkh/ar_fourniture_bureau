# AR - Fourniture Bureau

Module Odoo de gestion des demandes de fournitures de bureau.

Le module couvre la demande par collaborateur, la validation Manager N+1, le traitement par les personnes de traitement et la confirmation de livraison.

## Objectif fonctionnel

Centraliser les demandes de fournitures et tracer leur traitement de bout en bout.

Le module permet de :

- creer une demande de fournitures ;
- ajouter des articles et quantites ;
- rattacher automatiquement le demandeur, son departement et son Manager N+1 ;
- soumettre la demande au Manager N+1 ;
- valider ou refuser la demande ;
- faire traiter la demande par une personne habilitee ;
- marquer la demande comme livree ;
- notifier les acteurs par email ;
- tracer les changements dans le chatter.

## Roles fonctionnels

### Demandeur

Le demandeur initie la demande.

Il peut :

- creer une demande ;
- ajouter les lignes d'articles ;
- joindre des pieces si necessaire ;
- soumettre la demande ;
- suivre l'etat ;
- recevoir la notification de livraison ou de refus.

### Manager N+1

Le Manager N+1 valide ou refuse la demande.

Condition importante : l'utilisateur doit etre le Manager N+1 reel du demandeur.

### Traiteur fournitures

Le traiteur prepare et livre les fournitures.

Il doit etre declare dans le referentiel des personnes de traitement et etre disponible.

Il peut :

- consulter les demandes validees ;
- traiter la preparation ;
- marquer la demande comme livree ;
- refuser depuis l'etape de traitement si necessaire.

### Administrateur

L'administrateur maintient les articles, les traiteurs, la documentation et les droits.

## Etats du workflow

Les etats principaux sont :

- `Nouvelle`
- `Validation N+1`
- `Traitement`
- `Livree`
- `Refusee`

## Flux de validation

1. `Nouvelle`
2. `Validation N+1`
3. `Traitement`
4. `Livree`

Un refus est possible depuis :

- `Validation N+1` par le Manager N+1 ;
- `Traitement` par une personne de traitement autorisee.

## Donnees de reference

Le module utilise :

- un catalogue d'articles ;
- un referentiel des traiteurs ;
- une documentation interne.

Les traiteurs doivent etre lies a un employe Odoo et marques comme disponibles pour recevoir les demandes.

## Notifications

Les templates email couvrent notamment :

- nouvelle demande vers Manager N+1 ;
- demande approuvee vers demandeur ;
- demande en traitement vers traiteurs ;
- demande livree vers demandeur ;
- demande refusee vers demandeur.

Fichier principal :

- `data/mail_templates.xml`

## Securite et droits

Les droits sont definis dans :

- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`

Points de controle :

- seul le demandeur modifie une demande nouvelle ;
- seul le Manager N+1 valide a l'etape N+1 ;
- seuls les traiteurs disponibles traitent les demandes ;
- les demandes livrees ou refusees ne doivent plus etre modifiees.

## Modeles principaux

- `ar.fb.demande`
- `ar.fb.demande.line`
- `ar.fb.article`
- `ar.fb.traiteur`
- `ar.fb.documentation`

## Structure du module

- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`
- `data/mail_templates.xml`
- `views/article_views.xml`
- `views/traite_person_views.xml`
- `views/demande_views.xml`
- `views/documentation_views.xml`
- `views/menus.xml`
- `models/article.py`
- `models/demande.py`
- `models/traite_person.py`
- `models/documentation.py`
- `static/src/scss/fourniture_bureau_kanban.scss`
- `static/src/js/fourniture_bureau_animations.js`

## Installation

1. Copier le module dans le dossier addons Odoo.
2. Redemarrer le serveur Odoo si necessaire.
3. Mettre a jour la liste des applications.
4. Installer le module.
5. Creer les articles de fournitures.
6. Declarer les traiteurs disponibles.
7. Verifier les managers dans les fiches employes.
8. Tester une demande complete.

## Maintenance fonctionnelle

Lorsqu'une regle change, verifier aussi :

- les boutons de workflow ;
- les record rules ;
- les templates email ;
- le referentiel des traiteurs ;
- ce README.
