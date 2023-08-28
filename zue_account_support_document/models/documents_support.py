from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import base64
from datetime import date

class sending_support_document(models.Model):
    _name = 'sending.support.document'
    _description = 'Envios de documentos soporte'

    name = fields.Char('Nombre')
    initial_date = fields.Date('Fecha inicial', required=True)
    end_date = fields.Date('Fecha final', required=True)
    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
                                default=lambda self: self.env.company)
    journal_resolution_id = fields.Many2one(related='company_id.journal_support_document_co', string='Diario Resolución')
    observations = fields.Char('Observaciones')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('ac', 'Asignación de Consecutivo'),
        ('xml', 'XMLs'),
        ('ws', 'Enviar WS'),
        ('finished', 'Finalizado'),
    ], string='Estado', default='draft', copy=False)
    executing_document_support_ids = fields.One2many('sending.support.document.detail', 'document_support_id', string='Ejecución')
    qty_failed = fields.Integer(string='Cantidad Fallidos / Sin Respuesta', default=0, copy=False)
    qty_done = fields.Integer(string='Cantidad Aceptados', default=0, copy=False)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "DS {} a {} - {}".format(str(record.initial_date),str(record.end_date),record.company_id.name)))
        return result

    def consecutive_assignment(self):
        #Elimine información del detalle en caso de existir
        self.env['sending.support.document.detail'].search([('document_support_id', '=', self.id)]).unlink()
        #Se obtienen los movimientos publicados en el rango de fechas que tienen un diario con documento soporte
        obj_moves = self.env['account.move'].search([('state', '=', 'posted'),
                                                     ('date', '>=', self.initial_date), ('date', '<=', self.end_date),
                                                     ('move_type', 'not in', ['out_refund', 'in_refund']),
                                                     ('journal_id.document_analyze','=',True),
                                                     ('x_support_document_sent', '=', False)]) #Se asignan unicamente apuntes que aun no se han enviado
        obj_moves_lines = self.env['account.move.line'].search([('move_id','in',obj_moves.ids),
                                                                ('partner_id.zue_electronic_invoice_fiscal_regimen', '=', '49'),
                                                                ('partner_id.obliged_invoice','=',False),
                                                                ('account_id.accounting_class','=','RESULTADO')])
        #Obtener diario consecutivo dian
        journal_support_document_co = self.company_id.journal_support_document_co
        sequence_dian = journal_support_document_co.secure_sequence_id

        #Insertar movimientos
        if len(obj_moves_lines) == 0:
            raise ValidationError(_('No se encontro información de acuerdo a los filtros ingresados.'))

        lst_moves = []
        for move in obj_moves_lines:
            dict_move = {
                'document_support_id': self.id,
                'partner_id': move.partner_id.id,
                'move_id': move.move_id.id,
                'line_move_id': move.id,
                'line_move_ids': '/',
                'concept': move.name,
                'first_concept': '/',
                'amount': move.debit - move.credit,
                'journal_id':move.move_id.journal_id.id,
                'prefix_doc_support': '/',
                'item_doc_support': 0,
                'consecutive_doc_support': '0',
            }
            lst_moves.append(dict_move)
        #Se guarda la data en pandas
        moves_df = pd.DataFrame(lst_moves)
        # Se agrupa por tercero, asiento contable y diario
        group_moves_df = moves_df.groupby(
            by=['document_support_id', 'partner_id', 'move_id', 'line_move_ids', 'first_concept', 'journal_id',
                'prefix_doc_support', 'item_doc_support', 'consecutive_doc_support'], group_keys=False,
            as_index=False).sum()
        #Se obtiene el primer concepto de cada detalle y los apuntes contables
        sequence_number_next = journal_support_document_co.sequence_number_next
        count_sequence = 0
        for i,j in group_moves_df.iterrows():
            concepts = moves_df.loc[(moves_df['move_id'] == group_moves_df.loc[i,'move_id']) & (moves_df['partner_id'] == group_moves_df.loc[i,'partner_id']), 'concept']
            line_move_ids_series = moves_df.loc[(moves_df['move_id'] == group_moves_df.loc[i,'move_id']) & (moves_df['partner_id'] == group_moves_df.loc[i,'partner_id']), 'line_move_id']
            group_moves_df.loc[i,'first_concept'] = concepts.values[0]
            group_moves_df.loc[i,'line_move_ids'] = ','.join(map(str, line_move_ids_series.values))
            group_moves_df.loc[i, 'prefix_doc_support'] = journal_support_document_co.code
            group_moves_df.loc[i, 'item_doc_support'] = sequence_number_next+count_sequence
            group_moves_df.loc[i, 'consecutive_doc_support'] = sequence_dian._next()
            count_sequence+=1
        #Salvar proceso
        lst_moves_finally = group_moves_df.to_dict(orient='records')
        for dict_move in lst_moves_finally:
            # Se eliminan las columnas que no se van guardar
            del dict_move['line_move_id']
            #Se obtienen los apuntes contables
            dict_move['line_move_ids'] = list(map(int,dict_move['line_move_ids'].split(',')))
            #Se guarda en la tabla detalle del proceso
            self.env['sending.support.document.detail'].create(dict_move)
        self.state = 'ac'

    def cancel_process(self):
        obj_detail = self.env['sending.support.document.detail'].search([('document_support_id', '=', self.id)])
        len_obj_detail = len(obj_detail)
        obj_detail.unlink()
        #Reversar secuencia obtenida
        journal_support_document_co = self.company_id.journal_support_document_co
        if journal_support_document_co.sequence and journal_support_document_co.sequence_number_next:
            sequence = journal_support_document_co.sequence._get_current_sequence()
            sequence_ant = journal_support_document_co.sequence_number_next - len_obj_detail
            sequence.sudo().number_next = sequence_ant
        self.write({'state': 'draft'})

    def create_xmls(self):
        raise ValidationError(_('En Desarrollo.'))

class sending_support_document_datail(models.Model):
    _name = 'sending.support.document.detail'
    _description = 'Envios de documentos soporte detalle'

    document_support_id = fields.Many2one('sending.support.document', string='Documentos soporte', ondelete='cascade')
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

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} - {} - {}".format(record.consecutive_doc_support,record.partner_id.name,record.move_id.name)))
        return result