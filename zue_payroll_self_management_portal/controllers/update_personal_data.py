# -*- coding: utf-8 -*-
from odoo.http import request, route, Controller

class ZuePayrollUpdatePersonalDataPortal(Controller):

    def _get_portal_employee(self):
        return request.env['hr.employee.public'].search(
            [('user_id', '=', request.env.user.id)], limit=1)

    def _get_portal_design(self):
        company = request.env.user.company_id
        return request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', company.id)], limit=1)

    def _get_countries_list(self):
        return [
            {'id': country.id, 'name': country.name}
            for country in request.env['res.country'].search([])
        ]

    def _render_update_personal_data(self, profile_update=False):
        return request.render(
            'zue_payroll_self_management_portal.update_personal_data',
            {
                'profile_update': profile_update,
                'obj': self._get_portal_employee(),
                'list_countries': self._get_countries_list(),
                'portal_design': self._get_portal_design(),
            },
        )

    @route(
        '/zue_payroll_self_management_portal/update_personal_data',
        type='http',
        auth='user',
        website=True,
        methods=['GET'],
    )
    def update_personal_data(self, **kw):
        if not request.env.user:
            return request.not_found()
        if not self._get_portal_employee():
            return request.not_found()
        return self._render_update_personal_data(profile_update=False)

    @route(
        '/zue_payroll_self_management_portal/update_personal_data_save',
        type='http',
        auth='user',
        website=True,
        methods=['POST'],
        csrf=True,
    )
    def update_personal_data_save(self, **post):
        if not request.env.user:
            return request.not_found()

        obj_employee = self._get_portal_employee()
        if not obj_employee:
            return request.not_found()

        values_employee = {
            'personal_mobile': post.get('phone'),
            'birthday': post.get('date_birthday') or False,
            'personal_email': post.get('email'),
            'work_email': post.get('email'),
            'mobile_phone': post.get('mobile_phone'),
            'work_phone': post.get('work_phone'),
            'licencia_rh': post.get('licencia_rh'),
            'z_stratum': post.get('z_stratum'),
            'z_ethnic_group': post.get('z_ethnic_group'),
            'z_victim_armed_conflict': post.get('z_victim_armed_conflict'),
            'licencia_categoria': post.get('licencia_categoria'),
            'licencia_vigencia': post.get('licencia_vigencia') or False,
            'licencia_restricciones': post.get('licencia_restricciones'),
            'place_of_birth': post.get('place_of_birth'),
            'emergency_contact': post.get('emergency_contact'),
            'emergency_phone': post.get('emergency_phone'),
            'emergency_relationship': post.get('emergency_relationship'),
            'certificate': post.get('certificate'),
            'country_id': int(post['country_id']) if post.get('country_id') else False,
            'country_of_birth': int(post['country_of_birth']) if post.get('country_of_birth') else False,
            'study_field': post.get('study_field'),
            'study_school': post.get('study_school'),
            'marital': post.get('marital'),
        }
        values_partner = {
            'street': post.get('street'),
            'mobile': post.get('phone'),
        }

        request.env['hr.employee.update.tmp'].create({
            'employee_id': obj_employee.id,
        }).update_personal_data(values_employee, values_partner)

        return self._render_update_personal_data(profile_update=True)
