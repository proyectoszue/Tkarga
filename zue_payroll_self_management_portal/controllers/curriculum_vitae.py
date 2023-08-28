# -*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.http import request, route, Controller

class ZuePayrollCurriculumVitaePortal(Controller):
    @route('/zue_payroll_self_management_portal/curriculum_vitae', auth='user', website=True)
    def curriculum_vitae_data(self, **kw):
        if not request.env.user:
            return request.not_found()

        # Tipo
        resume_line_type = []
        obj_resume_line_type = request.env['hr.resume.line.type'].sudo().search([])
        for line in obj_resume_line_type:
            resume_line_type.append((line.id, line.name))
        resume_line_type.append((0, 'Otro'))
        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        if len(obj_employee) > 0:
            for employee in obj_employee:
                curriculum = employee.get_info_curriculum_vitae_portal()
                type_resumes = []
                for type_r in request.env['hr.resume.line.type'].sudo().search([]):
                    type_resumes.append(type_r.name)
                type_resumes.append('Otro')

                return request.render('zue_payroll_self_management_portal.curriculum_vitae_data',
                                      {'curriculum': curriculum,
                                       'type_resumes':type_resumes,
                                       'lst_resume_line_type':resume_line_type,
                                       'portal_design':obj_portal_design})

    @route(["/zue_payroll_self_management_portal/add_curriculum_employee_save"], type='http', auth='user', website=True,
           csrf=False)
    def add_curriculum_employee_save(self, **post):
        if not request.env.user:
            return request.not_found()

        # Tipo
        resume_line_type = []
        obj_resume_line_type = request.env['hr.resume.line.type'].sudo().search([])
        for line in obj_resume_line_type:
            resume_line_type.append((line.id, line.name))
        resume_line_type.append((False, 'Otro'))

        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)

        #Crear nueva experiencia
        if len(obj_employee) > 0:
            values_add = {
                'employee_id': obj_employee.id,
                'name': post['field_name'],
                'line_type_id': int(post['field_line_type_id']) if post['field_line_type_id'] != '0' else False,
                'display_type': 'classic',
                'date_start': post['field_date_start'] if post['field_date_start'] != '' else False,
                'date_end': post['field_date_end'] if post['field_date_end'] != '' else False,
                'description': post['field_description'],
               }
            request.env['hr.resume.line'].sudo().create(values_add)

            for employee in obj_employee:
                curriculum = employee.get_info_curriculum_vitae_portal()
                type_resumes = []
                for type_r in request.env['hr.resume.line.type'].sudo().search([]):
                    type_resumes.append(type_r.name)
                type_resumes.append('Otro')

                return request.render('zue_payroll_self_management_portal.curriculum_vitae_data',
                                      {'curriculum': curriculum,
                                       'type_resumes': type_resumes,
                                       'lst_resume_line_type': resume_line_type, 'portal_design':obj_portal_design})

    @route(["/zue_payroll_self_management_portal/delete_curriculum_employee_save/<int:resume_id>"], type='http', auth='user', website=True,
           csrf=False)
    def delete_curriculum_employee_save(self, resume_id,**post):
        if not request.env.user:
            return request.not_found()

        # Tipo
        resume_line_type = []
        obj_resume_line_type = request.env['hr.resume.line.type'].sudo().search([])
        for line in obj_resume_line_type:
            resume_line_type.append((line.id, line.name))
        resume_line_type.append((False, 'Otro'))

        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)

        if len(obj_employee) > 0:
            request.env['hr.resume.line'].sudo().search([('id','=',resume_id),('employee_id','=',obj_employee.id)]).unlink()

            for employee in obj_employee:
                curriculum = employee.get_info_curriculum_vitae_portal()
                type_resumes = []
                for type_r in request.env['hr.resume.line.type'].sudo().search([]):
                    type_resumes.append(type_r.name)
                type_resumes.append('Otro')

                return request.render('zue_payroll_self_management_portal.curriculum_vitae_data',
                                      {'curriculum': curriculum,
                                       'type_resumes': type_resumes,
                                       'lst_resume_line_type': resume_line_type, 'portal_design':obj_portal_design})

    @route('/zue_payroll_self_management_portal/skills', auth='user', website=True)
    def skills_data(self, **kw):
        if not request.env.user:
            return request.not_found()

        # Tipo
        skill_type = []
        obj_skill_type = request.env['hr.skill.type'].sudo().search([])
        for line in obj_skill_type:
            skill_type.append((line.id, line.name))

        # Habilidades
        skill_skills = []
        obj_skills = request.env['hr.skill'].sudo().search([])
        for line in obj_skills:
            skill_skills.append((line.id, line.name, line.skill_type_id.id, line.is_other))

        # Nivel
        skill_level = []
        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_skill_level = request.env['hr.skill.level'].sudo().search([])
        for line in obj_skill_level:
            skill_level.append((line.id, line.name, line.skill_type_id.id))
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        if len(obj_employee) > 0:
            for employee in obj_employee:
                skills = employee.get_info_skills_portal()

                return request.render('zue_payroll_self_management_portal.skills_data',
                                      {'skills': skills,
                                       'lst_skill_type':skill_type,
                                        'lst_skill_skills':skill_skills,
                                        'lst_skill_level':skill_level,
                                        'portal_design':obj_portal_design})

    @route(["/zue_payroll_self_management_portal/add_skill_employee_save"], type='http', auth='user', website=True,
           csrf=False)
    def add_skill_employee_save(self, **post):
        if not request.env.user:
            return request.not_found()
        messages = []

        # Tipo
        skill_type = []
        obj_skill_type = request.env['hr.skill.type'].sudo().search([])
        for line in obj_skill_type:
            skill_type.append((line.id, line.name))

        # Habilidades
        skill_skills = []
        obj_skills = request.env['hr.skill'].sudo().search([])
        for line in obj_skills:
            skill_skills.append((line.id, line.name, line.skill_type_id.id, line.is_other))

        # Nivel
        skill_level = []
        obj_skill_level = request.env['hr.skill.level'].sudo().search([])
        for line in obj_skill_level:
            skill_level.append((line.id, line.name, line.skill_type_id.id))

        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        if len(obj_employee) > 0:
            values_add = {
                'employee_id': obj_employee.id,
                'skill_type_id': int(post['field_skill_type_id']) if post['field_skill_type_id'] != '' else False,
                'skill_id': int(post['field_skill_id']) if post['field_skill_id'] != '' else False,
                'which_is': post['field_skill_other'] if post['field_skill_other'] != '' else False,
                'skill_level_id': int(post['field_skill_level_id']) if post['field_skill_level_id'] != '' else False,
            }
            request.env['hr.employee.skill'].sudo().create(values_add)

            for employee in obj_employee:
                skills = employee.get_info_skills_portal()

                return request.render('zue_payroll_self_management_portal.skills_data',
                                      {'skills': skills,
                                       'lst_skill_type': skill_type,
                                       'lst_skill_skills': skill_skills,
                                       'lst_skill_level': skill_level, 'portal_design':obj_portal_design})

    @route(["/zue_payroll_self_management_portal/delete_skill_employee_save/<int:skill_id>"], type='http',
           auth='user', website=True,
           csrf=False)
    def delete_skill_employee_save(self, skill_id, **post):
        if not request.env.user:
            return request.not_found()

        # Tipo
        skill_type = []
        obj_skill_type = request.env['hr.skill.type'].sudo().search([])
        for line in obj_skill_type:
            skill_type.append((line.id, line.name))

        # Habilidades
        skill_skills = []
        obj_skills = request.env['hr.skill'].sudo().search([])
        for line in obj_skills:
            skill_skills.append((line.id, line.name, line.skill_type_id.id, line.is_other))

        # Nivel
        skill_level = []
        obj_skill_level = request.env['hr.skill.level'].sudo().search([])
        for line in obj_skill_level:
            skill_level.append((line.id, line.name, line.skill_type_id.id))

        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        if len(obj_employee) > 0:
            request.env['hr.employee.skill'].sudo().search([('id', '=', skill_id), ('employee_id', '=', obj_employee.id)]).unlink()

            for employee in obj_employee:
                skills = employee.get_info_skills_portal()

                return request.render('zue_payroll_self_management_portal.skills_data',
                                      {'skills': skills,
                                       'lst_skill_type': skill_type,
                                       'lst_skill_skills': skill_skills,
                                       'lst_skill_level': skill_level, 'portal_design':obj_portal_design})





