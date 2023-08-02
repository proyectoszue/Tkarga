# -*- coding: utf-8 -*-
from odoo.http import request, route, Controller

class ZuePayrollSelfManagementPortalSS(Controller):
    @route('/zue_payroll_self_management_portal/social_security', auth='user', website=True)
    def social_security(self, **kw):
        if not request.env.user:
            return request.not_found()

        #Parentesco
        dependents_type = [('hijo', 'Hijo'),
                           ('padre', 'Padre'),
                           ('madre', 'Madre'),
                           ('conyuge', 'Cónyuge'),
                           ('otro', 'Otro')]
        #Genero
        gender = [('masculino', 'Masculino'),
                   ('femenino', 'Femenino'),
                   ('otro', 'Otro')]

        social_security = []
        dependents = []
        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)])
        if len(obj_employee) > 0:
            for employee in obj_employee:
                social_security = employee.get_info_social_security_portal()
                dependents = employee.get_info_dependents_portal()

            info_employee = {
                'social_security': social_security,
                'dependents': dependents,
                'lst_dependents_type': dependents_type,
                'lst_gender': gender,
                'portal_design': obj_portal_design,
            }

            return request.render('zue_payroll_self_management_portal.social_security', info_employee)

    @route(["/zue_payroll_self_management_portal/add_dependents_employee_save"], type='http', auth='user', website=True,
           csrf=False)
    def add_dependents_employee_save(self, **post):
        if not request.env.user:
            return request.not_found()

        # Parentesco
        dependents_type = [('hijo', 'Hijo'),
                           ('padre', 'Padre'),
                           ('madre', 'Madre'),
                           ('conyuge', 'Cónyuge'),
                           ('otro', 'Otro')]
        # Genero
        gender = [('masculino', 'Masculino'),
                  ('femenino', 'Femenino'),
                  ('otro', 'Otro')]

        social_security = []
        dependents = []
        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)])
        if len(obj_employee) > 0:
            values_add = {
                'employee_id': obj_employee.id,
                'name': post['field_name'],
                'genero': post['field_genero'] if post['field_genero'] != '' else False,
                'date_birthday': post['field_date_birthday'] if post['field_date_birthday'] != '' else False,
                'dependents_type': post['field_dependents_type'] if post['field_dependents_type'] != '' else False,
            }
            request.env['hr.employee.dependents'].sudo().create(values_add)

            for employee in obj_employee:
                social_security = employee.get_info_social_security_portal()
                dependents = employee.get_info_dependents_portal()

            info_employee = {
                'social_security': social_security,
                'dependents': dependents,
                'lst_dependents_type': dependents_type,
                'lst_gender': gender,
                'portal_design': obj_portal_design,
            }

            return request.render('zue_payroll_self_management_portal.social_security', info_employee)

    @route(["/zue_payroll_self_management_portal/delete_dependents_employee_save/<int:dependent_id>"], type='http',
           auth='user', website=True,
           csrf=False)
    def delete_dependents_employee_save(self, dependent_id, **post):
        if not request.env.user:
            return request.not_found()

        # Parentesco
        dependents_type = [('hijo', 'Hijo'),
                           ('padre', 'Padre'),
                           ('madre', 'Madre'),
                           ('conyuge', 'Cónyuge'),
                           ('otro', 'Otro')]
        # Genero
        gender = [('masculino', 'Masculino'),
                  ('femenino', 'Femenino'),
                  ('otro', 'Otro')]

        social_security = []
        dependents = []
        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)])
        if len(obj_employee) > 0:
            request.env['hr.employee.dependents'].sudo().search([('id', '=', dependent_id), ('employee_id', '=', obj_employee.id)]).unlink()

            for employee in obj_employee:
                social_security = employee.get_info_social_security_portal()
                dependents = employee.get_info_dependents_portal()

            info_employee = {
                'social_security': social_security,
                'dependents': dependents,
                'lst_dependents_type': dependents_type,
                'lst_gender': gender,
                'portal_design': obj_portal_design,
            }

            return request.render('zue_payroll_self_management_portal.social_security', info_employee)
