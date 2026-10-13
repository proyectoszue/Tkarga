import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useOwnedDialogs, useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { Component } from "@odoo/owl";
import {
    ZueTestingDashboard,
} from "@zue_testing_dashboard/js/core_zue_testing_dashboard";

const VERSION_SEARCH_LIMIT = 7;
const VERSION_SEARCH_MORE_LIMIT = 320;

/** Payroll: many2one de contrato (hr.version) para el panel. */
export class ZueDashboardVersionMany2One extends Component {
    static template = "zue_testing_dashboard.VersionMany2One";
    static components = { AutoComplete };
    static props = {
        value: { type: [Number, String, { value: false }, { value: "" }], optional: true },
        displayName: { type: String, optional: true },
        update: Function,
        disabled: { type: Boolean, optional: true },
        placeholder: { type: String, optional: true },
    };
    static defaultProps = {
        value: false,
        displayName: "",
        disabled: false,
        placeholder: "",
    };

    setup() {
        this.orm = useService("orm");
        this.addDialog = useOwnedDialogs();
        this.sources = [
            {
                placeholder: _t("Loading..."),
                options: (request) => this.loadOptionsSource(request),
            },
        ];
    }

    async loadOptionsSource(name) {
        if (this.props.disabled) {
            return [];
        }
        if (this.lastProm) {
            this.lastProm.abort(false);
        }
        this.lastProm = this.orm.call(
            "zue.testing.dashboard.session",
            "searchDashboardVersions",
            [],
            {search: name || "", limit: VERSION_SEARCH_LIMIT + 1}
        );
        const options = await this.lastProm;
        const mapped = (options || []).slice(0, VERSION_SEARCH_LIMIT).map((option) => ({
            label: option.label,
            onSelect: () => this.props.update(option.value, option.label),
        }));
        if ((options || []).length > VERSION_SEARCH_LIMIT) {
            mapped.push({
                cssClass: "o_m2o_dropdown_option",
                label: _t("Search More..."),
                onSelect: () => this.onSearchMore(name),
            });
        }
        if (!mapped.length) {
            mapped.push({ label: _t("(no result)") });
        }
        return mapped;
    }

    async onSearchMore(name) {
        let dynamicFilters;
        if (name) {
            const matches = await this.orm.call(
                "zue.testing.dashboard.session",
                "searchDashboardVersions",
                [],
                {search: name, limit: VERSION_SEARCH_MORE_LIMIT}
            );
            const ids = (matches || []).map((item) => item.value);
            dynamicFilters = [{
                description: _t("Quick search: %s", name),
                domain: [["id", "in", ids]],
            }];
        }
        const SelectCreateDialog = registry.category("dialogs").get("select_create");
        this.addDialog(SelectCreateDialog, {
            title: _t("Search: Contrato"),
            resModel: "hr.version",
            noCreate: true,
            multiSelect: false,
            domain: [],
            dynamicFilters,
            context: {},
            onSelected: async (resId) => {
                const versionId = Array.isArray(resId) ? resId[0] : resId;
                await this.selectVersionById(versionId);
            },
        });
    }

    async selectVersionById(versionId) {
        if (!versionId) {
            this.props.update(false, "");
            return;
        }
        const options = await this.orm.call(
            "zue.testing.dashboard.session",
            "searchDashboardVersions",
            [],
            {ids: [versionId], limit: 1}
        );
        const option = (options || [])[0];
        this.props.update(versionId, option ? option.label : String(versionId));
    }

    onChange({ inputValue }) {
        if (!inputValue.length) {
            this.props.update(false, "");
        }
    }
}

ZueTestingDashboard.components = {
    ...ZueTestingDashboard.components,
    ZueDashboardVersionMany2One,
};

