from psycopg2 import Error as Psycopg2Error

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ZueAccountClosingReversalWizard(models.TransientModel):
    _name = 'zue.account.closing.reversal.wizard'
    _description = 'Reversión cierre contable (eliminación definitiva)'

    z_company_id = fields.Many2one('res.company',string='Compañía',required=True,default=lambda self: self.env.company)
    z_closing_year = fields.Integer(string='Año de cierre',required=True,default=lambda self: fields.Date.today().year - 1)
    z_move_id = fields.Many2one('account.move',string='Documento de cierre (asiento)',required=True,
                                domain="[('accounting_closing_id', '!=', False), ""('accounting_closing_id.closing_year', '=', z_closing_year), ""('company_id', '=', z_company_id)]")

    # ── Validaciones ────────────────────────────────────────────────────────────

    def _assert_move_is_closing_for_year(self):
        """Verifica que el asiento seleccionado pertenezca al año y compañía indicados."""
        self.ensure_one()

        if not self.z_move_id:
            raise UserError(_('Debe seleccionar un documento de cierre.'))

        closing = self.z_move_id.accounting_closing_id
        if not closing:
            raise UserError(_('El asiento seleccionado no está vinculado a un cierre contable anual.'))

        if closing.closing_year != self.z_closing_year:
            raise UserError(_('El año del cierre no coincide con el asiento seleccionado.'))

        if self.z_move_id.company_id != self.z_company_id:
            raise UserError(_('El asiento no pertenece a la compañía indicada.'))

    def _assert_not_fiscally_locked(self):
        """Impide la acción si la fecha del asiento cae en un periodo bloqueado."""
        self.ensure_one()
        move       = self.z_move_id
        violations = move._get_violated_lock_dates(move.date, move._affect_tax_report())
        if violations:
            info = self.env['res.company']._format_lock_dates(violations)
            raise UserError(_(
                'La fecha del asiento de cierre está dentro de un periodo bloqueado '
                '(%(locks)s). No se puede eliminar.', locks=info
            ))

    def _assert_move_deletable_by_policy(self):
        """Impide eliminar asientos con hash inalterable."""
        self.ensure_one()
        if self.z_move_id.inalterable_hash:
            raise UserError(_(
                'Este asiento pertenece a una cadena de hash inalterable y no puede eliminarse.'
            ))

    # ── Eliminación SQL ─────────────────────────────────────────────────────────

    def _sql_purge_closing_move(self, move_id):
        """
        Elimina el asiento y sus apuntes directamente en base de datos.
        Al ser SQL puro no genera trazabilidad ni registros de auditoría en el ORM.
        El orden respeta las FK para evitar errores de integridad referencial.
        """
        cr = self.env.cr

        # Obtiene los ids de los apuntes del asiento
        cr.execute('SELECT id FROM account_move_line WHERE move_id = %s', (move_id,))
        line_ids = [row[0] for row in cr.fetchall()]

        if line_ids:
            # Elimina conciliaciones parciales que referencian los apuntes
            cr.execute("""
                DELETE FROM account_partial_reconcile
                 WHERE debit_move_id  IN %s
                    OR credit_move_id IN %s
            """, (tuple(line_ids), tuple(line_ids)))

            # Limpia la referencia a conciliación total antes de borrar las líneas
            cr.execute('UPDATE account_move_line SET full_reconcile_id = NULL WHERE move_id = %s',(move_id,))

            # Elimina la relación muchos a muchos con impuestos
            cr.execute('DELETE FROM account_move_line_account_tax_rel WHERE account_move_line_id IN %s',(tuple(line_ids),))

            # Elimina líneas analíticas asociadas
            cr.execute('DELETE FROM account_analytic_line WHERE move_line_id IN %s',(tuple(line_ids),))

            # Elimina mensajes y seguidores de los apuntes
            cr.execute("DELETE FROM mail_followers WHERE res_model = 'account.move.line' AND res_id IN %s",(tuple(line_ids),))
            cr.execute("DELETE FROM mail_message WHERE model = 'account.move.line' AND res_id IN %s",(tuple(line_ids),))

        # Elimina los apuntes contables
        cr.execute('DELETE FROM account_move_line WHERE move_id = %s', (move_id,))

        # Elimina mensajes y seguidores del asiento
        cr.execute("DELETE FROM mail_followers WHERE res_model = 'account.move' AND res_id = %s",(move_id,))
        cr.execute("DELETE FROM mail_message WHERE model = 'account.move' AND res_id = %s",(move_id,))

        # Elimina el asiento contable
        cr.execute('DELETE FROM account_move WHERE id = %s', (move_id,))

    def _cleanup_closing_if_empty(self, closing):
        """Si ya no quedan asientos del cierre, resetea su saldo."""
        remaining = self.env['account.move'].search_count([('accounting_closing_id', '=', closing.id)])
        if remaining == 0:
            closing.balance = 0.0

    # ── Acción principal ────────────────────────────────────────────────────────

    def action_execute(self):
        self.ensure_one()

        # Validaciones previas a la eliminación
        self._assert_move_is_closing_for_year()
        self._assert_not_fiscally_locked()
        self._assert_move_deletable_by_policy()

        move_id = self.z_move_id.id
        closing = self.z_move_id.accounting_closing_id

        # Ejecuta el borrado dentro de un savepoint:
        # si algo falla a mitad del SQL la transacción no queda en estado inconsistente
        try:
            with self.env.cr.savepoint():
                self._sql_purge_closing_move(move_id)
        except Psycopg2Error as exc:
            raise UserError(_('No se pudo eliminar el asiento por restricciones en la base de datos. ''Detalle técnico: %(detail)s', detail=str(exc))) from exc

        # Invalida el caché del ORM para que no sirva los registros ya eliminados
        self.env['account.move'].invalidate_model()
        self.env['account.move.line'].invalidate_model()

        # Limpia el cierre si ya no tiene asientos asociados
        self._cleanup_closing_if_empty(closing)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title':   _('Cierre eliminado'),
                'message': _('Se eliminó el asiento de cierre y sus apuntes correctamente.'),
                'type':    'success',
                'sticky':  False,
                'next':    {'type': 'ir.actions.act_window_close'},
            },
        }