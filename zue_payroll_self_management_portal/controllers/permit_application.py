#-*- coding: utf-8 -*-
import io
import re
import base64

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

from PyPDF2 import  PdfFileReader, PdfFileWriter

from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval


class ZuePermitApplicationPortal(Controller):
    @route(["/zue_payroll_self_management_portal/application_permit"], auth='user', website=True)
    def permit_application(self, **kw):
        if not request.env.user:
            return request.not_found()

        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)
        lst_leave_types = []
        leave_types = request.env['hr.leave.type'].sudo().search([('published_portal', '=', True)])
        for line in leave_types:
            lst_leave_types.append((line.id, line.name))

        return request.render('zue_payroll_self_management_portal.application_permit',{'absences_update':False,'obj_employee':obj_employee,'lst_leave_types': lst_leave_types, 'portal_design':obj_portal_design})

    @route(["/zue_payroll_self_management_portal/save_permit_application"], type='http', auth='user', website=True, csrf=False)
    def save_permit_application(self, **post):
        if not request.env.user:
            return request.not_found()

        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        lst_leave_types = []
        leave_types = request.env['hr.leave.type'].sudo().search([('published_portal', '=', True)])
        for line in leave_types:
            lst_leave_types.append((line.id, line.name))

        if not post.get('date_end',False):
            date_start = datetime.strptime(post['date_start'], '%Y-%m-%d')
            date_end = date_start + timedelta(days=int(post['number_of_days'])-1,hours=23,minutes=59,seconds=59)
        else:
            date_start = datetime.strptime(post['date_start'], '%Y-%m-%d')
            date_end = datetime.strptime(post['date_end'] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')

        dict_leave = {
            'holiday_status_id': int(post['holiday_status_id']) if post.get('holiday_status_id','0') != '0' else False,
            'employee_ids': [obj_employee.id],
            'employee_id' : obj_employee.id,
            'request_date_from':  date_start.date(),
            'request_date_to': date_end.date(),
            'date_from': date_start,
            'date_to': date_end,
            'number_of_days': int(post['number_of_days']),
            'name': post['observation'],
            'holiday_type': 'employee',
            'state': 'confirm'
        }

        obj_leave = request.env['hr.leave'].sudo().create(dict_leave)
        obj_leave.with_context(leave_skip_state_check=True)._compute_date_from_to()
        obj_leave.with_context(leave_skip_state_check=True)._compute_department_id()
        obj_leave.with_context(leave_skip_state_check=True)._onchange_info_entity()
        obj_leave.with_context(leave_skip_state_check=True).onchange_number_of_days_vacations()

        #Adjunto
        if post.get('attachment', False):
            obj_attachment = request.env['ir.attachment']
            name = post.get('attachment').filename
            file = post.get('attachment')
            leave_id = obj_leave.id
            attachment = file.read()
            attachment_id = obj_attachment.sudo().create({
                'name': name,
                'store_fname': name,
                'res_name': name,
                'type': 'binary',
                'res_model': 'hr.leave',
                'res_id': leave_id,
                'datas': base64.b64encode(attachment),
            })

        return request.render('zue_payroll_self_management_portal.application_permit',{'absences_update':True,'obj_employee':obj_employee,'lst_leave_types': lst_leave_types, 'portal_design':obj_portal_design})
