#-*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from PyPDF2 import  PdfFileReader, PdfFileWriter

from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval


class ZuePayrollSelfManagementPortal(Controller):
    @route('/zue_payroll_self_management_portal', auth='user', website=True)
    def index(self, **kw):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)])

        for employee in obj_employee:
            obj_contract = request.env['hr.contract'].search([('employee_id','=',employee.id),('state','=','open')], limit=1)                           

            photo = employee.image_1920
            name = employee.name
            identification = employee.identification_id
            street = employee.address_home_id.street
            phone = employee.personal_mobile
            date_birthday = employee.birthday
            type_employee = employee.type_employee.name
            company = employee.company_id.name
            type_contract = obj_contract.get_contract_type()
            department = employee.department_id.name
            job = employee.job_id.name
            date_start = obj_contract.date_start
            email = employee.personal_email
        
        info_employee = {
            'title': 'Portal de autogestión de nómina',
            'photo': photo,
            'name':name,
            'identification':identification,
            'street':street,
            'phone':phone,
            'date_birthday':date_birthday,
            'type_employee':type_employee,
            'company':company,
            'type_contract':type_contract,
            'department':department,
            'job':job,
            'date_start':date_start,
            'email':email
        }

        return request.render('zue_payroll_self_management_portal.index_page', info_employee)
    
   