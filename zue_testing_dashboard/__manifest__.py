# -*- coding: utf-8 -*-
{
    'name': "zue_testing_dashboard",

    'summary': """
        ZUE - Panel visual para pruebas funcionales""",

    'description': """
        Permite ejecutar pruebas funcionales desde un panel visual en Odoo.
        Centraliza proveedores de pruebas instalados sin acoplar la interfaz a un modulo funcional.
        
        Estructura tecnica:
        - Archivos: models/core_test_provider.py, models/core_adapter_session.py, views/core_adapter_views.xml, security/groups.xml, security/ir.model.access.csv y recursos static/src.
        - Modelos: zue.testing.dashboard.test.provider, zue.testing.dashboard.session y zue.testing.dashboard.line.
        - Metodos: get_adapter_data, prepare_run, run_case, finish_run, clear_last_run, _get_zue_testing_dashboard_test_specs, _get_zue_testing_dashboard_scope_labels, _get_zue_testing_dashboard_source_labels y _run_zue_testing_dashboard_test.
        - Componentes JS: ZueTestingDashboard registrado como accion cliente zue_testing_dashboard.dashboard.
        - Vistas: menu Pruebas ZUE y accion reutilizable del panel.
        - Particularidades: cada caso se ejecuta en su propio punto de guardado y revierte los datos creados al finalizar.
        
        Logica de negocio:
        El modulo no define pruebas de negocio por si mismo. Los modulos proveedores publican escenarios funcionales y el panel los ejecuta con progreso visual, estado, trazabilidad y detalle de fallos.
    """,

    'author': "ZUE S.A.S",
    'website': "http://www.zue.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden/Tests',
    'version': '19.0.1.0.0',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'zue_hr_payroll', 'zue_hr_social_security'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/core_adapter_views.xml',
        'views/core_history_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'zue_testing_dashboard/static/src/js/core_process_result_viewer.js',
            'zue_testing_dashboard/static/src/js/payroll_process_result_viewer.js',
            'zue_testing_dashboard/static/src/js/core_zue_testing_dashboard.js',
            'zue_testing_dashboard/static/src/js/payroll_zue_testing_dashboard.js',
            'zue_testing_dashboard/static/src/js/history_result_field.js',
            'zue_testing_dashboard/static/src/scss/core_zue_testing_dashboard.scss',
            'zue_testing_dashboard/static/src/scss/payroll_zue_testing_dashboard.scss',
            'zue_testing_dashboard/static/src/xml/core_process_result_viewer.xml',
            'zue_testing_dashboard/static/src/xml/payroll_process_result_viewer.xml',
            'zue_testing_dashboard/static/src/xml/core_zue_testing_dashboard.xml',
            'zue_testing_dashboard/static/src/xml/history_result_field.xml',
            'zue_testing_dashboard/static/src/xml/payroll_zue_testing_dashboard.xml',
        ],
    },

    'installable': True,
    'license': 'LGPL-3',
    'zue_functional': {
        'area': 'Operación general',
        'summary': 'ZUE - Panel visual para pruebas funcionales.',
        'features': [
            'Ejecuta pruebas funcionales publicadas por módulos proveedores.',
            'Muestra progreso, resultados y detalle de fallos en un panel.',
            'Conserva el historial y revierte los datos creados por cada caso.',
        ],
        'reports': [
        ],
    },
}
