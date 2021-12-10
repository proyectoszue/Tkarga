# -*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.http import request, route, Controller

class ZuePayrollUpdatePersonalDataPortal(Controller):
    @route('/zue_payroll_self_management_portal/update_personal_data', auth='user', website=True)
    def update_personal_data(self, **kw):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)

        return request.render('zue_payroll_self_management_portal.update_personal_data',
                              {'obj': obj_employee})

    @route(["/zue_payroll_self_management_portal/update_personal_data_save"], type='http', auth='user', website=True, csrf=False)
    def update_personal_data_save(self, **post):
        if not request.env.user:
            return request.not_found()

        values_employee = {'personal_mobile': post['phone'],
                           'birthday': post['date_birthday'],
                           'personal_email': post['email']}
        values_partner = {'street': post['street'],
                          'mobile': post['phone']}

        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        request.env['hr.employee.update.tmp'].create({'employee_id':obj_employee.id}).update_personal_data(values_employee,values_partner)
        return


