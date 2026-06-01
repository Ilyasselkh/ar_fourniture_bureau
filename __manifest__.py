{
    'name': 'AR - Fourniture Bureau',
    'version': '1.0',
    'summary': 'Gestion des demandes de fournitures de bureau',
    'author': 'AR',
    'category': 'Operations',
    'depends': ['base', 'hr', 'mail'],
    "data": [
        "security/security.xml",
        "security/record_rules.xml",
        "security/ir.model.access.csv",
        "data/mail_templates.xml",
        "views/article_views.xml",
        "views/traite_person_views.xml",
        "views/demande_views.xml",
        "views/documentation_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ar_fourniture_bureau/static/src/scss/fourniture_bureau_kanban.scss",
            "ar_fourniture_bureau/static/src/js/fourniture_bureau_animations.js",
        ],
    },
    'installable': True,
    'application': True,
}
