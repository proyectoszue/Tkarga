{
    'name': "zue_electronic_invoice_pos",
    'icon': '/zue_electronic_invoice/static/description/icon.png',
    'summary': "Facturación electrónica ZUE para punto de venta",
    'description': "Facturación electrónica ZUE para órdenes de punto de venta.",
    'author': "ZUE S.A.S.",
    'category': 'Accounting/Localizations/EDI',
    'version': '19.0.2.1.0',
    'depends': ['zue_electronic_invoice', 'point_of_sale'],
    'post_init_hook': 'post_init_hook',
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
            'Envía por el canal POS las notas crédito de facturas originadas en el POS.',
            'Carga los servicios web y el generador XML POS solo al instalar y reutiliza los existentes sin reemplazar su parametrización.',
        ],
        'reports': [
        ],
    },
}

