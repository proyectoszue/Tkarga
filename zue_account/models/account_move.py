

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime

#MOVIMIENTO CONTABLE ENCABEZADO

class account_move(models.Model):
    _inherit = 'account.move'

    supplier_invoice_number = fields.Char(string='Nº de factura del proveedor',help="La referencia de esta factura proporcionada por el proveedor.", copy=False)
    supplier_invoice_attachment = fields.Many2one('documents.document',string="Soporte") #fields.Binary(string="Soporte")
    iva_amount = fields.Float('Valor IVA', compute='_compute_amount_iva', store=True)
    tax_base_amount = fields.Float('Valor Base Impuestos', compute='_compute_tax_base_amount', store=True)
    # l10n_co_edi_type = fields.Char(string='Tipo de Documento', required=False)
    accounting_closing_id = fields.Many2one('annual.accounting.closing', string='Cierre contable anual', ondelete='cascade')
    is_invoice_ref = fields.Boolean('No referencia factura', default=False)
    move_ref_id = fields.Many2one('account.move', string='Factura a rectificar', domain="[('state', '=', 'posted'),('move_type', '=', 'out_invoice')]")

    @api.onchange('move_ref_id')
    def _get_entities(self):
        for record in self:
            if record.move_ref_id.name:
                record.ref = 'Reversión de: ' + record.move_ref_id.name

    # FIX TEMPORAL ERROR action_delete_duplicates
    def action_delete_duplicates(self):
        return True

    # # Borrar
    # def button_process_edi_web_services(self):
    #     return

    # supplier_invoice_attachment_name = fields.Char(string="Soporte Filename")
    @api.depends('line_ids', 'invoice_line_ids')
    def _compute_amount_iva(self):
        iva_amount = 0

        if self.invoice_line_ids.tax_id:
            obj_taxes = self.env['account.tax'].search([('name', 'ilike', 'IVA')])
            if len(obj_taxes) > 0:
                percent = obj_taxes[0].amount

                for lines in self.invoice_line_ids:
                    for taxes in lines.tax_ids:
                        if taxes.ids[0] in obj_taxes.ids:
                            iva_amount += lines.price_subtotal * percent / 100

        self.iva_amount = iva_amount

    @api.depends('line_ids', 'invoice_line_ids')
    def _compute_tax_base_amount(self):
        for record in self:
            tax_base_amount = 0

            if record.invoice_line_ids.tax_id:
                for lines in record.invoice_line_ids:
                    if tax_base_amount > 0:
                        break

                    # for taxes in lines.tax_ids:
                    #     if not taxes.l10n_co_edi_type.retention:
                    #         tax_base_amount = record.amount_untaxed
                    #         break

            record.tax_base_amount = tax_base_amount

    @api.constrains('line_ids','invoice_line_ids')
    def _check_line_ids(self):
        for record in self:
            # Permitir generar cierre anual sin distribución analítica.
            if record.accounting_closing_id:
                continue

            for lines in record.line_ids:
                # if lines.required_partner and not lines.partner_id:
                    # raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga un tercero y este no ha sido digitado. Por favor verifique!'))

                if 'stock_move_id' in self.env['account.move']._fields:
                    if lines.required_analytic_account and not lines.analytic_distribution and not record.stock_move_id.picking_id:
                        if lines.price_total > 0:
                            raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))
                else:
                    if lines.required_analytic_account and not lines.analytic_distribution:
                        if lines.price_total > 0:
                            raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))

            # for lines in record.invoice_line_ids:
            #     if lines.required_partner and not lines.partner_id:
            #         raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga un tercero y este no ha sido digitado. Por favor verifique!'))

                if 'stock_move_id' in self.env['account.move']._fields:
                    if lines.required_analytic_account and not lines.analytic_distribution and not record.stock_move_id.picking_id:
                        if lines.price_total > 0:
                            raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))
                else:
                    if lines.required_analytic_account and not lines.analytic_distribution:
                        if lines.price_total > 0:
                            raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))

    # @api.constrains('supplier_invoice_number')
    # def _check_supplier_invoice(self):
    #     for record in self:
    #         if record.move_type == 'in_invoice': #and record.is_rcm == False:
    #             obj_move = self.env['account.move'].search([('supplier_invoice_number', '=', record.supplier_invoice_number),('id','!=',record.id)])
    #             if len(obj_move) > 0:
    #                 raise ValidationError('El número de factura digitado ya existe, por favor verificar.')

    def button_draft(self):
        """
        Restablecer a borrador sin recalcular apuntes contables existentes.
        Se usa skip_invoice_sync para inhibir _sync_dynamic_lines durante
        el cambio de estado posted → draft.
        """
        moves_to_protect = self.filtered(lambda m: m.state == 'posted')

        if moves_to_protect:
            return super(
                account_move,
                moves_to_protect.with_context(
                    skip_invoice_sync=True,
                    check_move_validity=False,
                )
            ).button_draft()

        return super().button_draft()

    # ZUE Inicio Ajustes calculo de base minima
    def zue_check_minimum_base(self):
        """Aplica base mínima por impuesto:
        - Si t.base_affected_only_taxes_id: base = suma del MONTO de ese otro impuesto (AIU) en el documento (solo líneas donde t aplique).
        - Si no: base = suma de subtotales (antes de IVA) de esas líneas.
        Si la base acumulada < minimum_base -> remover t de todas esas líneas.
        """
        for move in self:
            # Omitimos notas
            if move.move_type in ('out_refund', 'in_refund'):
                continue

            lines = move.invoice_line_ids
            if not lines:
                continue

            # Filtramos impuestos presentes en las líneas que manejan base mínima
            taxes_to_check = lines.mapped('tax_ids').filtered(lambda t: getattr(t, 'has_minimum_base', False))
            if not taxes_to_check:
                continue

            currency = move.currency_id
            partner = move.partner_id
            is_refund = move.move_type in ('out_refund', 'in_refund')

            # Precalcular por línea los montos por impuesto (para luego poder sumar AIU, grupos, etc.)
            per_line = {}
            for il in lines:
                if not il.tax_ids:
                    continue
                price_unit = il.price_unit * (1 - (il.discount or 0.0) / 100.0)
                res = il.tax_ids.compute_all(price_unit, currency, il.quantity, product=il.product_id, partner=partner, is_refund=is_refund, handle_price_include=True)
                amounts_by_tax = {}
                for t in res.get('taxes', []):
                    # acumulamos por si el mismo tax aparece fraccionado
                    amounts_by_tax[t['id']] = amounts_by_tax.get(t['id'], 0.0) + t['amount']

                per_line[il.id] = {
                    'line': il,
                    'amounts_by_tax': amounts_by_tax,
                    'subtotal': il.price_subtotal,  # antes de IVA (y demás impuestos)
                }

            # Sumar hijos de impuestos recursivamente
            def flatten_ids(tax):
                ids = {tax.id}
                if getattr(tax, 'amount_type', '') == 'group' and tax.children_tax_ids:
                    for ch in tax.children_tax_ids:
                        ids |= flatten_ids(ch)
                return ids

            taxes_to_remove = set()

            # Evaluar cada impuesto con base mínima
            for tax in taxes_to_check:
                min_required = tax.minimum_base or 0.0
                if min_required <= 0.0:
                    continue

                # Solo líneas que usan este impuesto
                candidate_line_ids = [il.id for il in lines if tax in il.tax_ids]
                if not candidate_line_ids:
                    continue

                # Base = suma del MONTO del "otro impuesto" (ej. AIU) si está configurado
                if getattr(tax, 'base_affected_only_taxes_id', False):
                    base_tax = tax.base_affected_only_taxes_id
                    base_ids = flatten_ids(base_tax)
                    base_sum = 0.0
                    for lid in candidate_line_ids:
                        info = per_line.get(lid)
                        if not info:
                            continue
                        amts = info['amounts_by_tax']
                        base_sum += sum(amts.get(tid, 0.0) for tid in base_ids)

                # Si NO, base = suma de SUBTOTALES (antes de IVA) de esas líneas
                else:
                    base_sum = sum(per_line.get(lid, {}).get('subtotal', 0.0) for lid in candidate_line_ids)

                # Comparar contra base mínima y marcar para remover
                if base_sum < min_required:
                    taxes_to_remove.add(tax.id)

            # Remover impuestos marcados y limpiar redondeos
            if taxes_to_remove:
                for il in lines:
                    current = set(il.tax_ids.ids)
                    rem = list(current & taxes_to_remove)
                    if rem:
                        il.write({'tax_ids': [(3, tid) for tid in rem]})

                # Eliminar líneas contables de impuestos removidos para que no queden valores
                # residuales en el asiento (retención/CxC-CxP).
                tax_lines_to_unlink = move.line_ids.filtered(
                    lambda l: l.display_type == 'tax'
                    and l.tax_line_id
                    and l.tax_line_id.id in taxes_to_remove
                )
                if tax_lines_to_unlink:
                    tax_lines_to_unlink.with_context(dynamic_unlink=True).unlink()

                # borrar líneas de redondeo ligadas a impuestos removidos (strategy=biggest_tax)
                if move.invoice_cash_rounding_id and move.invoice_cash_rounding_id.strategy == 'biggest_tax':
                    rounding_lines = move.line_ids.filtered(lambda l: l.display_type == 'rounding')
                    if rounding_lines:
                        to_unlink = rounding_lines.filtered(lambda rl: bool(set(rl.tax_ids.ids) & taxes_to_remove))
                        if to_unlink:
                            to_unlink.unlink()

                # Recalcular totales
                move._compute_tax_totals()
                move._compute_amount()
    # ZUE Fin Ajustes calculo de base minima

    @api.onchange('partner_id')
    def _onchange_assign_invoice_user(self):
        self.invoice_user_id = self.partner_id.user_id

    @api.model_create_multi
    def create(self, values_list):
        invoice_res = super(account_move, self).create(values_list)
        for invoice in invoice_res:
            if invoice.partner_id:
                invoice.partner_id.validate_check_fields_required()

            if invoice.move_type in ('out_refund', 'in_refund') \
                    and not invoice.move_ref_id \
                    and hasattr(invoice, 'reversed_entry_id') \
                    and invoice.reversed_entry_id:
                invoice.move_ref_id = invoice.reversed_entry_id.id

        return invoice_res

    def write(self, vals):
        invoice = super(account_move, self).write(vals)
        for record in self:
            if record.partner_id:
                record.partner_id.validate_check_fields_required()
            # Ejecutar en guardado final, pero evitar el flujo de carga desde catálogo.
            if record.state == 'draft' \
                    and record.move_type in ('out_invoice', 'in_invoice', 'out_receipt', 'in_receipt') \
                    and not (
                        self.env.context.get('from_product_catalog')
                        or self.env.context.get('default_from_product_catalog')
                        or self.env.context.get('skip_zue_minimum_base')
                    ):
                record.zue_check_minimum_base()

        return invoice

    def action_post(self):
        closing_moves_to_check = self.filtered(lambda m: m.accounting_closing_id and m.state == 'draft')
        for move in closing_moves_to_check:
            lock_dates = move._get_violated_lock_dates(move.date, move._affect_tax_report())
            if lock_dates:
                lock_date_info = move.company_id._format_lock_dates(lock_dates)
                raise ValidationError(_(
                    "No es posible publicar el cierre contable '%(closing)s' con fecha %(date)s porque el periodo esta bloqueado (%(lock_date_info)s). Desbloquee el periodo y vuelva a intentar.",
                    closing=move.accounting_closing_id.display_name,
                    date=move.date,
                    lock_date_info=lock_date_info,
                ))

        # Se valida base mínima al confirmar para garantizar consistencia contable
        # en el asiento final de impuestos y CxC/CxP.
        invoices_to_check = self.filtered(
            lambda m: m.state == 'draft'
            and m.move_type in ('out_invoice', 'in_invoice', 'out_receipt', 'in_receipt')
        )
        if invoices_to_check:
            invoices_to_check.zue_check_minimum_base()
        return super(account_move, self).action_post()

