from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    z_entity_code_cgn = fields.Char(string='Código de la entidad - CGN')
    z_bank_auto_reconcile_receivable_payable_only = fields.Boolean(string='Auto conciliación bancaria a CxC/CxP', default=False, help='Si se activa, la conciliacion bancaria automatica solo tomara cuentas por cobrar y por pagar.')
    z_bank_auto_reconcile_exact_match_only = fields.Boolean(string='Auto conciliacion bancaria solo valor exacto', default=False, help='Si se activa, la conciliacion bancaria automatica solo cerrara cruces exactos y dejara las diferencias para revision manual.')
    z_folder_multicash_to_validate_id = fields.Many2one('documents.document', string='Carpeta Multicash - Por Validar', domain=[('type', '=', 'folder'), ('shortcut_document_id', '=', False)])
    z_folder_multicash_validate_id = fields.Many2one('documents.document', string='Carpeta Multicash - Validado', domain=[('type', '=', 'folder'), ('shortcut_document_id', '=', False)])
    z_folder_multicash_issue_id = fields.Many2one('documents.document', string='Carpeta Multicash - Con Novedad', domain=[('type', '=', 'folder'), ('shortcut_document_id', '=', False)])
    z_folder_retention_certificates_id = fields.Many2one('documents.document', string='Carpeta certificados de retención', domain=[('type', '=', 'folder'), ('shortcut_document_id', '=', False)])

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    z_entity_code_cgn = fields.Char(related='company_id.z_entity_code_cgn', string='Código de la entidad - CGN', readonly=False)
    z_bank_auto_reconcile_receivable_payable_only = fields.Boolean(related='company_id.z_bank_auto_reconcile_receivable_payable_only', string='Auto conciliación bancaria a CxC/CxP', readonly=False)
    z_qty_thread_moves_balance = fields.Integer(string='Cantidad de registros - Hilos balance', default=10000)
    z_qty_thread_balance = fields.Integer(string='Cantidad de bloques - Hilos balance', default=5)
    # Documentos Multicash
    z_folder_multicash_to_validate_id = fields.Many2one(related='company_id.z_folder_multicash_to_validate_id',
                                                        string='Carpeta Multicash - Por Validar', readonly=False)
    z_folder_multicash_validate_id = fields.Many2one(related='company_id.z_folder_multicash_validate_id',
                                                     string='Carpeta Multicash - Validado', readonly=False)
    z_folder_multicash_issue_id = fields.Many2one(related='company_id.z_folder_multicash_issue_id',
                                                  string='Carpeta Multicash - Con Novedad', readonly=False)
    z_folder_retention_certificates_id = fields.Many2one(related='company_id.z_folder_retention_certificates_id',
                                                         string='Carpeta certificados de retención', readonly=False)

    def set_values(self):
        super().set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('zue_account.z_qty_thread_moves_balance', self.z_qty_thread_moves_balance)
        set_param('zue_account.z_qty_thread_balance', self.z_qty_thread_balance)

    def get_values(self):
        res = super().get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['z_qty_thread_moves_balance'] = get_param('zue_account.z_qty_thread_moves_balance')
        res['z_qty_thread_balance'] = get_param('zue_account.z_qty_thread_balance')
        return res
