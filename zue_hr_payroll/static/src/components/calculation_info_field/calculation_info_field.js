/** @odoo-module **/

import { Component, useRef, markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { usePopover } from "@web/core/popover/popover_hook";
import { _t } from "@web/core/l10n/translation";

const EMPTY_DETAIL_HTML = markup(
    `<div class="alert alert-info mb-0 py-2 px-2 small">` +
        `Aún no hay detalle del cálculo. Use el botón <strong>Calcular hoja</strong> para generarlo.` +
    `</div>`
);

class ZueCalculationInfoPopover extends Component {
    static template = "zue_hr_payroll.ZueCalculationInfoPopover";
    static props = {
        html: true,
        close: { type: Function, optional: true },
    };
}

export class ZueCalculationInfoField extends Component {
    static template = "zue_hr_payroll.ZueCalculationInfoField";
    static props = { ...standardFieldProps };

    setup() {
        this.iconRef = useRef("icon");
        this.popover = usePopover(ZueCalculationInfoPopover, { position: "left" });
    }

    get detailHtml() {
        return this.props.record.data[this.props.name] || "";
    }

    get hasText() {
        return Boolean(this.detailHtml);
    }

    get isManual() {
        return String(this.detailHtml).includes("o_zue_calc_manual");
    }

    get iconClass() {
        if (this.isManual) {
            return "text-warning";
        }
        if (this.hasText) {
            return "text-info";
        }
        return "text-muted";
    }

    get iconFaClass() {
        if (this.isManual) {
            return "fa fa-exclamation-triangle";
        }
        return "fa fa-info-circle";
    }

    get ariaLabel() {
        if (this.isManual) {
            return _t("Ajuste manual");
        }
        if (this.hasText) {
            return _t("Cómo se calculó");
        }
        return _t("Calcular hoja para ver el detalle");
    }

    onMouseEnter() {
        if (this.popover.isOpen) {
            return;
        }
        this.popover.open(this.iconRef.el, {
            html: this.hasText ? markup(this.detailHtml) : EMPTY_DETAIL_HTML,
        });
    }

    onMouseLeave() {
        this.popover.close();
    }
}

export const zueCalculationInfoField = {
    component: ZueCalculationInfoField,
    displayName: _t("Cómo se calculó"),
    supportedTypes: ["text", "char", "html"],
};

registry.category("fields").add("zue_calculation_info", zueCalculationInfoField);
