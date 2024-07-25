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

        countries = []
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        obj_countries = request.env['res.country'].search([('id','>',0)])
        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)

        for line in obj_countries:
            countries.append({'id': line.id,'name': line.name})

        return request.render('zue_payroll_self_management_portal.update_personal_data',
                              {'profile_update':False,'obj': obj_employee,'list_countries': countries,
                               'portal_design':obj_portal_design})

    @route(["/zue_payroll_self_management_portal/update_personal_data_save"], type='http', auth='user', website=True, csrf=False)
    def update_personal_data_save(self, **post):
        if not request.env.user:
            return request.not_found()

        values_employee = {
                            'personal_mobile': post['phone'],
                            'birthday': post['date_birthday'],
                            'personal_email': post['email'],
                            'gender': post['gender'],
                            'mobile_phone': post['mobile_phone'],
                            'work_phone': post['work_phone'],
                            'licencia_rh': post['licencia_rh'],
                            'z_stratum': post['z_stratum'],
                            'z_ethnic_group': post['z_ethnic_group'],
                            'z_victim_armed_conflict': post['z_victim_armed_conflict'],
                            'licencia_categoria': post['licencia_categoria'],
                            'licencia_vigencia': post['licencia_vigencia'],
                            'licencia_restricciones': post['licencia_restricciones'],
                            'place_of_birth': post['place_of_birth'],
                            'emergency_contact': post['emergency_contact'],
                            'emergency_phone': post['emergency_phone'],
                            'emergency_relationship': post['emergency_relationship'],
                            'certificate': post['certificate'],
                            'country_id': int(post['country_id']),
                            'country_of_birth': int(post['country_of_birth']),
                            'study_field': post['study_field'],
                            'study_school': post['study_school'],
                            'marital': post['marital'],
                           }
        values_partner = {'street': post['street'],
                          'mobile': post['phone']}

        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        request.env['hr.employee.update.tmp'].create({'employee_id':obj_employee.id}).update_personal_data(values_employee,values_partner)

        countries = []
        obj_countries = request.env['res.country'].search([('id', '>', 0)])

        for line in obj_countries:
            countries.append({'id': line.id, 'name': line.name})

        return request.render('zue_payroll_self_management_portal.update_personal_data',
                              {'profile_update': True, 'obj': obj_employee, 'list_countries': countries, 'portal_design': obj_portal_design})
        #return request.redirect('/zue_payroll_self_management_portal/update_personal_data')

