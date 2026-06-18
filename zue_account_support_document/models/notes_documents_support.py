from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd


class notes_documents_support(models.Model):
    _name = 'notes.documents.support'
    _description = 'Notas documentos soporte'

    name = fields.Char('Nombre')
    initial_date = fields.Date('Fecha inicial', required=True)
    end_date = fields.Date('Fecha final', required=True)
    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
                                default=lambda self: self.env.company)
    journal_resolution_id = fields.Many2one(related='company_id.journal_nc_support_document_co', string='Diario Resolución')
    observations = fields.Char('Observaciones')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('ac', 'Asignación de Consecutivo'),
        ('xml', 'XMLs'),
        ('ws', 'Enviar WS'),
        ('finished', 'Finalizado'),
    ], string='Estado', default='draft', copy=False)
    executing_document_support_ids = fields.One2many('sending.notes.document.support.detail', 'document_support_id', string='Ejecución')
    qty_failed = fields.Integer(string='Cantidad Fallidos / Sin Respuesta', default=0, copy=False)
    qty_done = fields.Integer(string='Cantidad Aceptados', default=0, copy=False)

    def consecutive_assignment(self):
        self.ensure_one()
        Detail = self.env['sending.notes.document.support.detail']
        # Detectar si line_move_ids es M2M (recomendado) o Char
        line_move_field = Detail._fields.get('line_move_ids')
        is_line_move_m2m = bool(line_move_field and line_move_field.type == 'many2many')
        # Limpiar detalle previo
        Detail.search([('document_support_id', '=', self.id)]).unlink()

        obj_moves = self.env['account.move'].search([('state', '=', 'posted'),
            ('date', '>=', self.initial_date), ('date', '<=', self.end_date),
            ('move_type', 'in', ['out_refund', 'in_refund']),
            ('journal_id.document_analyze', '=', True),
            ('x_support_document_sent', '=', False)])

        obj_moves_lines = self.env['account.move.line'].search([('move_id', 'in', obj_moves.ids),
            ('partner_id.zue_electronic_invoice_fiscal_regimen', '=', '49'),
            ('partner_id.obliged_invoice', '=', False),
            ('account_id.accounting_class', '=', 'RESULTADO')])

        if not obj_moves_lines:
            raise ValidationError(_('No se encontro información de acuerdo a los filtros ingresados.'))

        journal_nc_support_document_co = self.company_id.journal_nc_support_document_co
        sequence_dian = journal_nc_support_document_co.z_secure_sequence_id

        # Helper para sacar el siguiente consecutivo de la secuencia (v19 seguro)
        def _next_seq():
            # Preferible en Odoo: next_by_id()
            if hasattr(sequence_dian, 'next_by_id'):
                return str(sequence_dian.next_by_id())
            # fallback (si tu custom usa _next)
            return str(sequence_dian._next())

        # Helper para obtener "item" como tu lógica actual
        def _compute_item(next_seq_str):
            code = journal_nc_support_document_co.code or ''
            # Mantengo tu idea: cortar por longitud del código del diario de resolución
            num_part = next_seq_str[len(code):] if code and next_seq_str.startswith(code) else ''.join(ch for ch in next_seq_str if ch.isdigit())
            try:
                return int(num_part) + 1  # <-- mantengo tu +1
            except Exception:
                return 0

        # Agrupar SIN pandas (evita numpy.int64 y acelera)
        grouped = {}
        # key: (partner_id, move_id, journal_id)
        for ml in obj_moves_lines:
            partner_id = ml.partner_id.id
            move = ml.move_id
            move_id = move.id
            journal_id = move.journal_id.id
            key = (partner_id, move_id, journal_id)

            if key not in grouped:
                grouped[key] = {
                    'document_support_id': self.id,
                    'partner_id': partner_id,
                    'move_id': move_id,
                    'journal_id': journal_id,
                    'first_concept': ml.name or '/',
                    'amount': 0.0,
                    'line_ids': [],
                    # se completan luego:
                    'prefix_doc_support': '/',
                    'item_doc_support': 0,
                    'consecutive_doc_support': '0',
                }

            grouped[key]['amount'] += (ml.debit - ml.credit)
            grouped[key]['line_ids'].append(ml.id)

        # Crear detalle con consecutivo por grupo
        for (partner_id, move_id, journal_id), data in grouped.items():
            move = self.env['account.move'].browse(move_id)  # sin query extra real (prefetch)
            data['prefix_doc_support'] = move.journal_id.code or '/'
            seq_str = _next_seq()
            data['item_doc_support'] = _compute_item(seq_str)
            data['consecutive_doc_support'] = move.name or '0'

            line_ids = data.pop('line_ids', [])

            # line_move_ids según tipo real del campo
            if is_line_move_m2m:
                data['line_move_ids'] = [(6, 0, line_ids)]
            else:
                # tu implementación actual usa texto con ids separados por coma
                data['line_move_ids'] = ','.join(map(str, line_ids)) if line_ids else '/'

            # Cast “limpio” (por si hay floats raros)
            data['document_support_id'] = int(data['document_support_id'])
            data['partner_id'] = int(data['partner_id'])
            data['move_id'] = int(data['move_id'])
            data['journal_id'] = int(data['journal_id'])
            data['item_doc_support'] = int(data['item_doc_support'] or 0)
            data['amount'] = float(data['amount'] or 0.0)

            Detail.create(data)

        self.state = 'ac'

    def cancel_process(self):
        obj_detail = self.env['sending.notes.document.support.detail'].search([('document_support_id', '=', self.id)])
        # len_obj_detail = len(obj_detail)
        obj_detail.unlink()
        # #Reversar secuencia obtenida
        # journal_nc_support_document_co = self.company_id.journal_nc_support_document_co
        # if journal_nc_support_document_co.sequence_id and journal_nc_support_document_co.sequence_number_next:
        #     sequence = journal_nc_support_document_co.sequence_id._get_current_sequence()
        #     sequence_ant = journal_nc_support_document_co.sequence_number_next - len_obj_detail
        #     sequence.sudo().number_next = sequence_ant
        self.write({'state': 'draft'})

