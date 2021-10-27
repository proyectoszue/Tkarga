# -*- coding: utf-8 -*-
# from odoo import http


# class ZueContract(http.Controller):
#     @http.route('/zue_contract/zue_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_contract/zue_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_contract.listing', {
#             'root': '/zue_contract/zue_contract',
#             'objects': http.request.env['zue_contract.zue_contract'].search([]),
#         })

#     @http.route('/zue_contract/zue_contract/objects/<model("zue_contract.zue_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_contract.object', {
#             'object': obj
#         })
