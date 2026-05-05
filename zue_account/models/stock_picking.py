from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # standard Odoo version "19"
    def button_validate(self):
        # Parche funcional de rendimiento:
        # durante la validación de inventario se activa este contexto para que
        # capas posteriores (auditlog/lecturas binarias) usen estrategias livianas
        # y no ralenticen la operación por lectura masiva de adjuntos.
        # bin_size=True fuerza lecturas binarias livianas (tamaño en vez de contenido).
        return super(
            StockPicking,
            self.with_context(
                z_optimize_validate_performance=True,
                bin_size=True,
            ),
        ).button_validate()

    # standard Odoo version "19"
    @api.constrains("scheduled_date", "date_done")
    def _check_backdate_allowed(self):
        # Parche funcional de política:
        # los movimientos de inventario no deben bloquearse
        # por fechas de cierre contable/fiscal.
        # Se mantiene el comportamiento estándar de inventario, pero sin impedir
        # la operación logística por bloqueo contable.
        return