class sending_notes_document_support_detail(models.Model):
    _name = 'sending.notes.document.support.detail'
    _description = 'Envios de notas documentos soporte detalle'

    document_support_id = fields.Many2one('notes.documents.support', string='Documentos soporte NC', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Tercero')
    partner_vat = fields.Char(related='partner_id.vat', string='No. de identificación tercero')
    move_id = fields.Many2one('account.move', string='Asiento contable')
    move_date = fields.Date(related='move_id.date',string='Fecha')
    line_move_ids = fields.Many2many('account.move.line', string='Apuntes contables')
    first_concept = fields.Char(string='Concepto')
    amount = fields.Float(string='Valor')
    journal_id = fields.Many2one('account.journal', string='Diario contable')
    prefix_doc_support = fields.Char(string='Prefijo documento soporte')
    item_doc_support = fields.Integer(string='Item documento soporte')
    consecutive_doc_support = fields.Char(string='Consecutivo documento soporte')
    document_support_reverse_id = fields.Many2one('sending.support.document.detail',string='Documento soporte a reversar', domain="[('partner_id','=',partner_id)]")
    # XML
    xml_file = fields.Binary('XML')
    xml_file_name = fields.Char('XML name')
    result_upload_xml = fields.Text(string='Respuesta envio XML', readonly=True)
    status = fields.Char(string='Estado')
    result_status = fields.Text(string='Descripción estado', readonly=True)
    cuds = fields.Char(string='CUDS')
    transaction_id = fields.Char(string='Id Transacción DS')
    pdf_file = fields.Binary('PDF DS')
    pdf_name = fields.Char('PDF DS name')
    sequence = fields.Char(string='Prefijo+Consecutivo DS')
    resource_type_document = fields.Selection([
        ('ORIGINAL_DOCUMENT', 'Documento original'),
        ('SIGNED_XML', 'XML firmado'),
        ('PDF', 'Archivo PDF'),
        ('DIAN_RESULT', 'Resultado Dian'),
        ('DOCUMENT_TRANSFORMED', 'Documento transformado a la salida'),
        ('ATTACHED_DOCUMENT', 'Attached document de nómina'),
    ], string='Tipo de archivo', default='PDF')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('ac', 'Asignación de Consecutivo'),
        ('xml', 'XMLs'),
        ('ws', 'Enviar WS'),
        ('finished', 'Finalizado'),
    ], string='Estado doc', default='draft', copy=False)

    @api.depends('consecutive_doc_support','partner_id','move_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{} - {} - {}".format(record.consecutive_doc_support,record.partner_id.name,record.move_id.name)
