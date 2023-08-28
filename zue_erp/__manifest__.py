# -*- coding: utf-8 -*-
{
    'name': "zue_erp",

    'summary': """
        ZUE ERP""",

    'description': """
        .ZUE ERP.
    """,

    'author': "ZUE S.A.S",
    #'website': "http://www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'ZueERP',
    "version": "15.0.1.0.0",
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','base_vat','contacts','zue_xml_generator','zue_request_ws'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/report_execute_query.xml',
        'views/general_actions.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/actions_alerts.xml',
        'views/zue_confirm_wizard.xml',
        'views/general_menus.xml'       
    ],
    'license': 'LGPL-3',
}
