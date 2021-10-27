# -*- coding: utf-8 -*-
# from odoo import http


# class ZueHrPayroll(http.Controller):
#     @http.route('/zue_hr_payroll/zue_hr_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_hr_payroll/zue_hr_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_hr_payroll.listing', {
#             'root': '/zue_hr_payroll/zue_hr_payroll',
#             'objects': http.request.env['zue_hr_payroll.zue_hr_payroll'].search([]),
#         })

#     @http.route('/zue_hr_payroll/zue_hr_payroll/objects/<model("zue_hr_payroll.zue_hr_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_hr_payroll.object', {
#             'object': obj
#         })
