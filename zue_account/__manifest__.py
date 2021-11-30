# -*- coding: utf-8 -*-
{
    'name': "zue_account",

    'summary': """
        Módulo para personalización de la contabilidad Colombiana. """,

    'description': """
        Módulo para personalización de la contabilidad Colombiana. 
    """,

    'author': "ZUE S.A.S",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_reports','documents'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions_payment_file.xml',
        'views/actions_account_account.xml',
        'views/actions_account_move.xml',
        'views/actions_documents.xml',
        'views/actions_account_aged_partner.xml',
        'views/actions_exogenous_information.xml',
        'views/menus.xml',
    ],
}
