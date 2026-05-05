# -*- coding: utf-8 -*-
{
    'name': "zue_account",
    'icon': '/zue_account/static/description/icon.png',
    'summary': """
        Módulo para personalización de la contabilidad Colombiana. """,

    'description': """
        Módulo para personalización de la contabilidad Colombiana. 
    """,

    'author': "ZUE S.A.S",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    "version": "19.0.1.0.0",

    # any module necessary for this one to work correctly
    'depends': ['base','account','zue_erp','account_reports','documents','l10n_co_reports','accountant','stock_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'data/account_fiscal_position_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_res_bank_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/account_group_data.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        'views/actions_payment_file.xml',
        'views/actions_account_account.xml',
        'views/aged_partner_balance_report_columns.xml',
        'views/actions_account_move.xml',
        'views/actions_account_closing_reversal.xml',
        # 'views/actions_documents.xml',
        # 'views/actions_account_aged_partner.xml', TOCA REHACER DESARROLLO EN V17
        'views/actions_exogenous_information.xml',
        'views/actions_bank_statements_report.xml',
        'views/actions_res_partner_fe.xml',
        'views/actions_account_journal.xml',
        'views/actions_reconciling_items.xml',
        'views/actions_res_config_settings.xml',
        'views/actions_bank_multicash_extracts.xml',
        'views/actions_bank_transaccion_table.xml',
        'views/actions_bank_movement_types.xml',
        'views/actions_concept_accounts.xml',
        'views/actions_match_bank_reconciliation.xml',
        'views/actions_bank_rec_widget.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zue_account/static/src/js/aged_partner_balance_filters_patch.js',
            'zue_account/static/src/js/bank_reconciliation_cxc_cxp_patch.js',
        ],
    },
    'license': 'LGPL-3',
}
