# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class account_bank_statment(models.Model):
    _inherit = "account.bank.statement"

    z_reconciling_id = fields.Many2one('zue.reconciling.items.encab', 'Partida conciliatoria')


class account_bank_statement_line(models.Model):
    _inherit = "account.bank.statement.line"

    z_reconciling_id = fields.Many2one(related='statement_id.z_reconciling_id', store=True, readonly=True, string='Partida conciliatoria')


class account_move_reconciling(models.Model):
    _inherit = "account.move"

    z_reconciling_id = fields.Many2one('zue.reconciling.items.encab', 'Partida conciliatoria', copy=False, index=True)


class zue_reconciling_items_encab(models.Model):
    _name = 'zue.reconciling.items.encab'
    _description = 'Encabezado partidas conciliatorias'

    name = fields.Char(string='Nombre', required=True)
    z_year = fields.Integer('Año', required=True)
    z_month = fields.Selection([('1', 'Enero'),('2', 'Febrero'),('3', 'Marzo'),('4', 'Abril'),('5', 'Mayo'),
                              ('6', 'Junio'),('7', 'Julio'),('8', 'Agosto'),('9', 'Septiembre'),('10', 'Octubre'),
                              ('11', 'Noviembre'),('12', 'Diciembre')], string='Mes', required=True)
    z_reconciling_detail = fields.One2many('zue.reconciling.items.detail', 'z_reconciling_encab', string='Detalle partidas conciliatorias')
    z_statement_ids = fields.One2many('account.bank.statement', 'z_reconciling_id', string='Extractos generados')
    z_statement_line_ids = fields.One2many('account.bank.statement.line', 'z_reconciling_id', string='Registros generados')
    z_move_ids = fields.One2many('account.move', 'z_reconciling_id', string='Asientos creados')
    state = fields.Selection([('draft','Borrador'),('processed','Procesado')], 'Estado', default='draft')
    z_counter_extract = fields.Integer(compute='_compute_generated_counters', string='Extractos')
    z_counter_record = fields.Integer(compute='_compute_generated_counters', string='Registros')
    z_counter_move = fields.Integer(compute='_compute_generated_counters', string='Asientos')
    z_counter_opening_move = fields.Integer(compute='_compute_generated_counters', string='Apertura')
    z_counter_closing_move = fields.Integer(compute='_compute_generated_counters', string='Cierre')
    z_search_all = fields.Boolean('Busqueda todos los meses anteriores')

    @api.depends('z_statement_ids', 'z_statement_line_ids', 'z_move_ids')
    def _compute_generated_counters(self):
        for record in self:
            record.z_counter_extract = len(record.z_statement_ids)
            record.z_counter_record = len(record.z_statement_line_ids)
            record.z_counter_move = len(record.z_move_ids)
            record.z_counter_opening_move = len(record.z_move_ids.filtered('statement_line_id'))
            record.z_counter_closing_move = len(record.z_move_ids.filtered('reversed_entry_id'))

    def return_action_to_open(self):
        self.ensure_one()
        res = {
            'name': 'Extractos bancarios',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'account.bank.statement',
            'target': 'current',
            'domain': [('id', 'in', self.z_statement_ids.ids)],
        }
        return res

    def return_action_to_open_lines(self):
        self.ensure_one()
        return {
            'name': 'Registros generados',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.bank.statement.line',
            'target': 'current',
            'domain': [('id', 'in', self.z_statement_line_ids.ids)],
        }

    def return_action_to_open_moves(self):
        self.ensure_one()
        return {
            'name': 'Asientos creados',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': [('id', 'in', self.z_move_ids.ids)],
        }

    def return_action_to_open_opening_moves(self):
        self.ensure_one()
        opening_moves = self.z_move_ids.filtered('statement_line_id')
        return {
            'name': 'Asientos apertura',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': [('id', 'in', opening_moves.ids)],
        }

    def return_action_to_open_closing_moves(self):
        self.ensure_one()
        closing_moves = self.z_move_ids.filtered('reversed_entry_id')
        return {
            'name': 'Asientos cierre',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': [('id', 'in', closing_moves.ids)],
        }

    def _reverse_closing_moves(self, move_commands, reverse_date, journal_id):
        reversal = self.env['account.move.reversal'].create(
            {
                'move_ids': move_commands,
                'date': reverse_date,
                'reason': 'ZUE: Cierre partidas conciliatorias',
                'journal_id': journal_id,
                'company_id': self.env.company.id,
            }
        )
        reversal.reverse_moves()
        reversal.new_move_ids.write({'z_reconciling_id': self.id})
        return reversal.new_move_ids.filtered(lambda move: move.state == 'draft')

    def _create_closing_statement_lines(self, statement_line_vals):
        statement_lines = self.env['account.bank.statement.line'].create(statement_line_vals)
        statement_lines.move_id.write({'z_reconciling_id': self.id})
        return statement_lines

    def search_reconciling_items(self):
        date_start = '01/' + str(self.z_month) + '/' + str(self.z_year)
        date_start = datetime.strptime(date_start, '%d/%m/%Y')

        date_end = date_start + relativedelta(months=1)
        date_end = date_end - timedelta(days=1)

        date_start = date_start.date()
        date_end = date_end.date()

        where_date = "B.date <= %(date_end)s" if self.z_search_all else "B.date >= %(date_start)s AND B.date <= %(date_end)s"
        query = f'''
                select B.date, A.payment_ref, A.partner_id, A.amount, A.statement_id, A.move_id, B.journal_id, A.id 
                from account_bank_statement_line A
                inner join account_move B on A.move_id = B.id and B.state = 'posted'
                where A.company_id = %(company_id)s and A.is_reconciled IS NOT TRUE and {where_date}
                order by B.journal_id, B.date, A.id
            '''

        self.env.cr.execute(query, {'company_id': self.env.company.id,
                                    'date_start': date_start,
                                    'date_end': date_end
                                    })
        list_items = self.env.cr.dictfetchall()

        reconciling_detail = []
        self.z_reconciling_detail.unlink()

        for row in list_items:
            reconciling_detail.append({'z_reconciling_encab': self.id,
                                       'z_date': row['date'],
                                       'z_payment_ref': row['payment_ref'],
                                       'z_partner_id': row['partner_id'],
                                       'z_amount': row['amount'],
                                       'z_statement_id': row['statement_id'],
                                       'z_move_id': row['move_id'],
                                       'z_journal_id': row['journal_id'],
                                       'z_bank_statement_line': row['id']})

        if reconciling_detail:
            self.env['zue.reconciling.items.detail'].create(reconciling_detail)
        else:
            raise ValidationError(_('No se encontraron partidas conciliatorias pendientes en el periodo seleccionado. Por favor verifique!'))
        return True

    def process(self):
        reverse_moves_to_post = self.env['account.move']

        date_start = '01/' + str(self.z_month) + '/' + str(self.z_year)
        date_start = datetime.strptime(date_start, '%d/%m/%Y')

        date_end = date_start + relativedelta(months=1)

        date_start = date_start.date()
        date_end = date_end.date()
        date_end_p = (date_end - timedelta(days=1))

        if self.z_search_all:
            date_end_p = date.today()

        statement_date = date_start if self.z_search_all else date_end
        current_journal = self.env['account.journal']
        journal_items = self.env['zue.reconciling.items.detail']

        def _process_journal_group(journal, items):
            nonlocal reverse_moves_to_post
            if not journal or not items:
                return

            obj_statement = self.env['account.bank.statement'].create(
                {
                    'name': 'PARTIDAS CONCILIATORIAS ' + str(date_start) + ' al ' + str(date_end) + ' ' + journal.name,
                    'journal_id': journal.id,
                    'date': statement_date,
                    'company_id': self.env.company.id,
                    'z_reconciling_id': self.id
                }
            )

            move_commands = [(4, move.id) for move in items.mapped('z_move_id')]
            if move_commands:
                reverse_moves_to_post |= self._reverse_closing_moves(move_commands, date_end_p, journal.id)

            statement_vals = []
            for item in items.sorted(lambda detail: (detail.z_date or statement_date, detail.id)):
                payment_ref = item.z_payment_ref or item.z_move_id.payment_reference or item.z_move_id.ref or '/'
                statement_vals.append({
                    'date': statement_date,
                    'name': "/",
                    'journal_id': journal.id,
                    'partner_id': item.z_partner_id.id,
                    'amount': item.z_amount,
                    'statement_id': obj_statement.id,
                    'payment_ref': payment_ref,
                })

            if statement_vals:
                self._create_closing_statement_lines(statement_vals)

        details = self.z_reconciling_detail.sorted(
            lambda item: ((item.z_journal_id or item.z_move_id.journal_id).id, item.z_date or statement_date, item.id)
        )

        for item in details:
            journal = item.z_journal_id or item.z_move_id.journal_id
            if not journal:
                raise ValidationError(_('No se encontró diario bancario para una de las partidas conciliatorias. Por favor verifique!'))

            if current_journal and journal != current_journal:
                _process_journal_group(current_journal, journal_items)
                journal_items = self.env['zue.reconciling.items.detail']

            current_journal = journal
            journal_items |= item

        _process_journal_group(current_journal, journal_items)

        # Se marca la linea del extracto como conciliado
        self.z_reconciling_detail.z_bank_statement_line.write({'is_reconciled': True})

        # Publicar las reversas creadas en este proceso sin depender del ref,
        # ya que puede variar por idioma.
        if reverse_moves_to_post:
            reverse_moves_to_post.action_post()

        self.state = 'processed'

        return True


