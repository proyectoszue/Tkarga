from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

class zue_employer_replacement(models.Model):
    _name = 'zue.employer.replacement'
    _description = 'Sustitución patronal empleado'
    _rec_name = 'z_employee_id'

    z_employee_id = fields.Many2one('hr.employee', 'Empleado', required=True)
    z_identification = fields.Char(related="z_employee_id.identification_id", store=True, string="Nº identificación")
    z_version_id = fields.Many2one(related="z_employee_id.version_id", store=True, string="Contrato activo")
    z_company_id = fields.Many2one(related='z_employee_id.company_id', store=True, string='Compañía actual')
    z_new_company_id = fields.Many2one('res.company', required=True, string='Compañía nueva')
    z_employer_replacement_date = fields.Date('Fecha de sustitución patronal')
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho')], string='Estado', default='draft')
    z_bank_account_changed = fields.Boolean('Cuenta bancaria modificada', default=False, readonly=True)
    # Campos actuales (información del empleado actual)
    z_analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analítica actual', compute='_compute_analytic_account', store=True, readonly=True)
    z_department_id = fields.Many2one('hr.department', string='Departamento actual', related='z_employee_id.department_id', readonly=True)
    z_job_id = fields.Many2one('hr.job', string='Puesto actual', related='z_employee_id.job_id', readonly=True)
    z_bank_account_id = fields.Many2one( 'res.partner.bank', string='Cuenta bancaria actual', compute='_compute_main_bank_account', store=True, readonly=True)
    # Campos nuevos (editables para la sustitución)
    z_new_analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analítica nueva', domain="['|', ('company_id', '=', False), ('company_id', '=', z_new_company_id)]", required=True)
    z_new_department_id = fields.Many2one('hr.department', string='Departamento nuevo', domain="[('company_id', '=', z_new_company_id)]", required=True)
    z_new_job_id = fields.Many2one('hr.job', string='Puesto nuevo', domain="['|', ('company_id', '=', False), ('company_id', '=', z_new_company_id)]", required=True)
    z_new_bank_account_id = fields.Many2one('res.partner.bank', string='Cuenta bancaria nueva', domain="['|', ('company_id', '=', False), ('company_id', '=', z_new_company_id)]", required=True)

    @api.depends('z_employee_id', 'z_employee_id.analytic_distribution')
    def _compute_analytic_account(self):
        for record in self:
            distribution = record.z_employee_id.analytic_distribution if record.z_employee_id else False
            if not distribution:
                record.z_analytic_account_id = False
                continue
            best_analytic_id = False
            best_percentage = None
            for analytic_id, percentage in distribution.items():
                try:
                    analytic_id_int = int(analytic_id)
                except Exception:
                    continue
                if best_percentage is None or (percentage or 0.0) > best_percentage:
                    best_percentage = percentage or 0.0
                    best_analytic_id = analytic_id_int
            record.z_analytic_account_id = best_analytic_id or False

    @api.depends('z_employee_id', 'z_employee_id.work_contact_id', 'z_employee_id.work_contact_id.bank_ids')
    def _compute_main_bank_account(self):
        """Obtiene la cuenta bancaria principal del empleado desde su contacto privado"""
        for record in self:
            if record.z_employee_id and record.z_employee_id.work_contact_id:
                main_bank = record.z_employee_id.work_contact_id.bank_ids.filtered(lambda b: b.is_main)
                record.z_bank_account_id = main_bank[0] if main_bank else False
            else:
                record.z_bank_account_id = False

    @api.onchange('z_employee_id', 'z_new_company_id')
    def onchange_update_bank_domain(self):
        """Actualiza dominio y contexto de cuentas bancarias y analíticas según la nueva compañía."""
        if self.z_new_company_id:
            company = self.z_new_company_id.id
            # Cuentas analíticas de la compañía destino (o sin compañía, uso compartido)
            analytic_domain = [
                '|',
                ('company_id', '=', company),
                ('company_id', '=', False),
            ]
            if self.z_new_analytic_account_id:
                new_account = self.z_new_analytic_account_id
                if new_account.company_id and new_account.company_id.id != company:
                    self.z_new_analytic_account_id = False
            return {
                'domain': {
                    'z_new_bank_account_id': [
                        '|',
                        ('company_id', '=', company),
                        ('company_id', '=', False),
                    ],
                    'z_new_analytic_account_id': analytic_domain,
                },
                'context': {
                    'default_company_id': company,
                },
            }
        else:
            return {
                'domain': {
                    'z_new_bank_account_id': [('id', '=', False)],
                    'z_new_analytic_account_id': [('id', '=', False)],
                },
                'context': {},
            }

    @api.constrains('z_new_company_id')
    def _check_company(self):
        for record in self:
            if record.z_company_id == record.z_new_company_id:
                raise ValidationError('El empleado ya se encuentra en la empresa seleccionada. Por favor verifique')

    def replace_employee_company(self):
        #raise ValidationError("Esta funcionalidad aún no está disponible, se encuentra en etapa de desarrollo para Odoo 19.")
        if self.z_employee_id:
            if not self.z_employer_replacement_date:
                raise UserError(_('Debe indicar la fecha de sustitución patronal antes de continuar.'))
            replacement_date = self.z_employer_replacement_date
            # DUPLICAR HOJA DE VIDA ASOCIADA A LA NUEVA COMPAÑÍA
            obj_employee = self.env['hr.employee'].browse(self.z_employee_id.id)
            new_cv_employee = obj_employee.with_company(self.z_new_company_id.id).copy_data()
            new_cv_employee[0]['company_id'] = self.z_new_company_id.id
            # copy_data añade sufijo tipo " (COPIA)"; conservar el nombre del empleado original
            new_cv_employee[0]['name'] = obj_employee.name
            # Eliminar campos que se asignarán después con los valores de la sustitución para evitar errores de acceso por multicompañia
            if 'work_contact_id' in new_cv_employee[0]:
                del new_cv_employee[0]['work_contact_id']
            if 'job_id' in new_cv_employee[0]:
                del new_cv_employee[0]['job_id']
            if 'department_id' in new_cv_employee[0]:
                del new_cv_employee[0]['department_id']
            # Eliminar campos relacionales que apuntan a empleados de la compañía original para evitar errores de acceso por multicompañia
            if 'parent_id' in new_cv_employee[0]:
                del new_cv_employee[0]['parent_id']
            if 'leave_manager_id' in new_cv_employee[0]:
                del new_cv_employee[0]['leave_manager_id']
            if 'timesheet_manager_id' in new_cv_employee[0]:
                del new_cv_employee[0]['timesheet_manager_id']
            if 'coach_id' in new_cv_employee[0]:
                del new_cv_employee[0]['coach_id']
            # Eliminar campos Many2one a res.partner de la compañía original para evitar errores de acceso por multicompañia
            if 'address_id' in new_cv_employee[0]:
                del new_cv_employee[0]['address_id']
            if 'partner_encab_id' in new_cv_employee[0]:
                del new_cv_employee[0]['partner_encab_id']
            # Eliminar seguidores del chatter del empleado origen para evitar errores de acceso por multicompañia (regla res.partner company)
            if 'message_follower_ids' in new_cv_employee[0]:
                del new_cv_employee[0]['message_follower_ids']

            # CREAR CONTACTO ANTES DEL EMPLEADO (para evitar error de constrains en identification_id)
            new_contact_created = None
            email = False
            if self.z_employee_id.partner_encab_id or self.z_employee_id.work_contact_id:
                # Copiar el contacto privado del empleado original
                original_contact = self.z_employee_id.partner_encab_id or self.z_employee_id.work_contact_id
                new_contact_data = original_contact.with_company(self.z_new_company_id.id).copy_data()[0]
                new_contact_data['company_id'] = self.z_new_company_id.id
                # copy_data añade sufijo tipo " (COPIA)" al contacto; conservar el nombre original
                new_contact_data['name'] = original_contact.name
                new_contact_data['l10n_latam_identification_type_id'] = original_contact.l10n_latam_identification_type_id.id
                new_contact_data['email'] = original_contact.email
                email = original_contact.email
                # Excluir bank_ids del copy_data para evitar duplicados
                if 'bank_ids' in new_contact_data:
                    del new_contact_data['bank_ids']
                new_contact = self.with_company(self.z_new_company_id.id).env['res.partner'].create(new_contact_data)
                new_contact_created = new_contact
                # Asignar el contacto al employee_data ANTES de crear el empleado
                new_cv_employee[0]['work_contact_id'] = new_contact.id
                new_cv_employee[0]['partner_encab_id'] = new_contact.id
                #new_cv_employee[0]['email'] = new_contact.id

            # Contrato anterior: cierre con la fecha de hoy (ejecución del proceso)
            old_contract_end_date = fields.Date.context_today(self)
            current_version = self.z_employee_id.current_version_id
            current_version.write({'retirement_date': old_contract_end_date, 'date_end': old_contract_end_date})
            # Nuevo empleado/contrato: la fecha de sustitución del asistente se guarda en el contrato (z_employer_replacement_date)
            new_cv_employee[0]['date_version'] = replacement_date

            # Guardar concepts_ids válidos (sin state=cancel) ANTES de crear
            concepts_to_write = []
            if 'concepts_ids' in new_cv_employee[0]:
                concepts_to_write = [
                    cmd for cmd in new_cv_employee[0]['concepts_ids']
                    if not (isinstance(cmd, (list, tuple)) and len(cmd) >= 3 and isinstance(cmd[2], dict) and cmd[
                        2].get('state') == 'cancel')
                ]
                # Limpiar el campo para que no se ejecute durante el create
                del new_cv_employee[0]['concepts_ids']

            obj_new_employee = self.with_context(from_multicash=True).with_company(self.z_new_company_id.id).env['hr.employee'].create(new_cv_employee[0])
            if obj_new_employee.current_version_id:
                obj_new_employee.current_version_id.write({'z_employer_replacement_date': replacement_date})

            # Escribir los concepts DESPUÉS de crear, evitando los métodos internos del create
            if concepts_to_write:
                obj_new_employee.with_context(from_multicash=True).write({'concepts_ids': concepts_to_write})

            # ACTUALIZAR LOS CAMPOS ADICIONALES DEL NUEVO EMPLEADO
            employee_update_vals = {
                'department_id': self.z_new_department_id.id if self.z_new_department_id else False,
                'job_id': self.z_new_job_id.id if self.z_new_job_id else False,
            }
            # Actualizar job_title con el nombre del nuevo puesto
            if self.z_new_job_id:
                employee_update_vals['job_title'] = self.z_new_job_id.name
            obj_new_employee.write(employee_update_vals)

            # COPIAR CUENTAS BANCARIAS DEL EMPLEADO ORIGINAL AL NUEVO
            if self.z_employee_id.work_contact_id and obj_new_employee.work_contact_id:
                original_banks = self.z_employee_id.work_contact_id.bank_ids
                # Copiar cada cuenta bancaria al nuevo contacto con la nueva compañía
                if original_banks:
                    for bank in original_banks:
                        # Verificar si ya existe una cuenta con este número y compañía
                        existing_bank_global = self.env['res.partner.bank'].search([
                            ('acc_number', '=', bank.acc_number),
                            ('company_id', '=', self.z_new_company_id.id)
                        ])

                        # Si existe y pertenece al contacto original, reasignarla al nuevo contacto
                        if existing_bank_global and existing_bank_global[0].partner_id.id == self.z_employee_id.work_contact_id.id:
                            # La cuenta existe y pertenece al empleado original, reasignarla al nuevo contacto
                            is_main_value = True if (self.z_new_bank_account_id and bank.id == self.z_new_bank_account_id.id) else False
                            update_vals = {
                                'partner_id': obj_new_employee.work_contact_id.id,
                                'is_main': is_main_value
                            }
                            # Actualizar payroll_dispersion_account
                            # Intentar primero buscar journal equivalente por nombre si la cuenta original lo tenía
                            target_journal = None
                            if bank.payroll_dispersion_account:
                                target_journal = self.env['account.journal'].search([
                                    ('company_id', '=', self.z_new_company_id.id),
                                    ('is_payroll_spreader', '=', True),
                                    ('name', '=', bank.payroll_dispersion_account.name)
                                ], limit=1)
                            # Si no encontró por nombre o no tenía, buscar cualquier journal de dispersión disponible
                            if not target_journal:
                                target_journal = self.env['account.journal'].search([
                                    ('company_id', '=', self.z_new_company_id.id),
                                    ('is_payroll_spreader', '=', True)
                                ], limit=1)
                            # Asignar el journal encontrado o False
                            update_vals['payroll_dispersion_account'] = target_journal.id if target_journal else False
                            existing_bank_global[0].write(update_vals)
                        elif not existing_bank_global:
                            # No existe ninguna cuenta con este número y compañía, crearla
                            bank_data = bank.copy_data()[0]
                            bank_data['partner_id'] = obj_new_employee.work_contact_id.id
                            # Actualizar el company_id a la nueva compañía
                            bank_data['company_id'] = self.z_new_company_id.id
                            # Si esta es la cuenta seleccionada, marcarla como principal
                            if self.z_new_bank_account_id and bank.id == self.z_new_bank_account_id.id:
                                bank_data['is_main'] = True
                            else:
                                bank_data['is_main'] = False
                            # Actualizar payroll_dispersion_account
                            # Intentar primero buscar journal equivalente por nombre si la cuenta original lo tenía
                            target_journal = None
                            if bank.payroll_dispersion_account:
                                target_journal = self.env['account.journal'].search([
                                    ('company_id', '=', self.z_new_company_id.id),
                                    ('is_payroll_spreader', '=', True),
                                    ('name', '=', bank.payroll_dispersion_account.name)
                                ], limit=1)
                            # Si no encontró por nombre o no tenía, buscar cualquier journal de dispersión disponible
                            if not target_journal:
                                target_journal = self.env['account.journal'].search([
                                    ('company_id', '=', self.z_new_company_id.id),
                                    ('is_payroll_spreader', '=', True)
                                ], limit=1)
                            # Asignar el journal encontrado o False
                            bank_data['payroll_dispersion_account'] = target_journal.id if target_journal else False
                            new_bank = self.env['res.partner.bank'].create(bank_data)

            # # DUPLICAR EL CONTRATO A LA NUEVA COMPAÑIA
            # replacement_contract_date = fields.Date.context_today(self)
            # current_version = self.z_employee_id.version_id
            # current_version.write({'retirement_date': replacement_contract_date})
            # new_version_employee = current_version.with_company(self.z_new_company_id.id).copy_data()
            # new_version_employee[0]['company_id'] = self.z_new_company_id.id
            # new_version_employee[0]['employee_id'] = obj_new_employee.id
            # new_version_employee[0]['retirement_date'] = False
            # new_version_employee[0]['z_employer_replacement_date'] = replacement_contract_date
            #
            # obj_new_version = self.with_company(self.z_new_company_id.id).env['hr.version'].create(new_version_employee[0])
            # obj_new_version.write({'name': str(obj_new_version.name).replace(' (copia)', '')})
            #
            # # ACTUALIZAR LOS CAMPOS ADICIONALES DEL NUEVO CONTRATO
            # version_extra_vals = {
            #     'job_id': self.z_new_job_id.id if self.z_new_job_id else False,
            # }
            # if self.z_new_analytic_account_id:
            #     version_extra_vals['analytic_distribution'] = {
            #         str(self.z_new_analytic_account_id.id): 100.0,
            #     }
            # else:
            #     version_extra_vals['analytic_distribution'] = False
            # obj_new_version.write(version_extra_vals)
            #
            # # ACTUALIZAR job_id EN change_wage_ids DEL NUEVO CONTRATO
            # if self.z_new_job_id and obj_new_version.change_wage_ids:
            #     for wage_change in obj_new_version.change_wage_ids:
            #         wage_change.write({'job_id': self.z_new_job_id.id})

            create_objects = []

            # DUPLICAR LAS LIQUIDACIONES DE ULTIMO AÑO
            date_start_payslips = str(datetime.now().date().year - 1)+'-01-01'
            obj_payslips = self.env['hr.payslip'].search([('version_id','=',current_version.id),
                                                          ('date_from', '>=', date_start_payslips),
                                                          ('date_from','<=',datetime.now().date())])
            for payslips in obj_payslips:
                new_payslips = payslips.with_company(self.z_new_company_id.id).copy_data()
                new_payslips[0]['employee_id'] = obj_new_employee.id
                new_payslips[0]['version_id'] = obj_new_employee.current_version_id.id
                new_payslips[0]['state'] = 'validated'

                cr_payslip = self.with_company(self.z_new_company_id.id).env['hr.payslip'].create(new_payslips[0])
                cr_payslip.write({'employee_id': obj_new_employee.id, 'version_id': obj_new_employee.current_version_id.id})
                create_objects.append(cr_payslip)

            # DUPLICAR HISTORICOS DE CESANTIAS Y LIQUIDACIONES
            obj_history_vacations = self.env['hr.vacation'].search([('version_id', '=', current_version.id)])
            for hr_vacation in obj_history_vacations:
                new_hr_vacation = hr_vacation.with_company(self.z_new_company_id.id).copy_data()
                new_hr_vacation[0]['employee_id'] = obj_new_employee.id
                new_hr_vacation[0]['version_id'] = obj_new_employee.current_version_id.id
                cr_hr_vacation = self.with_company(self.z_new_company_id.id).env['hr.vacation'].create(new_hr_vacation[0])
                cr_hr_vacation.write({'employee_id':obj_new_employee.id, 'version_id':obj_new_employee.current_version_id.id})
                create_objects.append(cr_hr_vacation)


            obj_history_cesantias = self.env['hr.history.cesantias'].search([('version_id','=',current_version.id)])
            for hr_cesantia in obj_history_cesantias:
                new_hr_cesantia = hr_cesantia.with_company(self.z_new_company_id.id).copy_data()
                new_hr_cesantia[0]['employee_id'] = obj_new_employee.id
                new_hr_cesantia[0]['version_id'] = obj_new_employee.current_version_id.id
                cr_hr_cesantias = self.with_company(self.z_new_company_id.id).env['hr.history.cesantias'].create(new_hr_cesantia[0])
                cr_hr_cesantias.write({'employee_id': obj_new_employee.id, 'version_id': obj_new_employee.current_version_id.id})
                create_objects.append(cr_hr_cesantias)

            # MARCAR SI SE CAMBIO LA CUENTA BANCARIA
            if self.z_bank_account_id != self.z_new_bank_account_id:
                self.z_bank_account_changed = True

            # FORZAR ACTUALIZACIÓN FINAL DE CAMPOS DEL EMPLEADO
            # (algunos procesos anteriores pueden haber sobrescrito estos valores)
            final_employee_update = {
                'department_id': self.z_new_department_id.id if self.z_new_department_id else False,
                'job_id': self.z_new_job_id.id if self.z_new_job_id else False,
            }
            if self.z_new_job_id:
                final_employee_update['job_title'] = self.z_new_job_id.name
            # Forzar también work_contact_id al nuevo contacto creado
            if new_contact_created:
                final_employee_update['work_contact_id'] = new_contact_created.id
                # Sincronizar partner_encab_id con work_contact_id
                final_employee_update['partner_encab_id'] = new_contact_created.id
                new_contact_created.write({'email':email})
                final_employee_update['work_email'] = email
            obj_new_employee.write(final_employee_update)


            self.state = 'done'

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('No se puede eliminar la sustitución patronal debido a que su estado es diferente de borrador.'))
        return super(zue_employer_replacement, self).unlink()