# -*- coding: utf-8 -*-
{
    'name': "zue_request_ws",

    'summary': """
        ZUE - App para el consumo de ws""",

    'description': """
        Aplicacion desarrollada con el proposito de consumir web services
    """,

    'author': "ZUE S.A.S",
    'website': "http://www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    "version": "15.0.1.0.0",
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions_zue_request_ws.xml',
        'views/general_menus.xml'
    ],
    'license': 'LGPL-3',
}
