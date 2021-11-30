# -*- coding: utf-8 -*-
{
    'name': "zue_hr_payroll",

    'summary': """
        Módulo de nómina para la localización colombiana | Liquidación de Nómina""",

    'description': """
        Módulo de nómina para la localización colombiana | Liquidación de Nómina
    """,

    'author': "ZUE S.A.S",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll','hr_holidays','zue_erp','zue_hr_employee','account','web'],

    # always loaded
    'data': [
        'data/hr_type_tax_retention_data.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/actions_loans.xml',        
        'views/actions_payslip.xml',
        'views/actions_leave.xml',     
        'views/actions_overtime.xml', 
        'views/actions_concepts_deduction_retention.xml',    
        'views/actions_calculation_rtefte_ordinary.xml', 
        'views/actions_payroll_flat_file.xml',
        'views/actions_payroll_flat_file_backup.xml',
        'views/actions_hr_payroll_posting.xml',
        'views/actions_payroll_report_zue.xml',
        'views/actions_payroll_vacation.xml',
        'views/actions_voucher_sending.xml',
        'views/actions_novelties_different_concepts.xml',
        'views/actions_hr_accumulated_payroll.xml',
        'views/actions_hr_assistance_vacation_alliancet.xml',
        'views/actions_hr_history_cesantias.xml',
        'views/actions_hr_history_prima.xml',
        'views/actions_hr_work_entry.xml',
        'views/actions_hr_electronic_payroll.xml',
        'views/actions_accumulated_reports.xml',
        'views/actions_hr_absence_history.xml',
        'reports/report_payslip.xml',
        'reports/report_payslip_vacations_templates.xml',
        'reports/report_payslip_vacations.xml',        
        'reports/report_payslip_contrato_templates.xml',
        'reports/report_payslip_contrato.xml', 
        'reports/report_payslip_cesantias_prima_templates.xml',  
        'reports/report_payslip_cesantias_prima.xml',   
        'reports/report_book_vacation.xml', 
        'reports/report_book_vacation_template.xml',      
        'reports/report_book_cesantias.xml', 
        'reports/report_book_cesantias_template.xml',      
        'views/menus.xml',
    ],
    
}

