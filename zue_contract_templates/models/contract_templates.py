# -*- coding: utf-8 -*-

from odoo import models, fields, api


class zue_contract_templates(models.Model):
    _name = 'zue.contract.templates'
    _description = 'Plantillas de contrato'

    name = fields.Char(string='Nombre')
    contract_type = fields.Selection([
        ('obra', 'Contrato por Obra o Labor'),
        ('fijo', 'Contrato de Trabajo a Término Fijo'),
        ('indefinido', 'Contrato de Trabajo a Término indefinido'),
        ('aprendizaje', 'Contrato de Aprendizaje'),
        ('temporal', 'Contrato Temporal, ocacional o accidental')
    ], string='Tipo de Contrato')
    z_contract_template = fields.Html(string="Plantilla de contrato")
    z_contract_templates_details_ids = fields.One2many('zue.contract.templates.details', 'z_contract_templates_id',
                                                  string='Configuración de campos')


class zue_contract_templates_details(models.Model):
    _name = 'zue.contract.templates.details'
    _description = 'Plantillas de contrato detalles'

    z_contract_templates_id = fields.Many2one('zue.contract.templates', string='Configuración de campos')
    z_sequence = fields.Integer(string='Secuencia', required=True)
    z_calculation = fields.Selection([('info', 'Información'),
                                      ('legal_representative_name', 'Representante Legal Nombre'),
                                      ('signature', 'Firma Autorizada'), ], string='Tipo Cálculo',
                                   default='info', required=True)
    z_type_partner = fields.Selection([('employee', 'Empleado'), ('company', 'Compañía')], string='Origen Información')
    z_information_fields_id = fields.Many2one('ir.model.fields', string="Información",
                                            domain="[('model_id.model', 'in', ['hr.employee','res.partner','hr.contract'])]")
    z_information_fields_relation = fields.Char(related='z_information_fields_id.relation', string='Relación del objeto')
    z_related_field_id = fields.Many2one('ir.model.fields', string='Campo Relación',domain="[('model_id.model', '=', z_information_fields_relation)]")




