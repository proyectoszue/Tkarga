# -*- coding: utf-8 -*-
# from odoo import http


# class ZueHrSocialSecurity(http.Controller):
#     @http.route('/zue_hr_social_security/zue_hr_social_security/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_hr_social_security/zue_hr_social_security/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_hr_social_security.listing', {
#             'root': '/zue_hr_social_security/zue_hr_social_security',
#             'objects': http.request.env['zue_hr_social_security.zue_hr_social_security'].search([]),
#         })

#     @http.route('/zue_hr_social_security/zue_hr_social_security/objects/<model("zue_hr_social_security.zue_hr_social_security"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_hr_social_security.object', {
#             'object': obj
#         })
