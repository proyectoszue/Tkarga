# -*- coding: utf-8 -*-
{
    'name': "zue_erp_reports_accounting",

    'summary': """
        ZUE ERP Reportes Contables""",

    'description': """
        .ZUE ERP Reportes Contables.
        Balance
        Auxiliar
        Libro Diario
        Libro Mayor
        Consultas
        Balance analítico
        Balance Costo por Vehículo
    """,

    'author': "ZUE S.A.S",
    #'website': "http://www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',    

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','account','zue_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',       
        'views/reports_views.xml',
        'views/action_balance_report.xml',
        'views/action_books_reports.xml',
        'reports/balance_report.xml',
        'reports/balance_report_template.xml',
        'views/menus.xml',
    ]    
}
