# AR - Fourniture Bureau

Module Odoo de gestion des demandes de fournitures de bureau.

## Objectif

Ce module permet aux collaborateurs de demander des fournitures, de faire valider la demande par le manager N+1, puis de suivre le traitement et la livraison par les personnes habilitées.

## Dépendances

- `base`
- `hr`
- `mail`

## Modèles principaux

- `ar.fb.demande` : demande de fourniture.
- `ar.fb.demande.line` : lignes d'articles demandés.
- `ar.fb.article` : catalogue des fournitures.
- `ar.fb.traiteur` : personnes autorisées à traiter les demandes.
- `ar.fb.documentation` : documentation métier.

## Workflow

1. `new` : nouvelle demande saisie par le demandeur.
2. `n1` : validation manager N+1.
3. `processing` : traitement par le service concerné.
4. `received` : demande livrée/réceptionnée.
5. `refused` : demande refusée.

## Fonctionnement

- Le demandeur, son département et son manager sont récupérés depuis `hr.employee`.
- Le demandeur peut modifier et soumettre la demande tant qu'elle est nouvelle.
- Le manager N+1 valide ou refuse.
- Les utilisateurs configurés comme traiteurs prennent en charge le traitement.
- La réception clôture la demande.
- Les changements sont suivis dans le chatter.

## Sécurité

Le module utilise des groupes, règles d'enregistrement et droits d'accès :

- `security/security.xml`
- `security/record_rules.xml`
- `security/ir.model.access.csv`

## Interface

Des vues de gestion des articles, traiteurs, demandes, documentation et menus sont fournies. Des assets SCSS/JS améliorent l'affichage kanban et les animations.

