# -*- coding: utf-8 -*-
{
    'name': "zue_hr_social_security",

    'summary': """
        Módulo de nómina para la localización colombiana | Seguridad Social""",

    'description': """
        Módulo de nómina para la localización colombiana | Seguridad Social
    """,

    'author': "ZUE S.A.S",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    "version": "15.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll','hr_holidays','zue_erp','zue_hr_employee','zue_hr_payroll','account'],

    # always loaded
    'data': [
        'views/actions_parameterization.xml',
        'views/actions_hr_payroll_social_security.xml',
        'views/actions_hr_social_security_branches.xml',
        'views/actions_hr_provisions.xml',
        'views/actions_hr_consolidated_provisions.xml',
        'views/actions_hr_closing_configuration.xml',
        'views/actions_hr_entities_reports.xml',
        'views/actions_hr_report_expenses_employee.xml',
        'views/actions_vacation_book_reports.xml',
        'views/menus.xml',
        'reports/social_security_report_template.xml',
        'reports/social_security_report.xml',              
        'security/ir.model.access.csv',
    ],
    'license': 'LGPL-3',
}
