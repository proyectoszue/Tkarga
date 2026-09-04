/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    onMounted() {
        super.onMounted(...arguments);
        if (
            this.pos.config.canInvoice &&
            (!this.currentOrder.isRefund || this.currentOrder.isToInvoice())
        ) {
            this.currentOrder.setToInvoice(true);
        }
    },
});
