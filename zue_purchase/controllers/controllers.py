# -*- coding: utf-8 -*-
# from odoo import http


# class ZuePurchase(http.Controller):
#     @http.route('/zue_purchase/zue_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_purchase/zue_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_purchase.listing', {
#             'root': '/zue_purchase/zue_purchase',
#             'objects': http.request.env['zue_purchase.zue_purchase'].search([]),
#         })

#     @http.route('/zue_purchase/zue_purchase/objects/<model("zue_purchase.zue_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_purchase.object', {
#             'object': obj
#         })
