# -*- coding: utf-8 -*-
{
    'name': "zue_erp_asset",

    'summary': """
        ZUE ERP Activos""",

    'description': """
        .ZUE ERP Activos.
    """,

    'author': "ZUE S.A.S",
    #'website': "http://www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    "version": "15.0.1.0.0",    

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','account_asset'],

    # always loaded
    'data': [
        'views/account_assets_report.xml',
        'views/assets_fields.xml',
        'security/ir.model.access.csv'
    ],
    'license': 'LGPL-3',
}
