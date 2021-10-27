{
    'name': "zue_purchase",

    'summary': """Módulo de compras de zue""",

    'description': """Módulo de compras de zue""",

    'author': "ZUE S.A.S.",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','zue_erp','purchase','account', 'zue_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sre_order.xml',
        'views/account_move.xml',
        'views/account_move_refund.xml',
        'views/security_company.xml',
        'reports/report_purchaseorder_document.xml',
        'views/menus.xml',
        
    ],
}