class hr_contract(models.Model):
    _inherit = 'hr.contract'

    struct_report_contract_template = fields.Html(string="Plantilla de contrato")

    def get_z_signing_contracts(self):
        res = {'nombre':'NO AUTORIZADO', 'cargo':'NO AUTORIZADO','firma':''}
        obj_user = self.env['res.users'].search([('z_signing_contracts','=',True)])
        for user in obj_user:
            res['nombre'] = user.name
            res['cargo'] = 'Representante Legal'
            res['firma'] = user.sign_signature
        return res

    # def report_contracts_nivus(self):
    #     self.ensure_one()
    #     datas = {
    #         'id': self.id,
    #         'model': 'hr.contract'
    #     }
    #     report_name = ''
    #     if self.z_category_educators_type_contract == '2':
    #         report_name = 'zue_customizations_nivus.report_part_time_teaching_contract_document'
    #     elif self.z_category_educators_type_contract == '3':
    #         report_name = 'zue_customizations_nivus.report_three_quarters_teaching_contract_document'
    #     elif self.z_category_educators_type_contract == '7':
    #         report_name = 'zue_customizations_nivus.report_service_provision_document'
    #     elif self.contract_type == 'fijo' and (self.z_category_educators_type_contract == False or self.z_category_educators_type_contract in ['1','5']):
    #         report_name = 'zue_customizations_nivus.report_indiv_fixed_term_contract_document'
    #     elif self.contract_type == 'indefinido' and (self.z_category_educators_type_contract == False or self.z_category_educators_type_contract in ['1','5']):
    #         report_name = 'zue_customizations_nivus.report_administrative_contract_document'
    #     elif self.contract_type == 'obra' and self.z_category_educators_type_contract in ['4']:
    #         report_name = 'zue_customizations_nivus.report_teaching_contract_document'
    #     elif self.contract_type == 'aprendizaje':
    #         report_name = 'zue_customizations_nivus.report_learning_contract_document'
    #     elif self.contract_type == 'temporal':
    #         raise ValidationError(_("El tipo de contrato temporal no tiene plantilla."))
    #     else:
    #         raise ValidationError(_("No se encontro tipo de contrato asociado. Por favor verifique"))
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': report_name,
    #         'report_type': 'qweb-pdf',
    #         'datas': datas
    #     }

    def _get_report_contract_templates_filename(self):
        obj_template = self.env['zue.contract.templates'].search([('contract_type', '=', self.contract_type)], limit=1)
        if len(obj_template) > 0:
            return obj_template.name
        else:
            return 'Plantilla de contrato'

    def generate_certificate(self):
        struct_report = ''
        obj_template = self.env['zue.contract.templates'].search([('contract_type', '=', self.contract_type)], limit=1)
        obj_representative = self.employee_id.company_id.partner_id.child_ids.filtered(lambda x: x.x_contact_job_title.code == 'RL')
        obj_signature = self.env['res.users'].search([('sign_signature', '!=', False), ('z_signing_contracts', '=', True)])
        if len(obj_template) > 0:
            struct_report = obj_template.z_contract_template
            # Recorrer configuración
            for conf in sorted(obj_template.z_contract_templates_details_ids, key=lambda x: x.z_sequence):
                ldict = {'employee': self.employee_id, 'contract': self}
                value = None
                if conf.z_calculation == 'info':
                    if conf.z_type_partner == 'employee':
                        if conf.z_information_fields_id.model_id.model == 'hr.employee':
                            if conf.z_information_fields_id.ttype == 'many2one':
                                code_python = 'value = employee.' + str(conf.z_information_fields_id.name) + '.' + str(
                                    conf.z_related_field_id.name)
                            else:
                                code_python = 'value = employee.' + str(conf.z_information_fields_id.name)
                            exec(code_python, ldict)
                            value = ldict.get('value')
                        elif conf.z_information_fields_id.model_id.model == 'hr.contract':
                            if conf.z_information_fields_id.ttype == 'many2one':
                                code_python = 'value = contract.' + str(conf.z_information_fields_id.name) + '.' + str(
                                    conf.z_related_field_id.name)
                            else:
                                code_python = 'value = contract.' + str(conf.z_information_fields_id.name)
                            exec(code_python, ldict)
                            value = ldict.get('value')
                        elif conf.z_information_fields_id.model_id.model == 'res.partner':
                            if conf.z_information_fields_id.ttype == 'many2one':
                                code_python = 'value = employee.address_home_id.' + str(
                                    conf.z_information_fields_id.name) + '.' + str(conf.z_related_field_id.name)
                            else:
                                code_python = 'value = employee.address_home_id.' + str(conf.z_information_fields_id.name)
                            exec(code_python, ldict)
                            value = ldict.get('value')
                    if conf.z_type_partner == 'company':
                        if conf.z_information_fields_id.model_id.model == 'hr.employee':
                            raise UserError(
                                'No se puede traer información de la compañía de un campo de la tabla empleados, por favor verificar.')
                        elif conf.z_information_fields_id.model_id.model == 'hr.contract':
                            raise UserError(
                                'No se puede traer información de la compañía de un campo de la tabla contratos, por favor verificar.')
                        elif conf.z_information_fields_id.model_id.model == 'res.partner':
                            if conf.z_information_fields_id.ttype == 'many2one':
                                code_python = 'value = employee.company_id.partner_id.' + str(
                                    conf.z_information_fields_id.name) + '.' + str(conf.z_related_field_id.name)
                            else:
                                code_python = 'value = employee.company_id.partner_id.' + str(
                                    conf.z_information_fields_id.name)
                            exec(code_python, ldict)
                            value = ldict.get('value')
                # Tipo de Calculo Representante legal
                if conf.z_calculation == 'legal_representative_name':
                    if len(obj_representative) == 1:
                        value = obj_representative.name
                # Tipo de Calculo Firma
                if conf.z_calculation == 'signature':
                    if len(obj_signature) == 1:
                        value = obj_signature.sign_signature.decode('utf-8')
                # ----------------------------------------------------------------------------------------------
                #                                       GUARDAR RESULTADO
                # ----------------------------------------------------------------------------------------------
                if value != None and value != False:
                    struct_report = struct_report.replace(
                        '$_val' + str(conf.z_sequence) + '_$',
                        ("{:,.2f}".format(value) if type(value) is float else str(value)))
                else:
                    struct_report = struct_report.replace(
                        '$_val' + str(conf.z_sequence) + '_$', '')

            # Limpiar vals no calculados
            for sequence_val in range(1, 101):
                struct_report = struct_report.replace('$_val' + str(sequence_val) + '_$', '')

            # Retonar PDF
            self.struct_report_contract_template = struct_report
            datas = {
                'id': self.id,
                'model': 'hr.contract'
            }

            return {
                'type': 'ir.actions.report',
                'report_name': 'zue_contract_templates.struct_report_contract_templates',
                'report_type': 'qweb-pdf',
                'datas': datas
            }
        else:
            raise ValidationError('No ha configurado platilla de contrato, por favor verificar.')
