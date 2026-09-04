# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api, _


class account_journal(models.Model):
    _inherit = 'account.journal'

    document_analyze = fields.Boolean(string='Reportar documento')

    def _z_extract_sequence_number(self, sequence_value, prefix='DSE'):
        """Extrae el número del consecutivo cuando coincide con el prefijo esperado."""
        if not sequence_value:
            return 0
        sequence_text = str(sequence_value).strip()
        expected_prefix = (prefix or '').strip()
        if expected_prefix and not sequence_text.startswith(expected_prefix):
            return 0
        match = re.search(r'(\d+)(?!.*\d)', sequence_text)
        return int(match.group(1)) if match else 0

    def _z_get_last_support_document_sequence_number(self, prefix='DSE'):
        """Obtiene el último número usado en DS/NC DS para la compañía del diario."""
        self.ensure_one()
        last_number = 0
        detail_models = (
            'sending.support.document.detail',
            'sending.notes.document.support.detail',
        )
        for model_name in detail_models:
            details = self.env[model_name].sudo().search([
                ('document_support_id.company_id', '=', self.company_id.id),
                ('consecutive_doc_support', '!=', False),
            ], order='id desc', limit=100)
            for detail in details:
                number = self._z_extract_sequence_number(detail.consecutive_doc_support, prefix=prefix)
                if number:
                    last_number = max(last_number, number)
                    break
        return last_number

    def _z_get_dse_sequence_vals(self):
        """Valores para crear la secuencia DSE, copiados de una existente o por defecto."""
        self.ensure_one()
        template = self.env['ir.sequence'].sudo().search([
            ('prefix', '=', 'DSE'),
            ('name', 'ilike', 'DSE Secuencia'),
        ], limit=1, order='id asc')
        if template:
            vals = {
                'name': template.name,
                'implementation': template.implementation,
                'prefix': template.prefix,
                'suffix': template.suffix or False,
                'padding': template.padding,
                'number_increment': template.number_increment,
                'number_next': 1,
                'active': True,
                'use_date_range': template.use_date_range,
                'code': template.code or False,
            }
        else:
            vals = {
                'name': 'DSE Secuencia',
                'implementation': 'no_gap',
                'prefix': 'DSE',
                'suffix': False,
                'padding': 1,
                'number_increment': 1,
                'number_next': 1,
                'active': True,
                'use_date_range': False,
            }
        last_number = self._z_get_last_support_document_sequence_number(prefix=vals.get('prefix'))
        increment = vals.get('number_increment') or 1
        vals['number_next'] = (last_number + increment) if last_number else 1
        return vals

    def _z_create_support_document_sequence(self):
        """Crea la secuencia DSE para la compañía del diario."""
        self.ensure_one()
        vals = self._z_get_dse_sequence_vals()
        vals['company_id'] = self.company_id.id
        return self.env['ir.sequence'].sudo().create(vals)

    def _z_assign_support_document_sequence(self):
        """Asigna en z_secure_sequence_id la secuencia DSE de la misma compañía del diario."""
        self.ensure_one()
        if self.z_secure_sequence_id:
            return self.z_secure_sequence_id

        Sequence = self.env['ir.sequence'].sudo()
        sequence = Sequence.search([
            ('prefix', '=', 'DSE'),
            ('company_id', '=', self.company_id.id),
        ], order='id asc', limit=1)

        if not sequence:
            sequence = self._z_create_support_document_sequence()

        self.sudo().write({'z_secure_sequence_id': sequence.id})
        self.invalidate_recordset(['z_secure_sequence_id'])
        return self.z_secure_sequence_id

    @api.model_create_multi
    def create(self, vals_list):
        journals = super().create(vals_list)
        for journal in journals.filtered(lambda j: j.document_analyze and not j.z_secure_sequence_id):
            journal._z_assign_support_document_sequence()
        return journals

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ('document_analyze', 'code', 'company_id')):
            for journal in self.filtered(lambda j: j.document_analyze and not j.z_secure_sequence_id):
                journal._z_assign_support_document_sequence()
        return res
