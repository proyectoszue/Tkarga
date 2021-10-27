# -*- coding: utf-8 -*-
# from odoo import http


# class ZueFleetMaintenance(http.Controller):
#     @http.route('/zue_fleet_maintenance/zue_fleet_maintenance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_fleet_maintenance/zue_fleet_maintenance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_fleet_maintenance.listing', {
#             'root': '/zue_fleet_maintenance/zue_fleet_maintenance',
#             'objects': http.request.env['zue_fleet_maintenance.zue_fleet_maintenance'].search([]),
#         })

#     @http.route('/zue_fleet_maintenance/zue_fleet_maintenance/objects/<model("zue_fleet_maintenance.zue_fleet_maintenance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_fleet_maintenance.object', {
#             'object': obj
#         })
