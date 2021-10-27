# -*- coding: utf-8 -*-
# from odoo import http


# class ZueErp(http.Controller):
#     @http.route('/zue_erp/zue_erp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_erp/zue_erp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_erp.listing', {
#             'root': '/zue_erp/zue_erp',
#             'objects': http.request.env['zue_erp.zue_erp'].search([]),
#         })

#     @http.route('/zue_erp/zue_erp/objects/<model("zue_erp.zue_erp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_erp.object', {
#             'object': obj
#         })
