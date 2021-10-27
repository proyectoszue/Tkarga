# -*- coding: utf-8 -*-
{
    'name': "zue_stock",

    'summary': """
        Modulo de inventario por ZUE S.A.S""",

    'description': """
        Modulo de inventario por ZUE S.A.S
    """,

    'author': "ZUE S.A.S",
    

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','purchase'],

    # always loaded
    'data': [
        'views/actions_accounting.xml',
    ],
    
}
