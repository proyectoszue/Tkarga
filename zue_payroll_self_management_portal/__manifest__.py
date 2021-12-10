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
        # 'security/ir.model.access.csv',
        'views/index.xml',
        'views/res_users.xml',
        'views/payroll_vouchers.xml',
        'views/update_personal_data.xml'
    ],
}
