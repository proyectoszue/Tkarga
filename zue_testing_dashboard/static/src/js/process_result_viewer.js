import { Component, useState } from "@odoo/owl";
import { formatCurrency } from "@web/core/currency";
import { user } from "@web/core/user";
import { formatFloat } from "@web/core/utils/numbers";

/**
 * Render unico de resultados de pruebas de proceso.
 * Lo usan tanto la ejecucion en vivo del panel como el Historial,
 * para que ambas vistas muestren los mismos tabs y tablas.
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

    isSocialSecurityResult(line) {
        if (line?.technical_name === "test_simulate_seguridad_social") {
            return true;
        }
        const info = this.getProcessObtainedInfo(line);
        return Boolean(info[0] && info[0].layout === "social_security");
    }

    isProvisionsResult(line) {
        if (line?.technical_name === "test_simulate_provisiones") {
            return true;
        }
        const info = this.getProcessObtainedInfo(line);
        return Boolean(info[0] && info[0].layout === "provisions");
    }

    isPeriodClosureResult(line) {
        return this.isProvisionsResult(line) || this.isSocialSecurityResult(line);
    }

    getPeriodClosureLineKey(line) {
        return String(line?.sequence || line?.id || "line");
    }

    getPeriodClosureResultTab(line) {
        return this.viewerState.periodClosureTabs[this.getPeriodClosureLineKey(line)] || "header";
    }

    setPeriodClosureResultTab(line, tabName) {
        this.viewerState.periodClosureTabs[this.getPeriodClosureLineKey(line)] = tabName;
    }

    getPeriodClosureSelectedRowIndex(line) {
        const selected = this.viewerState.periodClosureRows[this.getPeriodClosureLineKey(line)];
        if (selected === 0 || selected) {
            return selected;
        }
        return 0;
    }

    setPeriodClosureSelectedRowIndex(line, index) {
        this.viewerState.periodClosureRows[this.getPeriodClosureLineKey(line)] = index;
    }

    getPeriodClosureHeaderInfo(line) {
        const payload = this.isProvisionsResult(line)
            ? this.getProvisionsPayload(line)
            : this.getSocialSecurityPayload(line);
        const headerInfo = payload?.header_info;
        return headerInfo && typeof headerInfo === "object" ? headerInfo : {};
    }

    getPeriodClosureAccounting(line) {
        if (this.isProvisionsResult(line)) {
            return this.getProvisionsAccounting(line);
        }
        if (this.isSocialSecurityResult(line)) {
            return this.getSocialSecurityAccounting(line);
        }
        return false;
    }

    hasPeriodClosureAccounting(line) {
        return Boolean(this.getPeriodClosureAccounting(line));
    }

    getPeriodClosureAccountingProcesses(line) {
        const accounting = this.getPeriodClosureAccounting(line);
        return Array.isArray(accounting?.processes) ? accounting.processes : [];
    }

    getProvisionsPayload(line) {
        const info = this.getProcessObtainedInfo(line);
        const payload = info.find((item) => item && item.layout === "provisions");
        return payload || {rows: [], warnings: [], accounting: false, header_info: {}};
    }

    getProvisionsRows(line) {
        const rows = this.getProvisionsPayload(line).rows;
        return Array.isArray(rows) ? rows : [];
    }

    getSelectedProvisionsRow(line) {
        const rows = this.getProvisionsRows(line);
        if (!rows.length) {
            return false;
        }
        const index = this.getPeriodClosureSelectedRowIndex(line);
        return rows[index] || rows[0] || false;
    }

    getProvisionsWarnings(line) {
        const warnings = this.getProvisionsPayload(line).warnings;
        return Array.isArray(warnings) ? warnings : [];
    }

    getProvisionsAccounting(line) {
        const accounting = this.getProvisionsPayload(line).accounting;
        return accounting && typeof accounting === "object" ? accounting : false;
    }

    getDetailFormColumnFields(detail, columnKey) {
        if (!detail || typeof detail !== "object") {
            return [];
        }
        const fields = detail[columnKey];
        return Array.isArray(fields) ? fields : [];
    }

    getProvisionsDetailColumnFields(row, columnKey) {
        return this.getDetailFormColumnFields(row?.detail, columnKey);
    }

    getSocialSecurityPayload(line) {
        const info = this.getProcessObtainedInfo(line);
        const payload = info.find((item) => item && item.layout === "social_security");
        return payload || {segments: [], warnings: [], accounting: false, header_info: {}};
    }

    getSocialSecuritySegments(line) {
        const segments = this.getSocialSecurityPayload(line).segments;
        return Array.isArray(segments) ? segments : [];
    }

    getSelectedSocialSecuritySegment(line) {
        const segments = this.getSocialSecuritySegments(line);
        if (!segments.length) {
            return false;
        }
        const index = this.getPeriodClosureSelectedRowIndex(line);
        return segments[index] || segments[0] || false;
    }

    get socialSecuritySectionDefs() {
        return [
            {key: "info_days", label: "Info y días"},
            {key: "health", label: "Salud"},
            {key: "pension", label: "Pensión"},
            {key: "arp", label: "ARP"},
            {key: "parafiscales", label: "Parafiscales"},
            {key: "absence_dates", label: "Ausencia y fechas"},
        ];
    }

    getSocialSecuritySegmentSectionFields(segment, sectionKey) {
        return this.getDetailFormColumnFields(segment, sectionKey);
    }

    getSocialSecurityWarnings(line) {
        const warnings = this.getSocialSecurityPayload(line).warnings;
        return Array.isArray(warnings) ? warnings : [];
    }

    getSocialSecurityAccounting(line) {
        const accounting = this.getSocialSecurityPayload(line).accounting;
        return accounting && typeof accounting === "object" ? accounting : false;
    }

    formatSocialSecurityFieldValue(fieldRow) {
        const value = fieldRow?.value;
        const valueType = fieldRow?.value_type || "text";
        if (valueType === "monetary") {
            return this.formatProcessResultMonetaryValue(value);
        }
        if (valueType === "percent") {
            if (value === null || value === undefined || value === false || value === "") {
                return "-";
            }
            return `${this.formatProcessResultValue(value)} %`;
        }
        if (valueType === "integer") {
            if (value === null || value === undefined || value === false || value === "") {
                return "-";
            }
            return String(value);
        }
        return this.formatProcessResultValue(value);
    }

    getProcessResultTab(line) {
        return this.viewerState.processTabs[this.getPeriodClosureLineKey(line)] || "worked_days";
    }

    setProcessResultTab(line, tabName) {
        this.viewerState.processTabs[this.getPeriodClosureLineKey(line)] = tabName;
    }
}
