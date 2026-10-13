import { Component, useState } from "@odoo/owl";
import { formatCurrency } from "@web/core/currency";
import { user } from "@web/core/user";
import { formatFloat } from "@web/core/utils/numbers";

/**
 * Core: viewer genérico de resultados de proceso.
 * Layouts de dominio (SS/provisiones) se agregan por patch desde payroll.
 */
export class ZueProcessResultViewer extends Component {

    static template = "zue_testing_dashboard.ProcessResultViewer";
    static props = {
        line: Object,
    };


    setup() {
        this.viewerState = useState({
            periodClosureTabs: {},
            periodClosureRows: {},
            processTabs: {},
        });
    }

    get line() {
        return this.props.line || {};
    }

    get companyCurrencyId() {
        return user.activeCompany?.currency_id || false;
    }

    formatMonetaryValue(value) {
        if (value === null || value === undefined || value === false || value === "") {
            return "";
        }
        const amount = Number(value);
        if (Number.isNaN(amount)) {
            return String(value);
        }
        if (!this.companyCurrencyId) {
            return formatFloat(amount, {digits: [false, 2]});
        }
        return formatCurrency(amount, this.companyCurrencyId);
    }

    formatProcessResultValue(value) {
        if (value === null || value === undefined || value === false || value === "") {
            return "-";
        }
        if (typeof value === "number") {
            return formatFloat(value, {digits: [false, 2]});
        }
        return String(value);
    }

    formatProcessResultMonetaryValue(value) {
        if (value === null || value === undefined || value === false || value === "") {
            return "-";
        }
        return this.formatMonetaryValue(value) || "-";
    }

    formatProcessInfoValue(infoLine) {
        if (typeof infoLine?.value === "number") {
            return this.formatProcessResultMonetaryValue(infoLine.value);
        }
        return this.formatProcessResultValue(infoLine?.value);
    }

    getProcessCalculatedLines(line) {
        return Array.isArray(line?.calculated_lines) ? line.calculated_lines : [];
    }

    getProcessWorkedDaysLines(line) {
        return Array.isArray(line?.worked_days_lines) ? line.worked_days_lines : [];
    }

    getProcessNotAppliedLines(line) {
        return Array.isArray(line?.not_applied_lines) ? line.not_applied_lines : [];
    }

    getProcessObtainedInfo(line) {
        return Array.isArray(line?.obtained_info) ? line.obtained_info : [];
    }

    /** Dominio: true si el resultado usa layout de cierre de periodo. */
    isPeriodClosureResult(line) {
        return false;
    }

    getPeriodClosureLineKey(line) {
        return String(line?.sequence || line?.id || "line");
    }

    getProcessResultTab(line) {
        return this.viewerState.processTabs[this.getPeriodClosureLineKey(line)] || "worked_days";
    }

    setProcessResultTab(line, tabName) {
        this.viewerState.processTabs[this.getPeriodClosureLineKey(line)] = tabName;
    }
}
