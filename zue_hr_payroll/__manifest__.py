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
    "version": "15.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll','hr_holidays','zue_erp','zue_hr_employee','account','web','mail'],

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
        'views/actions_hr_novelties_independents.xml',
        'views/actions_hr_accumulated_payroll.xml',
        'views/actions_hr_history_cesantias.xml',
        'views/actions_hr_history_prima.xml',
        'views/actions_hr_work_entry.xml',
        'views/actions_hr_report_leave_vs_work_entry.xml',
        'views/actions_hr_electronic_payroll.xml',
        'views/actions_hr_electronic_adjust_payroll.xml',
        'views/actions_accumulated_reports.xml',
        'views/actions_hr_absence_history.xml',
        'views/actions_hr_consolidated_reports.xml',
        'views/actions_payslip_reports_template.xml',
        'views/actions_hr_transfers_of_entities.xml',
        'views/actions_hr_withholding_and_income_certificate.xml',
        'views/actions_payroll_detail_report.xml',
        'views/actions_hr_auditing_reports.xml',
        'views/actions_massive_generation_contracts.xml',
        'views/actions_employer_replacement.xml',
        'reports/reports_payslip_header_footer_template.xml',
        'reports/report_payslip.xml',
        'reports/report_payslip_vacations_templates.xml',
        'reports/report_payslip_contrato_templates.xml',
        'reports/reports_payslip_header_footer.xml',
        'reports/report_payslip_cesantias_prima_templates.xml',
        'reports/report_book_vacation.xml', 
        'reports/report_book_vacation_template.xml',      
        'reports/report_book_cesantias.xml', 
        'reports/report_book_cesantias_template.xml',
        'reports/hr_report_absenteeism_history.xml',
        'reports/hr_report_absenteeism_history_template.xml',
        'reports/hr_report_income_and_withholdings.xml',
        'reports/hr_report_income_and_withholdings_template.xml',
        'reports/report_payroll_zue.xml',
        'views/actions_account_journal.xml',
        'views/actions_res_partner.xml',
        'views/actions_hr_absenteeism_history.xml',
        'views/actions_work_income_and_pensions.xml',
        'views/menus.xml',
    ],
    'license': 'LGPL-3',
}

