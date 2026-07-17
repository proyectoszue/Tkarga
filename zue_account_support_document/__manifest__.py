# -*- coding: utf-8 -*-
{
    'name': "zue_account_support_document",
    'icon': '/zue_account_support_document/static/description/icon.png',
    'summary': """
        Modulo de ZUE para soporte de documentos DIAN
    """,

    'description': """
        Modulo de ZUE para soporte de documentos DIAN
    """,

    'author': "ZUE S.A.S",

    'category': 'Uncategorized',
    "version": "19.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','zue_erp','zue_account','l10n_co'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions_parametrization_support_document.xml',
        'views/res_config_settings_views.xml',
        'views/actions_documents_support.xml',
        'views/actions_notes_documents_support.xml',
        # 'views/actions_account_move.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        'views/menus.xml',
    ],
    'license': 'LGPL-3',
}