/** Payroll: extiende el panel core (detectores, config compartida, inputs de proceso). */
patch(ZueTestingDashboard.prototype, {
    async loadProcessFormOptions() {
        const [applyChargeChoices, contractAplicarChoices, contractPeriodChoices, retentionChoices] = await Promise.all([
            this.orm.call(
                "zue.testing.dashboard.session",
                "getDashboardSelectionOptions",
                ["hr.loans", "apply_charge"]
            ),
            this.orm.call(
                "zue.testing.dashboard.session",
                "getDashboardSelectionOptions",
                ["hr.contract.concepts", "aplicar"]
            ),
            this.orm.call(
                "zue.testing.dashboard.session",
                "getDashboardSelectionOptions",
                ["hr.contract.concepts", "period"]
            ),
            this.orm.call(
                "zue.testing.dashboard.session",
                "getDashboardSelectionOptions",
                ["hr.version", "retention_procedure"]
            ),
        ]);
        this.state.loanApplyChargeChoices = applyChargeChoices || [];
        this.state.contractConceptAplicarChoices = contractAplicarChoices || [];
        this.state.contractConceptPeriodChoices = contractPeriodChoices || [];
        this.state.retentionProcedureChoices = retentionChoices || [];
    },

    get loanApplyChargeChoices() {
        return this.state.loanApplyChargeChoices || [];
    },

    get contractConceptAplicarChoices() {
        return this.state.contractConceptAplicarChoices || [];
    },

    get contractConceptPeriodChoices() {
        return this.state.contractConceptPeriodChoices || [];
    },

    get retentionProcedureChoices() {
        return this.state.retentionProcedureChoices || [];
    },

    get isSocialBenefitsProvider() {
        return this.state.providerModel === "zue.testing.dashboard.hr.liq.benefits.provider";
    },

    get isGeneralLiquidationProvider() {
        return this.state.providerModel === "zue.testing.dashboard.hr.liq.general.provider";
    },

    get isPeriodClosureProvider() {
        return this.state.providerModel === "zue.testing.dashboard.hr.social.security.provider";
    },

    get showGroupSharedConfig() {
        return (
            (this.isSocialBenefitsProvider || this.isGeneralLiquidationProvider || this.isPeriodClosureProvider)
            && this.state.scope === "all"
            && this.selectedCatalogTests.length > 0
        );
    },

    get isPeriodClosureSharedConfig() {
        return this.isPeriodClosureProvider;
    },

    get groupSharedConfig() {
        return this.state.groupSharedConfig;
    },

    getGroupSharedDateValue(fieldName) {
        return this.toDateTimeValue(this.groupSharedConfig[fieldName]);
    },

    setGroupSharedVersion(versionId, versionLabel) {
        this.state.groupSharedConfig = {
            ...this.groupSharedConfig,
            versionId: versionId || false,
            versionLabel: versionLabel || "",
        };
    },

    setGroupSharedDate(fieldName, dateValue) {
        this.state.groupSharedConfig = {
            ...this.groupSharedConfig,
            [fieldName]: this.serializeDateValue(dateValue, "date"),
        };
    },

    setGroupSharedValue(fieldName, value) {
        this.state.groupSharedConfig = {
            ...this.groupSharedConfig,
            [fieldName]: value,
        };
    },

    applyGroupSharedConfig() {
        const shared = this.groupSharedConfig;
        const nextInputs = {...this.state.testInputs};
        let appliedCount = 0;
        for (const test of this.selectedCatalogTests) {
            if (!this.isTestSelected(test.technical_name)) {
                continue;
            }
            const current = this.getProcessTestInputState(test.technical_name);
            if (this.isPeriodClosureSharedConfig) {
                nextInputs[test.technical_name] = {
                    ...current,
                    versionId: shared.versionId || false,
                    versionLabel: shared.versionLabel || "",
                    year: shared.year || "",
                    month: shared.month || false,
                };
            } else {
                nextInputs[test.technical_name] = {
                    ...current,
                    versionId: shared.versionId || false,
                    versionLabel: shared.versionLabel || "",
                    dateStart: shared.dateStart || "",
                    dateEnd: shared.dateEnd || "",
                };
            }
            appliedCount += 1;
        }
        this.state.testInputs = nextInputs;
        this.notification.add(
            _t("Configuración aplicada a %s prueba(s) seleccionada(s).", appliedCount),
            {type: appliedCount ? "success" : "warning"}
        );
    },

    get emptyGroupSharedConfig() {
        return {
            versionId: false,
            versionLabel: "",
            dateStart: "",
            dateEnd: "",
            year: "",
            month: false,
        };
    },

    needsTestInputState(test) {
        return (
            test.test_type === "process"
            || Boolean(test.test_model)
            || this.isAbsencesParametricTest(test)
        );
    },

    showParametricFieldPicker(test) {
        if (this.isAbsencesParametricTest(test)) {
            return false;
        }
        return Boolean(test?.test_model) && test?.test_type !== "process";
    },

    validateBeforeRun(selectedTechnicalNames) {
        return this.validateProcessNoveltiesBeforeRun(selectedTechnicalNames);
    },

    get providerGroups() {
        const byModel = Object.fromEntries(
            (this.moduleGroups || []).map((group) => [group.model, group])
        );
        const toChoice = (model) => {
            const group = byModel[model];
            return group ? {value: group.model, label: group.name} : false;
        };
        const parametricModels = [
            "zue.testing.dashboard.hr.configuration.provider",
            "zue.testing.dashboard.hr.employee.contract.provider",
        ];
        const processModels = [
            "zue.testing.dashboard.hr.liq.general.provider",
            "zue.testing.dashboard.hr.liq.benefits.provider",
            "zue.testing.dashboard.hr.social.security.provider",
        ];
        const parametricChoices = parametricModels.map(toChoice).filter(Boolean);
        const processChoices = processModels.map(toChoice).filter(Boolean);
        const known = new Set([...parametricModels, ...processModels]);
        const leftover = (this.moduleGroups || [])
            .filter((group) => !known.has(group.model))
            .map((group) => ({value: group.model, label: group.name}));
        const groups = [];
        if (parametricChoices.length) {
            groups.push({label: _t("Paramétricas"), choices: parametricChoices});
        }
        if (processChoices.length) {
            groups.push({label: _t("Proceso"), choices: processChoices});
        }
        if (leftover.length) {
            groups.push({label: _t("Otros"), choices: leftover});
        }
        return groups;
    },

    getDefaultTestInputState(test) {
        if (this.isAbsencesParametricTest(test)) {
            return {
                fieldRows: [],
                versionId: false,
                versionLabel: "",
                dateStart: "",
                dateEnd: "",
                leaveTypeId: false,
                leaveTypeLabel: "",
                destinationState: this.getAbsencesDefaultDestinationState(test),
            };
        }
        if (test?.test_type === "process") {
            return {
                fieldRows: [],
                versionId: false,
                versionLabel: "",
                dateStart: "",
                dateEnd: "",
                dateLiquidacion: "",
                datePrima: "",
                dateCesantias: "",
                dateVacaciones: "",
                haveCompensation: false,
                reasonRetiroId: false,
                reasonRetiroLabel: "",
                year: "",
                month: false,
                generateAccounting: false,
                novelties: [],
                overtimes: [],
                loans: [],
                differentConcepts: [],
                independentNovelties: [],
                contractConcepts: [],
                wageChanges: [],
                isAdvanceSeverance: false,
                advanceSeveranceValue: "",
                enjoyedVacations: [],
                paidVacations: [],
                retentionProcedure: false,
                fixedValueRetentionProcedure: "",
                rtfDeductions: [],
            };
        }
        return {fieldRows: []};
    },

    isPeriodicPayrollProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_periodic_payroll";
    },

    isContractLiquidationProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_liquidacion_contrato";
    },

    isIndependentPayrollProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_nomina_independiente";
    },

    isSocialSecurityProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_seguridad_social";
    },

    isProvisionsProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_provisiones";
    },

    isPeriodClosureProcess(testOrName) {
        return this.isSocialSecurityProcess(testOrName) || this.isProvisionsProcess(testOrName);
    },

    get socialSecurityMonthChoices() {
        return [
            {value: "1", label: "Enero"},
            {value: "2", label: "Febrero"},
            {value: "3", label: "Marzo"},
            {value: "4", label: "Abril"},
            {value: "5", label: "Mayo"},
            {value: "6", label: "Junio"},
            {value: "7", label: "Julio"},
            {value: "8", label: "Agosto"},
            {value: "9", label: "Septiembre"},
            {value: "10", label: "Octubre"},
            {value: "11", label: "Noviembre"},
            {value: "12", label: "Diciembre"},
        ];
    },

    isPrimaProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_prima";
    },

    isCesantiasProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return (
            name === "test_simulate_cesantias"
            || name === "test_simulate_intereses_cesantias"
        );
    },

    isVacacionesProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_vacaciones";
    },

    isAbsencesParametricTest(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return typeof name === "string" && name.startsWith("test_create_leave");
    },

    getAbsencesDefaultDestinationState(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        if (name === "test_create_leave_draft") {
            return "draft";
        }
        if (name === "test_create_leave_validate_real") {
            return "real";
        }
        return "forced";
    },

    get absencesDestinationStateChoices() {
        return [
            {value: "draft", label: "Borrador"},
            {value: "real", label: "Validada (flujo real)"},
            {value: "forced", label: "Validada (forzada)"},
        ];
    },

    get absencesLeaveTypeDomain() {
        return [["code", "!=", false]];
    },

    setAbsencesLeaveTypeSelection(technicalName, leaveTypeId, leaveTypeLabel) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                leaveTypeId: leaveTypeId || false,
                leaveTypeLabel: leaveTypeLabel || "",
            },
        };
    },

    isWageChangeProcess(testOrName) {
        return this.isPrimaProcess(testOrName) || this.isCesantiasProcess(testOrName);
    },

    getProcessTestInputState(technicalName) {
        const test = this.selectedCatalogTests.find((item) => item.technical_name === technicalName);
        return this.state.testInputs[technicalName] || this.getDefaultTestInputState(test);
    },

    setProcessTestInputValue(technicalName, fieldName, value) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                [fieldName]: value,
            },
        };
    },

    setProcessVersionSelection(technicalName, versionId, versionLabel) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                versionId: versionId || false,
                versionLabel: versionLabel || "",
                datePrima: "",
                dateCesantias: "",
                dateVacaciones: "",
            },
        };
        if (this.isContractLiquidationProcess(technicalName) && versionId) {
            this.refreshContratoAccrualDates(technicalName);
        }
    },

    setProcessReasonRetiroSelection(technicalName, reasonId, reasonLabel) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                reasonRetiroId: reasonId || false,
                reasonRetiroLabel: reasonLabel || "",
            },
        };
    },

    async refreshContratoAccrualDates(technicalName) {
        const inputState = this.getProcessTestInputState(technicalName);
        if (!inputState.versionId || !this.isContractLiquidationProcess(technicalName)) {
            return;
        }
        try {
            const dates = await this.orm.call(
                "zue.testing.dashboard.session",
                "resolveDashboardContratoAccrualDates",
                [inputState.versionId]
            );
            this.state.testInputs = {
                ...this.state.testInputs,
                [technicalName]: {
                    ...this.getProcessTestInputState(technicalName),
                    datePrima: dates?.date_prima || "",
                    dateCesantias: dates?.date_cesantias || "",
                    dateVacaciones: dates?.date_vacaciones || "",
                },
            };
        } catch (_error) {
            this.state.testInputs = {
                ...this.state.testInputs,
                [technicalName]: {
                    ...this.getProcessTestInputState(technicalName),
                    datePrima: "",
                    dateCesantias: "",
                    dateVacaciones: "",
                },
            };
        }
    },

    getProcessDateValue(technicalName, fieldName) {
        return this.toDateTimeValue(this.getProcessTestInputState(technicalName)[fieldName]);
    },

    onProcessDateChange(technicalName, fieldName, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const patch = {[fieldName]: serialized};
        if (fieldName === "dateEnd" && this.isContractLiquidationProcess(technicalName)) {
            patch.dateLiquidacion = serialized;
        }
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                ...patch,
            },
        };
        this.clampProcessNoveltiesToPeriod(technicalName);
    },

    hasProcessPeriod(technicalName) {
        const inputState = this.getProcessTestInputState(technicalName);
        return Boolean(inputState.dateStart && inputState.dateEnd);
    },

    getProcessPeriodMinDate(technicalName) {
        return this.getProcessDateValue(technicalName, "dateStart") || false;
    },

    getProcessPeriodMaxDate(technicalName) {
        return this.getProcessDateValue(technicalName, "dateEnd") || false;
    },

    getProcessNoveltyMinDate(technicalName, noveltyUid, fieldName) {
        const periodMin = this.getProcessPeriodMinDate(technicalName);
        if (!periodMin) {
            return false;
        }
        if (fieldName === "dateTo") {
            const dateFrom = this.getProcessNoveltyDateValue(technicalName, noveltyUid, "dateFrom");
            if (dateFrom && dateFrom.isValid && dateFrom > periodMin) {
                return dateFrom;
            }
        }
        return periodMin;
    },

    getProcessNoveltyMaxDate(technicalName, noveltyUid, fieldName) {
        const periodMax = this.getProcessPeriodMaxDate(technicalName);
        if (!periodMax) {
            return false;
        }
        if (fieldName === "dateFrom") {
            const dateTo = this.getProcessNoveltyDateValue(technicalName, noveltyUid, "dateTo");
            if (dateTo && dateTo.isValid && dateTo < periodMax) {
                return dateTo;
            }
        }
        return periodMax;
    },

    getProcessRowRangeMinDate(technicalName, dateFromSerialized) {
        const periodMin = this.getProcessPeriodMinDate(technicalName);
        const dateFrom = this.toDateTimeValue(dateFromSerialized);
        if (dateFrom && dateFrom.isValid && periodMin && dateFrom > periodMin) {
            return dateFrom;
        }
        return periodMin || false;
    },

    getProcessRowRangeMaxDate(technicalName, dateToSerialized) {
        const periodMax = this.getProcessPeriodMaxDate(technicalName);
        const dateTo = this.toDateTimeValue(dateToSerialized);
        if (dateTo && dateTo.isValid && periodMax && dateTo < periodMax) {
            return dateTo;
        }
        return periodMax || false;
    },

    isNoveltyDateOutsidePeriod(serializedDate, periodStart, periodEnd) {
        if (!serializedDate) {
            return false;
        }
        if (periodStart && serializedDate < periodStart) {
            return true;
        }
        if (periodEnd && serializedDate > periodEnd) {
            return true;
        }
        return false;
    },

    clampProcessNoveltiesToPeriod(technicalName) {
        const current = this.getProcessTestInputState(technicalName);
        const periodStart = current.dateStart || "";
        const periodEnd = current.dateEnd || "";
        let changed = false;
        const nextNovelties = (current.novelties || []).map((item) => {
            const nextItem = {...item};
            if (this.isNoveltyDateOutsidePeriod(nextItem.dateFrom, periodStart, periodEnd)) {
                nextItem.dateFrom = "";
                changed = true;
            }
            if (this.isNoveltyDateOutsidePeriod(nextItem.dateTo, periodStart, periodEnd)) {
                nextItem.dateTo = "";
                changed = true;
            }
            if (nextItem.dateFrom && nextItem.dateTo && nextItem.dateFrom > nextItem.dateTo) {
                nextItem.dateTo = "";
                changed = true;
            }
            return nextItem;
        });
        const nextOvertimes = (current.overtimes || []).map((item) => {
            const nextItem = {...item};
            if (this.isNoveltyDateOutsidePeriod(nextItem.dateFrom, periodStart, periodEnd)) {
                nextItem.dateFrom = "";
                changed = true;
            }
            if (this.isNoveltyDateOutsidePeriod(nextItem.dateTo, periodStart, periodEnd)) {
                nextItem.dateTo = "";
                changed = true;
            }
            if (nextItem.dateFrom && nextItem.dateTo && nextItem.dateFrom > nextItem.dateTo) {
                nextItem.dateTo = "";
                changed = true;
            }
            return nextItem;
        });
        const nextConcepts = (current.differentConcepts || []).map((item) => {
            const nextItem = {...item};
            if (this.isNoveltyDateOutsidePeriod(nextItem.date, periodStart, periodEnd)) {
                nextItem.date = "";
                changed = true;
            }
            return nextItem;
        });
        const nextIndependentNovelties = (current.independentNovelties || []).map((item) => {
            const nextItem = {...item};
            if (this.isNoveltyDateOutsidePeriod(nextItem.date, periodStart, periodEnd)) {
                nextItem.date = "";
                changed = true;
            }
            return nextItem;
        });
        const nextContractConcepts = (current.contractConcepts || []).map((item) => {
            const nextItem = {...item};
            if (nextItem.dateStart && nextItem.dateEnd && nextItem.dateStart > nextItem.dateEnd) {
                nextItem.dateEnd = "";
                changed = true;
            }
            return nextItem;
        });
        const nextWageChanges = (current.wageChanges || []).map((item) => {
            const nextItem = {...item};
            if (this.isNoveltyDateOutsidePeriod(nextItem.date, periodStart, periodEnd)) {
                nextItem.date = "";
                changed = true;
            }
            return nextItem;
        });
        const nextEnjoyedVacations = (current.enjoyedVacations || []).map((item) => {
            const nextItem = {...item};
            if (this.isNoveltyDateOutsidePeriod(nextItem.dateFrom, periodStart, periodEnd)) {
                nextItem.dateFrom = "";
                changed = true;
            }
            if (this.isNoveltyDateOutsidePeriod(nextItem.dateTo, periodStart, periodEnd)) {
                nextItem.dateTo = "";
                changed = true;
            }
            if (nextItem.dateFrom && nextItem.dateTo && nextItem.dateFrom > nextItem.dateTo) {
                nextItem.dateTo = "";
                changed = true;
            }
            return nextItem;
        });
        const nextPaidVacations = (current.paidVacations || []).map((item) => {
            const nextItem = {...item};
            if (this.isNoveltyDateOutsidePeriod(nextItem.dateStart, periodStart, periodEnd)) {
                nextItem.dateStart = "";
                changed = true;
            }
            return nextItem;
        });
        if (!changed) {
            return;
        }
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...current,
                novelties: nextNovelties,
                overtimes: nextOvertimes,
                differentConcepts: nextConcepts,
                independentNovelties: nextIndependentNovelties,
                contractConcepts: nextContractConcepts,
                wageChanges: nextWageChanges,
                enjoyedVacations: nextEnjoyedVacations,
                paidVacations: nextPaidVacations,
            },
        };
    },

    getProcessNovelties(technicalName) {
        return this.getProcessTestInputState(technicalName).novelties || [];
    },

    createProcessNoveltyRow() {
        this.state.testFieldUid += 1;
        return {
            uid: this.state.testFieldUid,
            workEntryTypeId: false,
            workEntryTypeLabel: "",
            dateFrom: "",
            dateTo: "",
        };
    },

    addProcessNovelty(technicalName) {
        if (!this.hasProcessPeriod(technicalName)) {
            this.notification.add(
                _t("Defina primero Fecha desde y Fecha hasta del escenario."),
                {type: "warning"}
            );
            return;
        }
        const current = this.getProcessTestInputState(technicalName);
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...current,
                novelties: [...(current.novelties || []), this.createProcessNoveltyRow()],
            },
        };
    },

    removeProcessNovelty(technicalName, noveltyUid) {
        const current = this.getProcessTestInputState(technicalName);
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...current,
                novelties: (current.novelties || []).filter((item) => item.uid !== noveltyUid),
            },
        };
    },

    updateProcessNovelty(technicalName, noveltyUid, values) {
        const current = this.getProcessTestInputState(technicalName);
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...current,
                novelties: (current.novelties || []).map((item) => (
                    item.uid === noveltyUid ? {...item, ...values} : item
                )),
            },
        };
    },

    setProcessNoveltyWorkEntryType(technicalName, noveltyUid, workEntryTypeId, workEntryTypeLabel) {
        this.updateProcessNovelty(technicalName, noveltyUid, {
            workEntryTypeId: workEntryTypeId || false,
            workEntryTypeLabel: workEntryTypeLabel || "",
        });
    },

    getProcessNoveltyDateValue(technicalName, noveltyUid, fieldName) {
        const novelty = this.getProcessNovelties(technicalName).find((item) => item.uid === noveltyUid);
        return this.toDateTimeValue(novelty ? novelty[fieldName] : "");
    },

    onProcessNoveltyDateChange(technicalName, noveltyUid, fieldName, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.updateProcessNovelty(technicalName, noveltyUid, {
            [fieldName]: serialized,
        });
    },

    getProcessSectionRows(technicalName, sectionKey) {
        return this.getProcessTestInputState(technicalName)[sectionKey] || [];
    },

    updateProcessSectionRows(technicalName, sectionKey, rows) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                [sectionKey]: rows,
            },
        };
    },

    updateProcessSectionRow(technicalName, sectionKey, rowUid, values) {
        const rows = this.getProcessSectionRows(technicalName, sectionKey).map((item) => (
            item.uid === rowUid ? {...item, ...values} : item
        ));
        this.updateProcessSectionRows(technicalName, sectionKey, rows);
    },

    removeProcessSectionRow(technicalName, sectionKey, rowUid) {
        this.updateProcessSectionRows(
            technicalName,
            sectionKey,
            this.getProcessSectionRows(technicalName, sectionKey).filter((item) => item.uid !== rowUid)
        );
    },

    requireProcessPeriodForSection(technicalName) {
        if (!this.hasProcessPeriod(technicalName)) {
            this.notification.add(
                _t("Defina primero Fecha desde y Fecha hasta del escenario."),
                {type: "warning"}
            );
            return false;
        }
        return true;
    },

    getProcessOvertimes(technicalName) {
        return this.getProcessSectionRows(technicalName, "overtimes");
    },

    addProcessOvertime(technicalName) {
        if (!this.requireProcessPeriodForSection(technicalName)) {
            return;
        }
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "overtimes", [
            ...this.getProcessOvertimes(technicalName),
            {
                uid: this.state.testFieldUid,
                typeOvertimeId: false,
                typeOvertimeLabel: "",
                hours: "",
                dateFrom: "",
                dateTo: "",
            },
        ]);
    },

    removeProcessOvertime(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "overtimes", rowUid);
    },

    setProcessOvertimeValue(technicalName, rowUid, fieldName, value) {
        this.updateProcessSectionRow(technicalName, "overtimes", rowUid, {[fieldName]: value});
    },

    setProcessOvertimeType(technicalName, rowUid, typeOvertimeId, typeOvertimeLabel) {
        this.updateProcessSectionRow(technicalName, "overtimes", rowUid, {
            typeOvertimeId: typeOvertimeId || false,
            typeOvertimeLabel: typeOvertimeLabel || "",
        });
    },

    getProcessOvertimeDateValue(technicalName, rowUid, fieldName) {
        const row = this.getProcessOvertimes(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row[fieldName] : "");
    },

    onProcessOvertimeDateChange(technicalName, rowUid, fieldName, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.setProcessOvertimeValue(technicalName, rowUid, fieldName, serialized);
    },

    getProcessLoans(technicalName) {
        return this.getProcessSectionRows(technicalName, "loans");
    },

    addProcessLoan(technicalName) {
        if (!this.requireProcessPeriodForSection(technicalName)) {
            return;
        }
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "loans", [
            ...this.getProcessLoans(technicalName),
            {
                uid: this.state.testFieldUid,
                salaryRuleId: false,
                salaryRuleLabel: "",
                entityId: false,
                entityLabel: "",
                applyCharge: false,
                amount: "",
                finalSettlement: false,
            },
        ]);
    },

    removeProcessLoan(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "loans", rowUid);
    },

    setProcessLoanValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "loans", rowUid, values);
    },

    getProcessDifferentConcepts(technicalName) {
        return this.getProcessSectionRows(technicalName, "differentConcepts");
    },

    addProcessDifferentConcept(technicalName) {
        if (!this.requireProcessPeriodForSection(technicalName)) {
            return;
        }
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "differentConcepts", [
            ...this.getProcessDifferentConcepts(technicalName),
            {
                uid: this.state.testFieldUid,
                salaryRuleId: false,
                salaryRuleLabel: "",
                date: "",
                amount: "",
                description: "",
                partnerId: false,
                partnerLabel: "",
            },
        ]);
    },

    removeProcessDifferentConcept(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "differentConcepts", rowUid);
    },

    setProcessDifferentConceptValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "differentConcepts", rowUid, values);
    },

    getProcessDifferentConceptDateValue(technicalName, rowUid) {
        const row = this.getProcessDifferentConcepts(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row.date : "");
    },

    onProcessDifferentConceptDateChange(technicalName, rowUid, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.setProcessDifferentConceptValue(technicalName, rowUid, {date: serialized});
    },

    getProcessIndependentNovelties(technicalName) {
        return this.getProcessSectionRows(technicalName, "independentNovelties");
    },

    addProcessIndependentNovelty(technicalName) {
        if (!this.requireProcessPeriodForSection(technicalName)) {
            return;
        }
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "independentNovelties", [
            ...this.getProcessIndependentNovelties(technicalName),
            {
                uid: this.state.testFieldUid,
                salaryRuleId: false,
                salaryRuleLabel: "",
                date: "",
                amount: "",
                description: "",
            },
        ]);
    },

    removeProcessIndependentNovelty(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "independentNovelties", rowUid);
    },

    setProcessIndependentNoveltyValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "independentNovelties", rowUid, values);
    },

    getProcessIndependentNoveltyDateValue(technicalName, rowUid) {
        const row = this.getProcessIndependentNovelties(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row.date : "");
    },

    onProcessIndependentNoveltyDateChange(technicalName, rowUid, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.setProcessIndependentNoveltyValue(technicalName, rowUid, {date: serialized});
    },

    getProcessWageChanges(technicalName) {
        return this.getProcessSectionRows(technicalName, "wageChanges");
    },

    async addProcessWageChange(technicalName) {
        if (!this.requireProcessPeriodForSection(technicalName)) {
            return;
        }
        const inputState = this.getProcessTestInputState(technicalName);
        let currentWage = "";
        if (inputState.versionId) {
            try {
                const wageValue = await this.orm.call(
                    "zue.testing.dashboard.session",
                    "getDashboardVersionWage",
                    [inputState.versionId],
                    {}
                );
                if (wageValue !== false && wageValue !== null && wageValue !== undefined) {
                    currentWage = wageValue;
                }
            } catch (_error) {
                currentWage = "";
            }
        }
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "wageChanges", [
            ...this.getProcessWageChanges(technicalName),
            {
                uid: this.state.testFieldUid,
                date: "",
                currentWage,
                wage: "",
            },
        ]);
    },

    removeProcessWageChange(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "wageChanges", rowUid);
    },

    setProcessWageChangeValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "wageChanges", rowUid, values);
    },

    getProcessEnjoyedVacations(technicalName) {
        return this.getProcessSectionRows(technicalName, "enjoyedVacations");
    },

    addProcessEnjoyedVacation(technicalName) {
        if (!this.requireProcessPeriodForSection(technicalName)) {
            return;
        }
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "enjoyedVacations", [
            ...this.getProcessEnjoyedVacations(technicalName),
            {
                uid: this.state.testFieldUid,
                dateFrom: "",
                dateTo: "",
            },
        ]);
    },

    removeProcessEnjoyedVacation(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "enjoyedVacations", rowUid);
    },

    setProcessEnjoyedVacationValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "enjoyedVacations", rowUid, values);
    },

    getProcessEnjoyedVacationDateValue(technicalName, rowUid, fieldName) {
        const row = this.getProcessEnjoyedVacations(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row?.[fieldName === "dateFrom" ? "dateFrom" : "dateTo"]);
    },

    onProcessEnjoyedVacationDateChange(technicalName, rowUid, fieldName, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const key = fieldName === "dateFrom" ? "dateFrom" : "dateTo";
        this.setProcessEnjoyedVacationValue(technicalName, rowUid, {[key]: serialized});
    },

    getProcessEnjoyedVacationMinDate(technicalName, rowUid, fieldName) {
        const periodMin = this.getProcessPeriodMinDate(technicalName);
        if (!periodMin) {
            return false;
        }
        if (fieldName === "dateTo") {
            const dateFrom = this.getProcessEnjoyedVacationDateValue(technicalName, rowUid, "dateFrom");
            if (dateFrom && dateFrom.isValid && dateFrom > periodMin) {
                return dateFrom;
            }
        }
        return periodMin;
    },

    getProcessEnjoyedVacationMaxDate(technicalName, rowUid, fieldName) {
        const periodMax = this.getProcessPeriodMaxDate(technicalName);
        if (!periodMax) {
            return false;
        }
        if (fieldName === "dateFrom") {
            const dateTo = this.getProcessEnjoyedVacationDateValue(technicalName, rowUid, "dateTo");
            if (dateTo && dateTo.isValid && dateTo < periodMax) {
                return dateTo;
            }
        }
        return periodMax;
    },

    getProcessPaidVacations(technicalName) {
        return this.getProcessSectionRows(technicalName, "paidVacations");
    },

    addProcessPaidVacation(technicalName) {
        if (!this.requireProcessPeriodForSection(technicalName)) {
            return;
        }
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "paidVacations", [
            ...this.getProcessPaidVacations(technicalName),
            {
                uid: this.state.testFieldUid,
                days: "",
                dateStart: "",
            },
        ]);
    },

    removeProcessPaidVacation(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "paidVacations", rowUid);
    },

    setProcessPaidVacationValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "paidVacations", rowUid, values);
    },

    getProcessPaidVacationDateValue(technicalName, rowUid) {
        const row = this.getProcessPaidVacations(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row?.dateStart);
    },

    onProcessPaidVacationDateChange(technicalName, rowUid, dateValue) {
        this.setProcessPaidVacationValue(
            technicalName,
            rowUid,
            {dateStart: this.serializeDateValue(dateValue, "date")}
        );
    },

    setProcessAdvanceSeverance(technicalName, checked) {
        const nextValues = {
            isAdvanceSeverance: Boolean(checked),
        };
        if (!checked) {
            nextValues.advanceSeveranceValue = "";
        }
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                ...nextValues,
            },
        };
    },

    setProcessAdvanceSeveranceValue(technicalName, value) {
        this.setProcessTestInputValue(technicalName, "advanceSeveranceValue", value);
    },

    getProcessWageChangeDateValue(technicalName, rowUid) {
        const row = this.getProcessWageChanges(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row.date : "");
    },

    onProcessWageChangeDateChange(technicalName, rowUid, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.setProcessWageChangeValue(technicalName, rowUid, {date: serialized});
    },

    getProcessContractConcepts(technicalName) {
        return this.getProcessSectionRows(technicalName, "contractConcepts");
    },

    addProcessContractConcept(technicalName) {
        if (!this.requireProcessPeriodForSection(technicalName)) {
            return;
        }
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "contractConcepts", [
            ...this.getProcessContractConcepts(technicalName),
            {
                uid: this.state.testFieldUid,
                salaryRuleId: false,
                salaryRuleLabel: "",
                amount: "",
                period: false,
                aplicar: false,
                dateStart: "",
                dateEnd: "",
                partnerId: false,
                partnerLabel: "",
            },
        ]);
    },

    removeProcessContractConcept(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "contractConcepts", rowUid);
    },

    setProcessContractConceptValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "contractConcepts", rowUid, values);
    },

    getProcessContractConceptDateValue(technicalName, rowUid, fieldName) {
        const row = this.getProcessContractConcepts(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row[fieldName] : "");
    },

    getProcessContractConceptMinDate(technicalName, rowUid, fieldName) {
        if (fieldName !== "dateEnd") {
            return false;
        }
        return this.getProcessContractConceptDateValue(technicalName, rowUid, "dateStart") || false;
    },

    getProcessContractConceptMaxDate(technicalName, rowUid, fieldName) {
        if (fieldName !== "dateStart") {
            return false;
        }
        return this.getProcessContractConceptDateValue(technicalName, rowUid, "dateEnd") || false;
    },

    onProcessContractConceptDateChange(technicalName, rowUid, fieldName, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const row = this.getProcessContractConcepts(technicalName).find((item) => item.uid === rowUid) || {};
        if (fieldName === "dateStart" && serialized && row.dateEnd && serialized > row.dateEnd) {
            this.setProcessContractConceptValue(technicalName, rowUid, {dateStart: serialized, dateEnd: ""});
            return;
        }
        if (fieldName === "dateEnd" && serialized && row.dateStart && serialized < row.dateStart) {
            return;
        }
        this.setProcessContractConceptValue(technicalName, rowUid, {[fieldName]: serialized});
    },

    setProcessRetentionProcedure(technicalName, value) {
        const nextValue = value || false;
        const current = this.getProcessTestInputState(technicalName);
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...current,
                retentionProcedure: nextValue,
                fixedValueRetentionProcedure: nextValue === "fixed"
                    ? current.fixedValueRetentionProcedure
                    : "",
            },
        };
    },

    setProcessFixedValueRetention(technicalName, value) {
        this.setProcessTestInputValue(technicalName, "fixedValueRetentionProcedure", value);
    },

    getProcessRtfDeductions(technicalName) {
        return this.getProcessSectionRows(technicalName, "rtfDeductions");
    },

    get rtfSalaryRuleDomain() {
        return [["type_concept", "=", "tributaria"]];
    },

    addProcessRtfDeduction(technicalName) {
        this.state.testFieldUid += 1;
        this.updateProcessSectionRows(technicalName, "rtfDeductions", [
            ...this.getProcessRtfDeductions(technicalName),
            {
                uid: this.state.testFieldUid,
                salaryRuleId: false,
                salaryRuleLabel: "",
                dateStart: "",
                dateEnd: "",
                valueTotal: "",
            },
        ]);
    },

    removeProcessRtfDeduction(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "rtfDeductions", rowUid);
    },

    setProcessRtfDeductionValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "rtfDeductions", rowUid, values);
    },

    getProcessRtfDeductionDateValue(technicalName, rowUid, fieldName) {
        const row = this.getProcessRtfDeductions(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row[fieldName] : "");
    },

    getProcessRtfDeductionMinDate(technicalName, rowUid, fieldName) {
        if (fieldName !== "dateEnd") {
            return false;
        }
        return this.getProcessRtfDeductionDateValue(technicalName, rowUid, "dateStart") || false;
    },

    getProcessRtfDeductionMaxDate(technicalName, rowUid, fieldName) {
        if (fieldName !== "dateStart") {
            return false;
        }
        return this.getProcessRtfDeductionDateValue(technicalName, rowUid, "dateEnd") || false;
    },

    onProcessRtfDeductionDateChange(technicalName, rowUid, fieldName, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const row = this.getProcessRtfDeductions(technicalName).find((item) => item.uid === rowUid) || {};
        if (fieldName === "dateStart" && serialized && row.dateEnd && serialized > row.dateEnd) {
            this.setProcessRtfDeductionValue(technicalName, rowUid, {dateStart: serialized, dateEnd: ""});
            return;
        }
        if (fieldName === "dateEnd" && serialized && row.dateStart && serialized < row.dateStart) {
            return;
        }
        this.setProcessRtfDeductionValue(technicalName, rowUid, {[fieldName]: serialized});
    },

    validateProcessNoveltiesBeforeRun(technicalNames) {
        for (const technicalName of technicalNames) {
            const test = this.selectedCatalogTests.find((item) => item.technical_name === technicalName);
            if (this.isAbsencesParametricTest(test)) {
                const absencesInput = this.getProcessTestInputState(technicalName);
                if (!absencesInput.versionId) {
                    return _t("Debe seleccionar un contrato existente en la base de datos.");
                }
                if (!absencesInput.dateStart || !absencesInput.dateEnd) {
                    return _t("Debe indicar Fecha desde y Fecha hasta de la ausencia.");
                }
                continue;
            }
            if (test?.test_type !== "process") {
                continue;
            }
            const inputState = this.getProcessTestInputState(technicalName);
            if (!inputState.versionId) {
                return _t("Debe seleccionar un contrato existente en la base de datos.");
            }
            if (this.isPeriodClosureProcess(test)) {
                if (!inputState.year) {
                    return _t("Debe indicar el año del periodo de cierre.");
                }
                if (!inputState.month) {
                    return _t("Debe indicar el mes del periodo de cierre.");
                }
                continue;
            }
            if (!inputState.dateStart || !inputState.dateEnd) {
                return _t("Debe indicar Fecha desde y Fecha hasta del escenario.");
            }
            if (this.isVacacionesProcess(test)) {
                const hasEnjoyed = this.getProcessEnjoyedVacations(technicalName).length > 0;
                const hasPaid = this.getProcessPaidVacations(technicalName).length > 0;
                if (!hasEnjoyed && !hasPaid) {
                    return _t(
                        "Debe agregar Vacaciones disfrutadas o Vacaciones remuneradas para simular la liquidación."
                    );
                }
            }
            const hasOptionalRows = (
                this.getProcessNovelties(technicalName).length
                || this.getProcessOvertimes(technicalName).length
                || this.getProcessLoans(technicalName).length
                || this.getProcessDifferentConcepts(technicalName).length
                || this.getProcessIndependentNovelties(technicalName).length
                || this.getProcessContractConcepts(technicalName).length
                || this.getProcessWageChanges(technicalName).length
                || this.getProcessEnjoyedVacations(technicalName).length
                || this.getProcessPaidVacations(technicalName).length
            );
            if (hasOptionalRows && !this.hasProcessPeriod(technicalName)) {
                return _t("Defina Fecha desde y Fecha hasta del escenario antes de ejecutar.");
            }
            if (inputState.isAdvanceSeverance) {
                if (
                    inputState.advanceSeveranceValue === ""
                    || inputState.advanceSeveranceValue === null
                    || inputState.advanceSeveranceValue === undefined
                ) {
                    return _t("Debe indicar el valor del anticipo de cesantías.");
                }
            }
            for (let index = 0; index < this.getProcessNovelties(technicalName).length; index++) {
                const novelty = this.getProcessNovelties(technicalName)[index];
                if (!novelty.dateFrom || !novelty.dateTo) {
                    return _t("En la novedad %s, las fechas Desde y Hasta son obligatorias.", index + 1);
                }
            }
            for (let index = 0; index < this.getProcessWageChanges(technicalName).length; index++) {
                const wageChange = this.getProcessWageChanges(technicalName)[index];
                if (!wageChange.date || wageChange.wage === "" || wageChange.wage === null || wageChange.wage === undefined) {
                    return _t(
                        "En el cambio de salario %s, fecha y nuevo salario son obligatorios.",
                        index + 1
                    );
                }
            }
            for (let index = 0; index < this.getProcessEnjoyedVacations(technicalName).length; index++) {
                const row = this.getProcessEnjoyedVacations(technicalName)[index];
                if (!row.dateFrom || !row.dateTo) {
                    return _t(
                        "En vacaciones disfrutadas %s, Desde y Hasta son obligatorios.",
                        index + 1
                    );
                }
            }
            for (let index = 0; index < this.getProcessPaidVacations(technicalName).length; index++) {
                const row = this.getProcessPaidVacations(technicalName)[index];
                if (!row.dateStart || !row.days || Number(row.days) <= 0) {
                    return _t(
                        "En vacaciones remuneradas %s, días y fecha inicial son obligatorios.",
                        index + 1
                    );
                }
            }
            for (let index = 0; index < this.getProcessOvertimes(technicalName).length; index++) {
                const overtime = this.getProcessOvertimes(technicalName)[index];
                if (!overtime.typeOvertimeId || !overtime.hours || !overtime.dateFrom || !overtime.dateTo) {
                    return _t(
                        "En la hora extra %s, tipo, horas, Desde y Hasta son obligatorios.",
                        index + 1
                    );
                }
            }
            for (let index = 0; index < this.getProcessLoans(technicalName).length; index++) {
                const loan = this.getProcessLoans(technicalName)[index];
                if (!loan.salaryRuleId || !loan.entityId || !loan.applyCharge || !loan.amount) {
                    return _t(
                        "En el prestamo %s, regla, entidad, aplicar cobro y valor son obligatorios.",
                        index + 1
                    );
                }
            }
            for (let index = 0; index < this.getProcessDifferentConcepts(technicalName).length; index++) {
                const concept = this.getProcessDifferentConcepts(technicalName)[index];
                if (!concept.salaryRuleId || !concept.date || concept.amount === "" || concept.amount === null || concept.amount === undefined) {
                    return _t(
                        "En el concepto diferente %s, regla, fecha y valor son obligatorios.",
                        index + 1
                    );
                }
            }
            for (let index = 0; index < this.getProcessIndependentNovelties(technicalName).length; index++) {
                const novelty = this.getProcessIndependentNovelties(technicalName)[index];
                if (
                    !novelty.salaryRuleId
                    || !novelty.date
                    || novelty.amount === ""
                    || novelty.amount === null
                    || novelty.amount === undefined
                    || Number(novelty.amount) === 0
                ) {
                    return _t(
                        "En la novedad independiente %s, regla, fecha y valor (distinto de 0) son obligatorios.",
                        index + 1
                    );
                }
            }
            for (let index = 0; index < this.getProcessContractConcepts(technicalName).length; index++) {
                const concept = this.getProcessContractConcepts(technicalName)[index];
                if (
                    !concept.salaryRuleId
                    || concept.amount === ""
                    || concept.amount === null
                    || concept.amount === undefined
                    || !concept.period
                    || !concept.aplicar
                ) {
                    return _t(
                        "En el concepto fijo %s, regla, valor, periodo y aplicar cobro son obligatorios.",
                        index + 1
                    );
                }
                if (concept.period === "limited" && (!concept.dateStart || !concept.dateEnd)) {
                    return _t(
                        "En el concepto fijo %s limitado, Fecha inicial y Fecha final son obligatorias.",
                        index + 1
                    );
                }
            }
            if (inputState.retentionProcedure === "fixed") {
                if (
                    inputState.fixedValueRetentionProcedure === ""
                    || inputState.fixedValueRetentionProcedure === null
                    || inputState.fixedValueRetentionProcedure === undefined
                ) {
                    return _t("Debe indicar Valor fijo retencion cuando el procedimiento es Valor fijo.");
                }
            }
            for (let index = 0; index < this.getProcessRtfDeductions(technicalName).length; index++) {
                const deduction = this.getProcessRtfDeductions(technicalName)[index];
                if (
                    !deduction.salaryRuleId
                    || !deduction.dateStart
                    || !deduction.dateEnd
                    || deduction.valueTotal === ""
                    || deduction.valueTotal === null
                    || deduction.valueTotal === undefined
                ) {
                    return _t(
                        "En la deduccion RTF %s, regla, fechas y valor total son obligatorios.",
                        index + 1
                    );
                }
            }
        }
        return false;
    },

    buildTestParamsForRun(technicalName) {
        const test = this.selectedCatalogTests.find((item) => item.technical_name === technicalName);
        const inputState = this.state.testInputs[technicalName] || this.getDefaultTestInputState(test);
        const params = {};
        const displayLines = [];
        if (this.isAbsencesParametricTest(test)) {
            if (inputState.versionId) {
                params.version_id = inputState.versionId;
                displayLines.push({
                    label: "Contrato",
                    value: inputState.versionLabel || String(inputState.versionId),
                });
            }
            if (inputState.leaveTypeId) {
                params.leave_type_id = inputState.leaveTypeId;
                displayLines.push({
                    label: "Tipo de entrada",
                    value: inputState.leaveTypeLabel || String(inputState.leaveTypeId),
                });
            }
            if (inputState.dateStart) {
                params.date_from = inputState.dateStart;
                displayLines.push({
                    label: "Fecha desde",
                    value: String(inputState.dateStart),
                });
            }
            if (inputState.dateEnd) {
                params.date_to = inputState.dateEnd;
                displayLines.push({
                    label: "Fecha hasta",
                    value: String(inputState.dateEnd),
                });
            }
            const destinationState = inputState.destinationState || this.getAbsencesDefaultDestinationState(test);
            params.destination_state = destinationState;
            const destinationLabel = (this.absencesDestinationStateChoices || []).find(
                (item) => item.value === destinationState
            )?.label || destinationState;
            displayLines.push({label: "Estado destino", value: destinationLabel});
            return {params, displayLines};
        }
        if (test?.test_type === "process") {
            if (inputState.versionId) {
                params.version_id = inputState.versionId;
                displayLines.push({
                    label: "Contrato",
                    value: inputState.versionLabel || String(inputState.versionId),
                });
            }
            if (this.isPeriodClosureProcess(test)) {
                if (inputState.year) {
                    params.year = Number(inputState.year);
                    displayLines.push({label: "Año", value: String(inputState.year)});
                }
                if (inputState.month) {
                    params.month = String(inputState.month);
                    const monthLabel = (this.socialSecurityMonthChoices || []).find(
                        (item) => String(item.value) === String(inputState.month)
                    )?.label || inputState.month;
                    displayLines.push({label: "Mes", value: monthLabel});
                }
                if (inputState.generateAccounting) {
                    params.generate_accounting = true;
                    displayLines.push({label: "Generar contabilización", value: "Sí"});
                }
            }
            if (inputState.dateStart) {
                params.date_start = inputState.dateStart;
                displayLines.push({
                    label: "Fecha desde",
                    value: String(inputState.dateStart),
                });
            }
            if (inputState.dateEnd) {
                params.date_end = inputState.dateEnd;
                displayLines.push({label: "Fecha hasta", value: String(inputState.dateEnd)});
            }
            if (this.isContractLiquidationProcess(test)) {
                const dateLiquidacion = inputState.dateLiquidacion || inputState.dateEnd;
                if (dateLiquidacion) {
                    params.date_liquidacion = dateLiquidacion;
                    displayLines.push({
                        label: "Fecha de liquidación",
                        value: String(dateLiquidacion),
                    });
                }
                if (inputState.datePrima) {
                    displayLines.push({
                        label: "Fecha causación prima",
                        value: String(inputState.datePrima),
                    });
                }
                if (inputState.dateCesantias) {
                    displayLines.push({
                        label: "Fecha causación cesantías",
                        value: String(inputState.dateCesantias),
                    });
                }
                if (inputState.dateVacaciones) {
                    displayLines.push({
                        label: "Fecha causación vacaciones",
                        value: String(inputState.dateVacaciones),
                    });
                }
                if (inputState.haveCompensation) {
                    params.have_compensation = true;
                    displayLines.push({label: "Indemnización", value: "Sí"});
                }
                if (inputState.reasonRetiroId) {
                    params.reason_retiro_id = inputState.reasonRetiroId;
                    displayLines.push({
                        label: "Motivo de retiro",
                        value: inputState.reasonRetiroLabel || String(inputState.reasonRetiroId),
                    });
                }
            }
            if (this.isCesantiasProcess(test) && inputState.isAdvanceSeverance) {
                params.z_is_advance_severance = true;
                displayLines.push({label: "Anticipo de cesantías", value: "Sí"});
                if (
                    inputState.advanceSeveranceValue !== ""
                    && inputState.advanceSeveranceValue !== null
                    && inputState.advanceSeveranceValue !== undefined
                ) {
                    params.z_value_advance_severance = Number(inputState.advanceSeveranceValue);
                    displayLines.push({
                        label: "Valor del anticipo",
                        value: this.formatMonetaryValue(inputState.advanceSeveranceValue),
                    });
                }
            }
            if (inputState.retentionProcedure) {
                params.retention_procedure = inputState.retentionProcedure;
                const retentionLabel = (this.retentionProcedureChoices || []).find(
                    (item) => item.value === inputState.retentionProcedure
                )?.label || inputState.retentionProcedure;
                displayLines.push({label: "Procedimiento RTF", value: retentionLabel});
            }
            if (
                inputState.retentionProcedure === "fixed"
                && inputState.fixedValueRetentionProcedure !== ""
                && inputState.fixedValueRetentionProcedure !== null
                && inputState.fixedValueRetentionProcedure !== undefined
            ) {
                params.fixed_value_retention_procedure = Number(inputState.fixedValueRetentionProcedure);
                displayLines.push({
                    label: "Valor fijo RTF",
                    value: this.formatMonetaryValue(inputState.fixedValueRetentionProcedure),
                });
            }
            const rtfDeductionRows = (inputState.rtfDeductions || []).filter(
                (item) => (
                    item.salaryRuleId
                    && item.dateStart
                    && item.dateEnd
                    && item.valueTotal !== ""
                    && item.valueTotal !== null
                    && item.valueTotal !== undefined
                )
            );
            if (rtfDeductionRows.length) {
                params.test_deductions_rtf = rtfDeductionRows.map((item) => ({
                    salary_rule_id: item.salaryRuleId,
                    date_start: item.dateStart,
                    date_end: item.dateEnd,
                    value_total: Number(item.valueTotal),
                }));
                rtfDeductionRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Deducción RTF ${index + 1}`,
                        value: `${item.salaryRuleLabel || item.salaryRuleId} | ${this.formatMonetaryValue(item.valueTotal)} | ${item.dateStart} - ${item.dateEnd}`,
                    });
                });
            }
            const noveltyRows = (inputState.novelties || []).filter(
                (item) => item.workEntryTypeId && item.dateFrom && item.dateTo
            );
            if (noveltyRows.length) {
                params.test_novelties = noveltyRows.map((item) => ({
                    work_entry_type_id: item.workEntryTypeId,
                    date_from: item.dateFrom,
                    date_to: item.dateTo,
                }));
                noveltyRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Novedad ${index + 1}`,
                        value: `${item.workEntryTypeLabel || item.workEntryTypeId} | ${item.dateFrom} - ${item.dateTo}`,
                    });
                });
            }
            const enjoyedVacationRows = (inputState.enjoyedVacations || []).filter(
                (item) => item.dateFrom && item.dateTo
            );
            if (enjoyedVacationRows.length) {
                params.test_enjoyed_vacations = enjoyedVacationRows.map((item) => ({
                    date_from: item.dateFrom,
                    date_to: item.dateTo,
                }));
                enjoyedVacationRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Vacación disfrutada ${index + 1}`,
                        value: `${item.dateFrom} - ${item.dateTo}`,
                    });
                });
            }
            const paidVacationRows = (inputState.paidVacations || []).filter(
                (item) => item.dateStart && item.days && Number(item.days) > 0
            );
            if (paidVacationRows.length) {
                params.test_paid_vacations = paidVacationRows.map((item) => ({
                    paid_vacation_days: Number(item.days),
                    start_date_paid_vacation: item.dateStart,
                }));
                paidVacationRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Vacación remunerada ${index + 1}`,
                        value: `${item.days} días | ${item.dateStart}`,
                    });
                });
            }
            const wageChangeRows = (inputState.wageChanges || []).filter(
                (item) => (
                    item.date
                    && item.wage !== ""
                    && item.wage !== null
                    && item.wage !== undefined
                )
            );
            if (wageChangeRows.length) {
                params.test_wage_changes = wageChangeRows.map((item) => ({
                    date: item.date,
                    wage: Number(item.wage),
                }));
                wageChangeRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Cambio de salario ${index + 1}`,
                        value: `${item.date} | actual ${this.formatMonetaryValue(item.currentWage)} → nuevo ${this.formatMonetaryValue(item.wage)}`,
                    });
                });
            }
            const overtimeRows = (inputState.overtimes || []).filter(
                (item) => item.typeOvertimeId && item.hours && item.dateFrom && item.dateTo
            );
            if (overtimeRows.length) {
                params.test_overtimes = overtimeRows.map((item) => ({
                    type_overtime_id: item.typeOvertimeId,
                    hours: Number(item.hours),
                    date_from: item.dateFrom,
                    date_to: item.dateTo,
                }));
                overtimeRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Hora extra ${index + 1}`,
                        value: `${item.typeOvertimeLabel || item.typeOvertimeId} | ${item.hours} h | ${item.dateFrom} - ${item.dateTo}`,
                    });
                });
            }
            const loanRows = (inputState.loans || []).filter(
                (item) => item.salaryRuleId && item.entityId && item.applyCharge && item.amount
            );
            if (loanRows.length) {
                params.test_loans = loanRows.map((item) => ({
                    salary_rule_id: item.salaryRuleId,
                    entity_id: item.entityId,
                    apply_charge: item.applyCharge,
                    amount: Number(item.amount),
                    final_settlement: Boolean(item.finalSettlement),
                }));
                loanRows.forEach((item, index) => {
                    const settlementLabel = item.finalSettlement ? " | finiquito saldo total" : "";
                    displayLines.push({
                        label: `Prestamo ${index + 1}`,
                        value: `${item.salaryRuleLabel || item.salaryRuleId} | ${this.formatMonetaryValue(item.amount)} | cobro ${item.applyCharge}${settlementLabel}`,
                    });
                });
            }
            const conceptRows = (inputState.differentConcepts || []).filter(
                (item) => item.salaryRuleId && item.date && item.amount !== "" && item.amount !== null && item.amount !== undefined
            );
            if (conceptRows.length) {
                params.test_different_concepts = conceptRows.map((item) => ({
                    salary_rule_id: item.salaryRuleId,
                    date: item.date,
                    amount: Number(item.amount),
                    description: item.description || "",
                    partner_id: item.partnerId || false,
                }));
                conceptRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Concepto diferente ${index + 1}`,
                        value: `${item.salaryRuleLabel || item.salaryRuleId} | ${this.formatMonetaryValue(item.amount)} | ${item.date}`,
                    });
                });
            }
            const independentNoveltyRows = (inputState.independentNovelties || []).filter(
                (item) => (
                    item.salaryRuleId
                    && item.date
                    && item.amount !== ""
                    && item.amount !== null
                    && item.amount !== undefined
                    && Number(item.amount) !== 0
                )
            );
            if (independentNoveltyRows.length) {
                params.test_independent_novelties = independentNoveltyRows.map((item) => ({
                    salary_rule_id: item.salaryRuleId,
                    date: item.date,
                    amount: Number(item.amount),
                    description: item.description || "",
                }));
                independentNoveltyRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Novedad independiente ${index + 1}`,
                        value: `${item.salaryRuleLabel || item.salaryRuleId} | ${this.formatMonetaryValue(item.amount)} | ${item.date}`,
                    });
                });
            }
            const contractConceptRows = (inputState.contractConcepts || []).filter(
                (item) => (
                    item.salaryRuleId
                    && item.amount !== ""
                    && item.amount !== null
                    && item.amount !== undefined
                    && item.period
                    && item.aplicar
                )
            );
            if (contractConceptRows.length) {
                params.test_contract_concepts = contractConceptRows.map((item) => ({
                    salary_rule_id: item.salaryRuleId,
                    amount: Number(item.amount),
                    period: item.period,
                    aplicar: item.aplicar,
                    date_start: item.dateStart || false,
                    date_end: item.dateEnd || false,
                    partner_id: item.partnerId || false,
                }));
                contractConceptRows.forEach((item, index) => {
                    displayLines.push({
                        label: `Concepto fijo ${index + 1}`,
                        value: `${item.salaryRuleLabel || item.salaryRuleId} | ${this.formatMonetaryValue(item.amount)} | cobro ${item.aplicar}`,
                    });
                });
            }
            return {params, displayLines};
        }
        for (const row of inputState.fieldRows || []) {
            if (row.value === null || row.value === undefined || row.value === "") {
                continue;
            }
            params[row.name] = row.value;
            displayLines.push({
                label: row.label || row.name,
                value: this.formatTestFieldDisplayValue(row),
            });
        }
        return {params, displayLines};
    },

});
