# -*- coding: utf-8 -*-
{
    'name': "zue_cost_distribution",

    'summary': """
        Distribución de costos""",

    'description': """
        Distribución de costos
    """,

    'author': "ZUE S.A.S",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'ZueDistribucionCostos',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','zue_erp','zue_account','zue_fleet_maintenance','zue_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_account.xml',
        'views/hr_distribution_model.xml',
        'views/hr_distribution_rules.xml',
        'views/menus.xml',
    ]    
}
