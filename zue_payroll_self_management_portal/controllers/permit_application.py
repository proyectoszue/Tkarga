#-*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from PyPDF2 import  PdfFileReader, PdfFileWriter

from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval
from odoo.tools import float_round


class ZuePermitApplicationPortal(Controller):
    @route(["/zue_payroll_self_management_portal/application_permit"], auth='user', website=True)
    def permit_application(self, **kw):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)

        return request.render('zue_payroll_self_management_portal.application_permit',{'obj_employee':obj_employee})

    @route(["/zue_payroll_self_management_portal/save_permit_application"], type='http', auth='user', website=True, csrf=False)
    def save_permit_application(self, **post):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)

        if post.get('initial_hour',False):
            initial_hour_lst = post['initial_hour'].split(':')
            initial_hour = float_round(int(initial_hour_lst[0]) + int(initial_hour_lst[1]) / 60 + 0 / 3600, precision_digits=2)
        else:
            initial_hour = 0

        if post.get('final_hour',False):
            final_hour_lst = post['final_hour'].split(':')
            final_hour = float_round(int(final_hour_lst[0]) + int(final_hour_lst[1]) / 60 + 0 / 3600, precision_digits=2)
        else:
            final_hour = 0

        permit = {
            'employee_id' : obj_employee.id,
            'permit_date' : post['permit_date'],
            'reason': post['reason'],
            'text_other': post.get('text_other',''),
            'leave_requested_more_day': True if post.get('leave_requested_more_day',False) == '' else False,
            'permit_days' : int(post.get('permit_days',0)),
            'initial_hour' : initial_hour,
            'final_hour' : final_hour,
            'observation': post['observation'],
            'state': 'confirm'
        }

        request.env['hr.permit.application'].sudo().create(permit)

        return request.redirect('/zue_payroll_self_management_portal')

    @route(["/zue_payroll_self_management_portal/my_application_permits"], type='http', auth='user', website=True)
    def my_application_permits(self, **kw):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        obj_permit_application = request.env['hr.permit.application'].search([('employee_id', '=', obj_employee.id)])

        return request.render('zue_payroll_self_management_portal.my_application_permits', {'obj_employee': obj_employee,'obj_permit_application':obj_permit_application})