class zue_reconciling_items_detail(models.Model):
    _name = 'zue.reconciling.items.detail'
    _description = 'Detalle partidas conciliatorias'
    _order = 'z_journal_id,z_date'

    z_reconciling_encab = fields.Many2one('zue.reconciling.items.encab', 'Encabezado partidas conciliatorias')
    z_date = fields.Date('Fecha')
    z_payment_ref = fields.Char('Etiqueta')
    z_partner_id = fields.Many2one('res.partner', 'Asociado')
    z_amount = fields.Float('Importe')
    z_statement_id = fields.Many2one('account.bank.statement', 'Extracto')
    z_move_id = fields.Many2one('account.move', 'Movimiento Contable')
    z_journal_id = fields.Many2one('account.journal', string='Diario')
    z_bank_statement_line = fields.Many2one('account.bank.statement.line', string='Det. Extracto')


class SequenceMixin(models.AbstractModel):
    """Mechanism used to have an editable sequence number.

    Be careful of how you use this regarding the prefixes. More info in the
    docstring of _get_last_sequence.
    """

    _inherit = 'sequence.mixin'

    def _constrains_date_sequence(self):
        # Make it possible to bypass the constraint to allow edition of already messed up documents.
        # /!\ Do not use this to completely disable the constraint as it will make this mixin unreliable.
        constraint_date = fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
            'sequence.mixin.constraint_start_date',
            '1970-01-01'
        ))
        for record in self:
            date = fields.Date.to_date(record[record._sequence_date_field])
            sequence = record[record._sequence_field]
            if sequence and date and date > constraint_date:
                format_values = record._get_sequence_format_param(sequence)[1]
                if (
                    format_values['year'] and format_values['year'] != date.year % 10**len(str(format_values['year']))
                    or format_values['month'] and format_values['month'] != date.month
                ):
                    raise ValidationError(_(
                        "The %(date_field)s (%(date)s) doesn't match the sequence number of the related %(model)s (%(sequence)s)\n"
                        "You will need to clear the %(model)s's %(sequence_field)s to proceed.\n"
                        "In doing so, you might want to resequence your entries in order to maintain a continuous date-based sequence.",
                        date=format_date(self.env, date),
                        sequence=sequence,
                        date_field=record._fields[record._sequence_date_field]._description_string(self.env),
                        sequence_field=record._fields[record._sequence_field]._description_string(self.env),
                        model=self.env['ir.model']._get(record._name).display_name,
                    ))
