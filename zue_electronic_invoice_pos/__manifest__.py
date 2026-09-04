{
    'name': "zue_electronic_invoice_pos",
    'icon': '/zue_electronic_invoice/static/description/icon.png',
    'summary': "Facturación electrónica ZUE para punto de venta",
    'description': "Facturación electrónica ZUE para órdenes de punto de venta.",
    'author': "ZUE S.A.S.",
    'category': 'Accounting/Localizations/EDI',
    'version': '19.0.1.0.0',
    'depends': ['zue_electronic_invoice', 'point_of_sale'],
    'data': [
        # 'data/zue_request_ws_data_pos.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
        # 'data/zue_xml_generator_data_pos.xml', VISTO COMENTADA POR ERROR EN MIGRACIÓN
    ],
    'license': 'LGPL-3',
    'auto_install': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'zue_electronic_invoice_pos/static/src/pos/payment_screen.js',
        ],
    },
    'zue_functional': {
        'area': 'Contabilidad, compras y tesorería',
        'summary': 'Extiende la facturación electrónica ZUE a las órdenes del punto de venta.',
        'features': [
            'Factura y envía automáticamente las órdenes del POS mediante el flujo de facturación electrónica.',
        ],
        'reports': [
        ],
    },
}
