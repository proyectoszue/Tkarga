from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders, draft=False):
        if orders:
            for record in orders:
                if 'data' in record:
                    record['data']['to_invoice'] = True
                    record['data']['invoice'] = True

        res = super(PosOrder, self).create_from_ui(orders, draft=draft)
        if res:
            orders_ids = self.browse([o['id'] for o in res if o.get('id')])
            for order in orders_ids:
                if order.account_move:
                    try:
                        order.account_move.send_all_process()
                        _logger.info("Factura %s enviada a FE correctamente.", order.account_move.name)
                    except Exception as e:
                        _logger.error("Error enviando FE para factura %s: %s", order.account_move.name, str(e))
        return res