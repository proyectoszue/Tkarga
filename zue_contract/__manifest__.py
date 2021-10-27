# -*- coding: utf-8 -*-
{
    'name': "zue_contract",

    'summary': """
        Folders for contracts. """,

    'description': """
        Folders for contracts. 
    """,

    'author': "ZUE S.A.S",
    
    'category': 'ZueContract',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','account','zue_fleet_maintenance','stock','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/action_contract_view.xml',
        'views/action_contract_config_view.xml',
        'views/menus.xml',
    ],
}