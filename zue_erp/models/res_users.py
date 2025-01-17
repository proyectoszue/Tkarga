# -*- coding: utf-8 -*-
from odoo import models, fields, api

class res_users(models.Model):
    _inherit = 'res.users'
    
    #Sucursal
    branch_ids = fields.Many2many('zue.res.branch', string='Sucursal', ondelete='restrict')    
    #Firma
    signature_documents = fields.Binary(string='Firma ZUE')
    #Firma autorizada para certificado laboral
    signature_certification_laboral = fields.Boolean('Firma autorizada para certificado laboral')

    def _can_import_remote_urls(self):
        """ Hook to decide whether the current user is allowed to import
        images via URL (as such an import can DOS a worker). By default,
        allows the administrator group.

        :rtype: bool
        """
        self.ensure_one()
        return self._is_group_import_remote_urls()

    def _is_group_import_remote_urls(self):
        self.ensure_one()
        return self._is_superuser() or self.has_group('zue_erp.group_import_remote_urls') or self.has_group('base.group_erp_manager')