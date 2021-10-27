# -*- coding: utf-8 -*-
# from odoo import http


# class ZueStock(http.Controller):
#     @http.route('/zue_stock/zue_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_stock/zue_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_stock.listing', {
#             'root': '/zue_stock/zue_stock',
#             'objects': http.request.env['zue_stock.zue_stock'].search([]),
#         })

#     @http.route('/zue_stock/zue_stock/objects/<model("zue_stock.zue_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_stock.object', {
#             'object': obj
#         })
