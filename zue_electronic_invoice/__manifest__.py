{
    'name': "zue_electronic_invoice",
    'icon': '/zue_electronic_invoice/static/description/icon.png',
    'summary': """Módulo de facturación electrónica zue""",

    'description': """Módulo de facturación electrónica zue""",

    'author': "ZUE S.A.S.",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    "version": "19.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','account','zue_account_support_document', 'point_of_sale', 'sale', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'data/zue_account_tax_type_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_responsibilities_rut_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/product_category_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/product_template_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_request_ws_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/fe_payments_options_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_xml_generator_data_nom_elect.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_xml_generator_data_elect_invo.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_xml_generator_data_pos.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_xml_generator_data_doc_sop.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        'views/actions_account_move.xml',
        'views/actions_account_tax.xml',
        'views/actions_account_journal.xml',
        'views/actions_res_config_settings.xml',
        'views/menus.xml',
        'views/actions_document_support.xml',
        'views/actions_upload_dian_invoice.xml',
    ],
    'license': 'LGPL-3',
}
