# -*- coding: utf-8 -*-
# from odoo import http


# class ZueElectronicInvoice(http.Controller):
#     @http.route('/zue_electronic_invoice/zue_electronic_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_electronic_invoice/zue_electronic_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_electronic_invoice.listing', {
#             'root': '/zue_electronic_invoice/zue_electronic_invoice',
#             'objects': http.request.env['zue_electronic_invoice.zue_electronic_invoice'].search([]),
#         })

#     @http.route('/zue_electronic_invoice/zue_electronic_invoice/objects/<model("zue_electronic_invoice.zue_electronic_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_electronic_invoice.object', {
#             'object': obj
#         })
