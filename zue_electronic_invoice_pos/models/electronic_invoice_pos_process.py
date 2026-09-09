from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _is_pos_electronic_invoice(self):
        return bool(self.pos_order_ids)

    def _get_fe_xml_prefixes(self):
        if self._is_pos_electronic_invoice():
            return "POSFacElectronica_", "POS_FE_v2_"
        return super()._get_fe_xml_prefixes()

    def _get_fe_web_service_name(self, service_name):
        if self._is_pos_electronic_invoice():
            return {
                "upload_file_fe": "uploadDocumentpos",
                "check_status_fe": "documentStatuspos",
                "download_pdf_fe": "documentpdfpos",
                "get_cufe_fe": "documentcufepos",
            }.get(service_name, service_name)
        return super()._get_fe_web_service_name(service_name)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def sync_from_ui(self, orders):
        for order in orders or []:
            order["to_invoice"] = True

        res = super().sync_from_ui(orders)

        order_ids = [order["id"] for order in res.get("pos.order", []) if order.get("id")]
        for order in self.browse(order_ids):
            if order.account_move:
                try:
                    order.account_move.send_all_process()
                    _logger.info("Factura %s enviada a FE correctamente.", order.account_move.name)
                except Exception as e:
                    _logger.error(
                        "Error enviando FE para factura %s: %s",
                        order.account_move.name,
                        str(e),
                    )
        return res
