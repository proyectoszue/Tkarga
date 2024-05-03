# -*- coding: utf-8 -*-
{
    'name': "zue_contract_templates",

    'summary': """
        Módulo de plantillas de contrato""",

    'description': """
        Módulo de plantillas de contrat
    """,

    'author': "ZUE S.A.S",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'ZueContractTemplates',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll','hr_holidays','hr_skills', 'hr_payroll_account','zue_erp','zue_hr_employee','account','web','zue_hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions_contract_templates.xml',
        'views/res_users.xml',
        'reports/report_contract.xml',
        'reports/report_contract_templates.xml',
        'views/menus.xml',
    ],
}
