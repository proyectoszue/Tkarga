# -*- coding: utf-8 -*-
{
    'name': "zue_hr_employee",

    'summary': """
        Módulo de nómina para la localización colombiana | Prametrización & Hoja de Vida Empleado & Contrato""",

    'description': """
        Módulo de nómina para la localización colombiana | Prametrización &  Hoja de Vida Empleado & Contrato      
    """,

    'author': "ZUE S.A.S",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    "version": "15.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','zue_erp','hr','hr_skills','hr_payroll','hr_contract','hr_holidays','hr_payroll_account','zue_resource'],

    # always loaded
    'data': [
        'data/hr_tipos_cotizante_data.xml',
        'data/hr_indicador_especial_pensiones_data.xml',
        'security/ir.model.access.csv',        
        'views/actions_entities.xml',
        'views/actions_employee.xml',
        'views/actions_partner_employee.xml',
        'views/actions_parametrization.xml',
        'views/actions_salary_rule.xml',
        'views/actions_contract.xml',
        'views/actions_labor_certificate_history.xml',
        'views/actions_labor_certificate_template.xml',
        'views/actions_parameterization_of_contributors.xml',
        'views/actions_hr_salary_history_report.xml',
        'views/actions_hr_skills.xml',
        'views/actions_employee_sanctions.xml',
        'views/actions_employee_report_curriculum.xml',
        'views/actions_retirement_severance_pay.xml',
        'reports/report_certification.xml',         
        'reports/report_certification_template.xml',
        'reports/report_birthday_list.xml', 
        'reports/report_birthday_list_template.xml',
        'reports/report_personal_data_form_template.xml', 
        'reports/report_personal_data_form.xml',
        'reports/report_print_badge.xml',
        'reports/report_print_badge_template.xml',
        'reports/report_retirement_severance_pay.xml',
        'reports/report_retirement_severance_pay_template.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
