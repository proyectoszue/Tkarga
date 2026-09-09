/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async save(params) {
        const isNewSalaryRule =
            this.props.resModel === "hr.salary.rule" && this.model.root.isNew;
        const saved = await super.save(...arguments);
        if (saved && isNewSalaryRule) {
            this.env.services.notification.add(
                _t(
                    "¡Importante! No olvide asociar esta regla en los XML de Nómina Electrónica y Nómina de Ajuste."
                ),
                { type: "warning", sticky: true }
            );
        }
        return saved;
    },
});
