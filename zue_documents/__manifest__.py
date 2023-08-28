# -*- coding: utf-8 -*-
{
    'name': "zue_documents",

    'summary': """
        Proyecto para ajustes al módulo de documentos de Odoo""",

    'description': """
        Proyecto para ajustes al módulo de documentos de Odoo
    """,

    'author': "ZUE S.A.S.",
    'website': "www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Documents',
    "version": "15.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','documents'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions_documents_document.xml',
        'views/actions_document_request_template.xml',
        'views/actions_request_template.xml',
        'views/actions_document_merge_pdf.xml',
        'views/menus.xml',
    ],
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'zue_documents/static/src/js/document_resquest_template.js',
            'zue_documents/static/src/js/documents_inspector.js',
            'zue_documents/static/src/js/documents_kanban_controller.js',
            'zue_documents/static/src/js/documents_list_controller.js',
            'zue_documents/static/src/js/documents_kanban_view.js',
            'zue_documents/static/src/js/documents_list_view.js',
        ],
        'web.assets_qweb': [
            'zue_documents/static/src/xml/documents_views.xml',
        ],
    }
}
