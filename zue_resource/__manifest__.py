# -*- coding: utf-8 -*-
{
    'name': "zue_resource",

    'summary': """
        Proyecto para ajustes al módulo recursos/resource de Odoo""",

    'description': """
        Proyecto para ajustes al módulo de recursos/resource de Odoo
    """,

    'author': "ZUE S.A.S.",
    'website': "www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Resource',
    "version": "15.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','zue_erp','resource'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/resource_calendar.xml',
    ],
    'license': 'LGPL-3',
}
