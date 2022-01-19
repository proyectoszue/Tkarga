{
    'name': "zue_electronic_invoice",

    'summary': """Módulo de facturación electrónica zue""",

    'description': """Módulo de facturación electrónica zue""",

    'author': "ZUE S.A.S.",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','zue_erp','account', 'zue_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions_account_move.xml',
        'views/actions_account_tax.xml',
        'views/actions_account_journal.xml',
        'views/actions_res_config_settings.xml',
        'views/menus.xml',
    ],
}
