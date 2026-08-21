/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AgedPartnerBalanceFilters } from "@account_reports/components/aged_partner_balance/filters";

patch(AgedPartnerBalanceFilters.prototype, {
    get filterExtraOptionsData() {
        return {
            ...super.filterExtraOptionsData,
            show_supplier_invoice_number: {
                name: _t("Mostrar Factura Proveedor"),
            },
            show_invoice_user_name: {
                name: _t("Mostrar Asesor"),
            },
            show_partner_name: {
                name: _t("Mostrar Cliente"),
            },
            show_partner_user_name: {
                name: _t("Mostrar Asesor Cliente"),
            },
        };
    },
});
