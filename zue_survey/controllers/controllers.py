# -*- coding: utf-8 -*-
# from odoo import http


# class ZueSurvey(http.Controller):
#     @http.route('/zue_survey/zue_survey/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zue_survey/zue_survey/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zue_survey.listing', {
#             'root': '/zue_survey/zue_survey',
#             'objects': http.request.env['zue_survey.zue_survey'].search([]),
#         })

#     @http.route('/zue_survey/zue_survey/objects/<model("zue_survey.zue_survey"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zue_survey.object', {
#             'object': obj
#         })
