# -*- coding: utf-8 -*-
# from odoo import http


# class ZueContractTemplates(http.Controller):
#     @http.route('/zue_contract_templates/zue_contract_templates', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_contract_templates/zue_contract_templates/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_contract_templates.listing', {
#             'root': '/zue_contract_templates/zue_contract_templates',
#             'objects': http.request.env['zue_contract_templates.zue_contract_templates'].search([]),
#         })

#     @http.route('/zue_contract_templates/zue_contract_templates/objects/<model("zue_contract_templates.zue_contract_templates"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_contract_templates.object', {
#             'object': obj
#         })
