# -*- coding: utf-8 -*-
# from odoo import http


# class ZueAccount(http.Controller):
#     @http.route('/zue_account/zue_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_account/zue_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_account.listing', {
#             'root': '/zue_account/zue_account',
#             'objects': http.request.env['zue_account.zue_account'].search([]),
#         })

#     @http.route('/zue_account/zue_account/objects/<model("zue_account.zue_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_account.object', {
#             'object': obj
#         })
