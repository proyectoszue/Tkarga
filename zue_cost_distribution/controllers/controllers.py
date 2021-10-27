# -*- coding: utf-8 -*-
# from odoo import http


# class ZueCostDistribution(http.Controller):
#     @http.route('/zue_cost_distribution/zue_cost_distribution/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_cost_distribution/zue_cost_distribution/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_cost_distribution.listing', {
#             'root': '/zue_cost_distribution/zue_cost_distribution',
#             'objects': http.request.env['zue_cost_distribution.zue_cost_distribution'].search([]),
#         })

#     @http.route('/zue_cost_distribution/zue_cost_distribution/objects/<model("zue_cost_distribution.zue_cost_distribution"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_cost_distribution.object', {
#             'object': obj
#         })
