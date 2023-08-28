# -*- coding: utf-8 -*-
# from odoo import http


# class ZueAccountSupportDocument(http.Controller):
#     @http.route('/zue_account_support_document/zue_account_support_document/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_account_support_document/zue_account_support_document/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_account_support_document.listing', {
#             'root': '/zue_account_support_document/zue_account_support_document',
#             'objects': http.request.env['zue_account_support_document.zue_account_support_document'].search([]),
#         })

#     @http.route('/zue_account_support_document/zue_account_support_document/objects/<model("zue_account_support_document.zue_account_support_document"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_account_support_document.object', {
#             'object': obj
#         })
