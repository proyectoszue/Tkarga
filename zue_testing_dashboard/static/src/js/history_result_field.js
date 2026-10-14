import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { ZueProcessResultViewer } from "@zue_testing_dashboard/js/core_process_result_viewer";

/** Core: widget del Historial que reutiliza el viewer de proceso. */
export class ZueTestingHistoryResultField extends Component {
    static template = "zue_testing_dashboard.HistoryResultField";
    static components = { ZueProcessResultViewer };
    static props = { ...standardFieldProps };

    get resultLine() {
        const rawValue = this.props.record.data[this.props.name];
        if (!rawValue) {
            return false;
        }
        let payload = false;
        try {
            payload = JSON.parse(rawValue);
        } catch {
            return false;
        }
        if (!payload || typeof payload !== "object") {
            return false;
        }
        return {
            id: this.props.record.resId || 0,
            sequence: payload.sequence || 0,
            technical_name: payload.technical_name || "",
            test_type: payload.test_type || "process",
            calculated_lines: payload.calculated_lines || [],
            worked_days_lines: payload.worked_days_lines || [],
            not_applied_lines: payload.not_applied_lines || [],
            obtained_info: payload.obtained_info || [],
        };
    }
}

registry.category("fields").add("zue_testing_history_result", {
    component: ZueTestingHistoryResultField,
    supportedTypes: ["text"],
});
