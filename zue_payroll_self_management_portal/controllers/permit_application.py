#-*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from PyPDF2 import  PdfFileReader, PdfFileWriter

from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval


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
        
        permit = {
            'employee_id' : obj_employee.id,
            'permit_date' : post['permit_date'],
            'permit_days' : post['permit_days'],
            'reason' : post['reason'],
            'observation' : post['observation'],
            'initial_hour' : post['initial_date'],
            'final_hour' : post['final_date'],
            'compensated' : 0
        }

        request.env['hr.permit.application'].create(permit)

        return request.redirect('/zue_payroll_self_management_portal')
