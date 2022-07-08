# -*- coding: utf-8 -*-
{
    'name': "zue_payroll_self_management_portal",

    'summary': """
        Portal de autogestión de nómina""",

    'description': """
        Portal de autogestión de nómina
    """,

    'author': "ZUE S.A.S.",
    'website': "www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'ZuePayroll ManagementPortal',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website','zue_hr_employee','zue_hr_payroll'],

    # always loaded
    'data': [
        'views/index.xml',
        'views/res_users.xml',
        'views/payroll_vouchers.xml',
        'views/update_personal_data.xml',
        'views/labor_certification.xml',
        'views/application_permit.xml',
        'views/hr_permit_application.xml',
        'reports/laboral_certification.xml',
        'reports/books_reports.xml',
        'reports/book_vacation_portal_template.xml',
        'reports/book_cesantias_portal_template.xml',
        'reports/payroll_vouchers.xml',
        'reports/payslip_header_footer_template.xml',
        'reports/portal_payslip.xml',
        'security/ir.model.access.csv',
        'data/hr_permissions_portal.xml',
        'views/menus.xml',
    ],
    'bootstrap': True,
}