class annual_accounting_closing(models.Model):
    _name = 'annual.accounting.closing'
    _description = 'Cierre contable anual'

    name = fields.Char('Nombre')
    balance = fields.Float('Saldo')
    closing_year = fields.Integer('Año de cierre')
    counter_contab = fields.Integer(compute='compute_counter_contab', string='Movimientos')
    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', string='Diario destino', company_dependent=True)
    counterparty_account = fields.Many2one('account.account', string='Cuenta contrapartida')
    filter_account_ids = fields.Many2many('account.group', string="Cuentas a cerrar")
    partner_id = fields.Many2one('res.partner', 'Tercero de cierre', default=lambda self: self.env.company.partner_id.id)
    closing_by_partner = fields.Boolean('Cerrar por tercero')

    def compute_counter_contab(self):
        count = self.env['account.move'].search_count([('accounting_closing_id', '=', self.id)])
        self.counter_contab = count

    def call_up_closing_wizard(self):
        yes_no = ''
        no_delete = False

        if self.counter_contab > 0:
            obj_contab = self.env['account.move'].search([('accounting_closing_id', '=', self.id)])
            for rows in obj_contab:
                if rows.state != 'draft':
                    no_delete = True
                    break
            if no_delete:
                return {'messages': [{'record': False, 'type': 'warning',
                                      'message': 'Ya hay documentos publicados. No es posible continuar!', }]}
            else:
                obj_move = self.env['account.move'].search([('accounting_closing_id', '=', self.id)])
                obj_move.unlink()
                self.generate_accounting_closing()
        else:
            self.generate_accounting_closing()

    def return_action_to_open(self):
        res = {
            'name': 'Movimientos',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': "[('accounting_closing_id','in',[" + str(self._ids[0]) + "])]"
        }
        return res

    def generate_accounting_closing(self):
        if not self.journal_id:
            raise ValidationError(_("Debe indicar el diario destino."))
        year = str(self.closing_year)
        start_date = '01/01/' + year
        end_date = '31/12/' + year
        row_count = 0
        accounts = ''

        if self.closing_by_partner:
            if not self.partner_id:
                raise ValidationError(_("No se ha especificado el tercero de cierre. Por favor verifique!"))
            if not self.filter_account_ids:
                raise ValidationError(_("No se han especificado las cuentas de cierre. Por favor verifique!"))
        else:
            if not self.counterparty_account:
                raise ValidationError(_("No se han especificado la cuenta de contrapartida. Por favor verifique!"))

        if self.filter_account_ids:
            for account in self.filter_account_ids:
                row_count += 1
                if row_count == 1:
                    if row_count == len(self.filter_account_ids):
                        accounts = '(' + account.code_prefix_start + '%)'
                    else:
                        accounts = '(' + account.code_prefix_start + '%|'
                elif row_count == len(self.filter_account_ids):
                    accounts += account.code_prefix_start + '%)'
                else:
                    accounts += account.code_prefix_start + '%|'
        else:
            accounts = '4%|5%|6%|7%'

        d_start_date = datetime.strptime(start_date, '%d/%m/%Y')
        d_end_date = datetime.strptime(end_date, '%d/%m/%Y')

        query = '''
                with saldo_anterior as (
                    select aml.account_id, aml.partner_id, sum(aml.debit - aml.credit) as saldo_anterior
                    from account_move am
                    inner join account_move_line aml on am.id = aml.move_id
                    inner join account_account aa on aml.account_id = aa.id and coalesce(aa.code_store->>'1', '') similar to '%s' 
                    where am."date" < '%s' and am.company_id = %s and am.state = 'posted' 
                    group by aml.account_id, aml.partner_id
                )
                select aml.account_id, aml.partner_id, coalesce(sa.saldo_anterior, 0) + sum(aml.debit - aml.credit) as saldo
                from account_move am
                inner join account_move_line aml on am.id = aml.move_id
                inner join account_account aa on aml.account_id = aa.id and coalesce(aa.code_store->>'1', '') similar to '%s' 
                left join saldo_anterior sa on aml.account_id = sa.account_id and aml.partner_id = sa.partner_id
                where am."date" between '%s' and '%s' and am.company_id = %s and am.state = 'posted' 
                group by aml.account_id, aml.partner_id, sa.saldo_anterior 
                ''' % (accounts, str(d_start_date), self.company_id.id, accounts, str(d_start_date), str(d_end_date), self.company_id.id)

        self.env.cr.execute(query)
        result_query = self.env.cr.fetchall()

        if not result_query:
            raise ValidationError(_("No se encontraron movimientos para el año especificado. Por favor verifique!"))

        line_ids = []
        move_dict = {
            'company_id': self.env.company.id,
            'ref': 'Cierre contable año: ' + year,
            'journal_id': self.journal_id.id,
            'date': d_end_date,
            'accounting_closing_id': self.id
        }

        total = 0
        for result in result_query:
            account_id = result[0]
            partner_id = result[1]
            balance = result[2]

            debit = 0
            credit = 0
            total += balance

            if balance > 0:
                credit = abs(balance)
            elif balance < 0:
                debit = abs(balance)
            else:
                continue

            line = {
                'name': 'Cierre contable año: ' + year,
                'partner_id': partner_id,
                'account_id': account_id,
                'journal_id': self.journal_id.id,
                'date': d_end_date,
                'debit': debit,
                'credit': credit,
            }
            line_ids.append(line)

            if self.closing_by_partner:
                line = {
                    'name': 'Cierre contable año: ' + year,
                    'partner_id': self.partner_id.id,
                    'account_id': account_id,
                    'journal_id': self.journal_id.id,
                    'date': d_end_date,
                    'debit': credit,
                    'credit': debit,
                }
                line_ids.append(line)
        debit = 0
        credit = 0
        if total > 0:
            debit = abs(total)
        elif total < 0:
            credit = abs(total)

        if not self.closing_by_partner:
            line = {
                'name': 'Cierre contable año: ' + year,
                'partner_id': self.env.company.partner_id.id,
                'account_id': self.counterparty_account.id,
                'journal_id': self.journal_id.id,
                'date': d_end_date,
                'debit': debit,
                'credit': credit
            }
            line_ids.append(line)

        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
        move = self.env['account.move'].create(move_dict)
        self.balance = total

        return True
