#-*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

from PyPDF2 import  PdfFileReader, PdfFileWriter

from odoo.exceptions import UserError, ValidationError
from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval


class ZuePayrollSelfManagementPortal(Controller):
    @route('/zue_payroll_self_management_portal', auth='user', website=True)
    def index(self, **kw):
        if not request.env.user:
            return request.not_found()

        date_today = datetime.now(timezone(request.env.user.tz)).date()
        obj_portal_news = request.env['hr.portal.news'].search(
            [('company_id', '=', request.env.user.company_id.id), '|', ('date_end', '=', False),
             ('date_end', '>=', date_today)])
        obj_portal_parametrization_portal = request.env['zue.parameterization.portal.menus'].search([])
        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)])
        if len(obj_employee) > 0:
            for employee in obj_employee:
                obj_contract = request.env['hr.contract.public'].search([('employee_id','=',employee.id),('state','=','open')], limit=1)
                if len(obj_contract) == 0:
                    raise ValidationError('El empleado '+str(employee.name)+' no tiene ningún contrato activo, por favor verificar.')
                photo = employee.image_1920
                name = employee.name
                identification = employee.identification_id
                street = employee.address_home_id.street
                phone = employee.personal_mobile
                date_birthday = employee.birthday
                type_employee = employee.type_employee.name
                company = employee.company_id.name
                type_contract = obj_contract.get_contract_type()
                accumulated_vacation_days = obj_contract.get_accumulated_vacation_days()
                enjoyed_vacation_days = sum([i.business_units for i in request.env['hr.vacation'].sudo().search([('contract_id', '=', obj_contract.id)])])
                money_vacation_days = sum([i.units_of_money for i in request.env['hr.vacation'].sudo().search([('contract_id', '=', obj_contract.id)])])
                department = employee.department_id.name
                parent = employee.parent_id.name
                branch = employee.branch_id.name
                laboral_address =  employee.address_id.name
                job = employee.sudo().job_id.name
                date_start = obj_contract.date_start
                email = employee.personal_email
                #Obtener turnos
                datetime_today = datetime.now(timezone(request.env.user.tz))
                start_datetime = str(datetime_today.year)+'-'+str(datetime_today.month)+'-01 00:00:00'
                start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S') + relativedelta(months=-1)
                end_datetime = start_datetime + relativedelta(months=3)
                obj_model_planning = request.env['ir.model'].sudo().search([('model','=','planning.slot')])
                if len(obj_model_planning) > 0:
                    obj_slot = request.env['planning.slot'].sudo().search([('resource_id.employee_id','=',employee.id),
                                                                           ('start_datetime','>=',start_datetime),
                                                                           ('start_datetime','<=',end_datetime)])
                    planning = request.env['planning.planning'].sudo().create({
                        'start_datetime': start_datetime,
                        'end_datetime': end_datetime,
                        'include_unassigned': False,
                        'slot_ids': [(6, 0, obj_slot.ids)],
                    })
                    planning_url = employee.get_info_planning_get_url(planning)
                    base_url = False
                    if request.env.user.company_id.website_id:
                        base_url = request.env.user.company_id.website_id.domain
                    if not base_url:
                        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    planning_url = base_url+planning_url[employee.id]
                else:
                    planning_url = False
                #Verificar si tiene instalada la funcionalidad estandar de Odoo - CURSOS
                obj_model_slide = request.env['ir.model'].sudo().search([('model', '=', 'slide.channel')])
                if len(obj_model_slide) > 0:
                    have_slides = True
                else:
                    have_slides = False
                #Entradas de trabajo
                lst_work_entry = []
                start_datetime_days_statistics = start_datetime + relativedelta(months=-1)
                obj_work_entry_type = request.env['hr.work.entry.type'].sudo().search([('active','=',True)])
                for w in obj_work_entry_type:
                    obj_work_entry = request.env['hr.work.entry'].sudo().search([('work_entry_type_id','=',w.id),
                                                                                 ('contract_id', '=', obj_contract.id),
                                                                                 ('date_start', '>=', start_datetime_days_statistics),
                                                                                 ('date_stop', '<=', datetime_today),
                                                                                 ('conflict', '=', False)])
                    duration = 0
                    if w.code == 'WORK100':
                        duration += sum(i.duration for i in obj_work_entry)/8 # cantidad de horas trabajadas / 8 (horas laborales) = días laborados
                    else:
                        for leave in obj_work_entry.leave_id.ids:
                            duration += sum(i.number_of_days for i in request.env['hr.leave'].sudo().search([('id','=',leave)]))

                    if duration > 0:
                        lst_work_entry.append((w.name,duration))
                #Documentos a expirar
                documents_statistics = employee.get_info_documents_portal(user_id=request.env.user.id, cant_expirados=1)

            info_employee = {
                'title': 'Portal de autogestión de nómina',
                'news': obj_portal_news,
                'parameterization_portal': obj_portal_parametrization_portal,
                'portal_design':obj_portal_design,
                'photo': photo,
                'name':name,
                'identification':identification,
                'street':street,
                'phone':phone,
                'date_birthday':date_birthday,
                'type_employee':type_employee,
                'company':company,
                'type_contract':type_contract,
                'accumulated_vacation_days':accumulated_vacation_days,
                'enjoyed_vacation_days':enjoyed_vacation_days,
                'money_vacation_days':money_vacation_days,
                'department':department,
                'parent':parent,
                'branch': branch,
                'laboral_address': laboral_address,
                'job':job,
                'date_start':date_start,
                'email':email,
                'user':request.env.user,
                'datetime_today':datetime_today,
                'start_datetime_days_statistics':start_datetime_days_statistics,
                'qty_days_statistics': (datetime_today.date()-start_datetime_days_statistics.date()).days,
                'qty_days_in_company': (datetime_today.date() - date_start).days,
                'planning_url': planning_url,
                'have_slides': have_slides,
                'lst_work_entry':lst_work_entry,
                'documents_statistics':documents_statistics
            }

            return request.render('zue_payroll_self_management_portal.index_page', info_employee)
        else:
            raise ValidationError('El usuario no está asociado a ningún empleado de la compañía, por favor verificar.')

   