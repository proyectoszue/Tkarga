# -*- coding: utf-8 -*-
{
    'name': "zue_erp",
    'icon': '/zue_erp/static/description/icon.png',
    'summary': """
        ZUE ERP""",

    'description': """
        .ZUE ERP.
    """,

    'author': "ZUE S.A.S",
    'website': "http://www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical',
    'version': '19.0.1.0.1',
    'application': True,

    'depends': ['base', 'base_import', 'base_vat', 'base_address_extended', 'l10n_latam_base', 'contacts', 'zue_xml_generator', 'zue_request_ws'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        # 'data/zue_ciiu_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_zip_code_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_third_party_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        'views/views_contact_form.xml',
        'views/report_execute_query.xml',
        'views/general_actions.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/actions_suppliers_category.xml',
        'views/actions_res_partner_inherit.xml',
        'views/general_menus.xml'
    ],
    'license': 'LGPL-3',
    'zue_functional': {
        'area': 'Operación general',
        'summary': 'ZUE ERP.',
        'features': [
            'Administra sucursales, tipos de tercero, códigos postales, festivos, ciudades y actividades CIIU.',
            'Valida la duplicidad de identificación tributaria en contactos.',
            'Controla qué usuarios pueden importar archivos desde una URL.',
        ],
        'reports': [
            'Reportes ZUE',
        ],
    },
}
