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
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/report_execute_query.xml',
        'views/general_actions.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/actions_alerts.xml',
        'views/actions_zue_request_ws.xml',
        'views/actions_zue_xml_generator.xml',
        'views/zue_confirm_wizard.xml',
        'views/general_menus.xml'       
    ]    
}
