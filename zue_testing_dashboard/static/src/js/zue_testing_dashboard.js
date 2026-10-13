import { Component, onWillStart, useState } from "@odoo/owl";
import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { formatCurrency } from "@web/core/currency";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { deserializeDate, deserializeDateTime, serializeDate, serializeDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { SelectMenu } from "@web/core/select_menu/select_menu";
import { user } from "@web/core/user";
import { useOwnedDialogs, useService } from "@web/core/utils/hooks";
import { formatFloat } from "@web/core/utils/numbers";
import { parseMonetary } from "@web/views/fields/parsers";
import { ZueProcessResultViewer } from "@zue_testing_dashboard/js/process_result_viewer";

const VERSION_SEARCH_LIMIT = 7;
const VERSION_SEARCH_MORE_LIMIT = 320;

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

export class ZueDashboardRecordMany2One extends Component {
    static template = "zue_testing_dashboard.RecordMany2One";
    static components = { AutoComplete };
    static props = {
        value: { type: [Number, String, { value: false }, { value: "" }], optional: true },
        displayName: { type: String, optional: true },
        update: Function,
        modelName: String,
        dialogTitle: { type: String, optional: true },
        disabled: { type: Boolean, optional: true },
        placeholder: { type: String, optional: true },
        domain: { type: Array, optional: true },
    };
    static defaultProps = {
        value: false,
        displayName: "",
        dialogTitle: "",
        disabled: false,
        placeholder: "",
        domain: [],
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

    get searchDomain() {
        return this.props.domain || [];
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
            "searchDashboardRecords",
            [this.props.modelName, name || "", VERSION_SEARCH_LIMIT + 1],
            {domain: this.searchDomain}
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
                "searchDashboardRecords",
                [this.props.modelName, name, VERSION_SEARCH_MORE_LIMIT],
                {domain: this.searchDomain}
            );
            const ids = (matches || []).map((item) => item.value);
            dynamicFilters = [{
                description: _t("Quick search: %s", name),
                domain: [["id", "in", ids]],
            }];
        }
        const SelectCreateDialog = registry.category("dialogs").get("select_create");
        this.addDialog(SelectCreateDialog, {
            title: this.props.dialogTitle || _t("Search"),
            resModel: this.props.modelName,
            noCreate: true,
            multiSelect: false,
            domain: this.searchDomain,
            dynamicFilters,
            context: {},
            onSelected: async (resId) => {
                const recordId = Array.isArray(resId) ? resId[0] : resId;
                await this.selectRecordById(recordId);
            },
        });
    }

    async selectRecordById(recordId) {
        if (!recordId) {
            this.props.update(false, "");
            return;
        }
        const records = await this.orm.read(this.props.modelName, [recordId], ["display_name"]);
        const record = (records || [])[0];
        this.props.update(recordId, record ? record.display_name : String(recordId));
    }

    onChange({ inputValue }) {
        if (!inputValue.length) {
            this.props.update(false, "");
        }
    }
}

export class ZueTestingDashboard extends Component {
    static template = "zue_testing_dashboard.ZueTestingDashboard";
    static components = {
        DateTimeInput,
        SelectMenu,
        ZueDashboardVersionMany2One,
        ZueDashboardRecordMany2One,
        ZueProcessResultViewer,
    };

    setup() {
        // Inicializa servicios OWL y el estado reactivo de la pantalla.
        this.orm = useService("orm");
        this.notification = useService("notification");
        // Listas y fechas memorizadas para no recrear props en cada render de los componentes Odoo.
        this.booleanFieldChoices = [
            {value: "true", label: "Si"},
            {value: "false", label: "No"},
        ];
        this.parsedDateCache = {};
        this.state = useState({
            moduleKey: false,
            scope: false,
            providerModel: false,
            sessionId: false,
            running: false,
            stopRequested: false,
            currentIndex: 0,
            totalToRun: 0,
            specs: [],
            lines: [],
            modules: [],
            notes: [],
            statusLegends: [],
            selectedTests: {},
            testInputs: {},
            groupSharedConfig: {
                versionId: false,
                versionLabel: "",
                dateStart: "",
                dateEnd: "",
                year: "",
                month: false,
            },
            testModelFieldsCache: {},
            testFieldPicker: {technicalName: false, search: ""},
            testFieldUid: 0,
            loanApplyChargeChoices: [],
            contractConceptAplicarChoices: [],
            contractConceptPeriodChoices: [],
            retentionProcedureChoices: [],
            monetaryInputFocusKey: false,
            testsDrawerOpen: false,
            infoDrawerOpen: false,
            counts: {total: 0, ok: 0, failed: 0, controlled: 0, skipped: 0},
            statusFilters: {total: true, ok: false, controlled: false, failed: false},
            testTypeFilters: {parametric: false, process: false},
            error: false,
        });

        onWillStart(async () => {
            await this.loadAdapterData();
            await this.loadProcessFormOptions();
        });
    }

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
    }

    get loanApplyChargeChoices() {
        return this.state.loanApplyChargeChoices || [];
    }

    get contractConceptAplicarChoices() {
        return this.state.contractConceptAplicarChoices || [];
    }

    get contractConceptPeriodChoices() {
        return this.state.contractConceptPeriodChoices || [];
    }

    get retentionProcedureChoices() {
        return this.state.retentionProcedureChoices || [];
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

    parseMonetaryInputValue(rawValue) {
        if (rawValue === null || rawValue === undefined) {
            return "";
        }
        const text = String(rawValue).trim();
        if (!text) {
            return "";
        }
        try {
            return parseMonetary(text);
        } catch (_error) {
            return "";
        }
    }

    getMonetaryInputDisplay(focusKey, value) {
        if (this.state.monetaryInputFocusKey === focusKey) {
            if (value === null || value === undefined || value === false || value === "") {
                return "";
            }
            return String(value);
        }
        return this.formatMonetaryValue(value);
    }

    onMonetaryInputFocus(focusKey) {
        this.state.monetaryInputFocusKey = focusKey;
    }

    onMonetaryInputBlur(focusKey, event, applyValue) {
        const parsed = this.parseMonetaryInputValue(event.target.value);
        applyValue(parsed);
        if (this.state.monetaryInputFocusKey === focusKey) {
            this.state.monetaryInputFocusKey = false;
        }
    }

    formatMonetaryDisplayOrDash(value) {
        if (value === null || value === undefined || value === false || value === "") {
            return "-";
        }
        return this.formatMonetaryValue(value) || "-";
    }

    get progressPercent() {
        // Calcula el porcentaje mostrado en la barra de progreso.
        if (!this.state.totalToRun) {
            return 0;
        }
        return Math.round((this.state.currentIndex / this.state.totalToRun) * 100);
    }

    get progressStyle() {
        // Devuelve el estilo inline que OWL usa para pintar la barra.
        return `width: ${this.progressPercent}%`;
    }

    get filteredLines() {
        const filters = this.state.statusFilters || {};
        const typeFilters = this.state.testTypeFilters || {};
        let lines = this.state.lines || [];
        if (filters.total) {
            return lines;
        }
        const activeStatuses = ["ok", "controlled", "failed"].filter((status) => filters[status]);
        const activeTypes = ["parametric", "process"].filter((testType) => typeFilters[testType]);
        if (activeStatuses.length) {
            lines = lines.filter((line) => activeStatuses.includes(line.status));
        }
        if (activeTypes.length) {
            lines = lines.filter((line) => activeTypes.includes(line.test_type));
        }
        return lines;
    }

    get testTypeCounts() {
        const lines = this.state.lines || [];
        return {
            parametric: lines.filter((line) => line.test_type === "parametric").length,
            process: lines.filter((line) => line.test_type === "process").length,
        };
    }

    get selectedModule() {
        // Obtiene el modulo funcional seleccionado en el primer combo.
        return this.state.modules.find((module) => module.key === this.state.moduleKey) || false;
    }

    get moduleGroups() {
        return this.selectedModule?.groups || [];
    }

    get selectedProvider() {
        // Obtiene el provider actualmente seleccionado en el segundo combo.
        return this.moduleGroups.find((group) => group.model === this.state.providerModel) || false;
    }

    get isSocialBenefitsProvider() {
        return this.state.providerModel === "zue.testing.dashboard.hr.liq.benefits.provider";
    }

    get isGeneralLiquidationProvider() {
        return this.state.providerModel === "zue.testing.dashboard.hr.liq.general.provider";
    }

    get isPeriodClosureProvider() {
        return this.state.providerModel === "zue.testing.dashboard.hr.social.security.provider";
    }

    get showGroupSharedConfig() {
        return (
            (this.isSocialBenefitsProvider || this.isGeneralLiquidationProvider || this.isPeriodClosureProvider)
            && this.state.scope === "all"
            && this.selectedCatalogTests.length > 0
        );
    }

    get isPeriodClosureSharedConfig() {
        return this.isPeriodClosureProvider;
    }

    get groupSharedConfig() {
        return this.state.groupSharedConfig;
    }

    getGroupSharedDateValue(fieldName) {
        return this.toDateTimeValue(this.groupSharedConfig[fieldName]);
    }

    setGroupSharedVersion(versionId, versionLabel) {
        this.state.groupSharedConfig = {
            ...this.groupSharedConfig,
            versionId: versionId || false,
            versionLabel: versionLabel || "",
        };
    }

    setGroupSharedDate(fieldName, dateValue) {
        this.state.groupSharedConfig = {
            ...this.groupSharedConfig,
            [fieldName]: this.serializeDateValue(dateValue, "date"),
        };
    }

    setGroupSharedValue(fieldName, value) {
        this.state.groupSharedConfig = {
            ...this.groupSharedConfig,
            [fieldName]: value,
        };
    }

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
    }

    get emptyGroupSharedConfig() {
        return {
            versionId: false,
            versionLabel: "",
            dateStart: "",
            dateEnd: "",
            year: "",
            month: false,
        };
    }

    get availableScopes() {
        // Devuelve los filtros publicados por el provider seleccionado.
        if (!this.selectedProvider) {
            return [];
        }
        return this.selectedProvider.scopes || [];
    }

    get moduleChoices() {
        return this.state.modules.map((module) => ({value: module.key, label: module.name}));
    }

    get providerChoices() {
        return [];
    }

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
    }

    get scopeChoices() {
        return this.availableScopes.map((scope) => ({
            value: scope.value,
            label: scope.count === undefined ? scope.label : `${scope.label} (${scope.count})`,
        }));
    }

    get selectedCatalogTests() {
        // Lista solo las pruebas que pertenecen al filtro visual activo.
        if (!this.selectedProvider) {
            return [];
        }
        const specs = this.selectedProvider.specs || [];
        if (!this.state.scope || this.state.scope === "all") {
            return specs;
        }
        return specs.filter((spec) => (spec.tags || []).includes(this.state.scope));
    }

    get selectedTestsCount() {
        return this.selectedCatalogTests.filter((test) => this.isTestSelected(test.technical_name)).length;
    }

    get allCatalogTestsSelected() {
        const tests = this.selectedCatalogTests;
        return tests.length > 0 && tests.every((test) => this.isTestSelected(test.technical_name));
    }

    get catalogGroups() {
        if (!this.selectedProvider) {
            return [];
        }
        const tests = this.selectedCatalogTests;
        if (!tests.length) {
            return [];
        }
        const scopeOptions = (this.selectedProvider.scopes || []).filter(
            (scope) => scope.value !== "all"
        );
        if (this.state.scope && this.state.scope !== "all") {
            const activeScope = scopeOptions.find((scope) => scope.value === this.state.scope);
            return [{
                tag: this.state.scope,
                label: activeScope?.label || this.state.scope,
                count: tests.length,
                tests,
            }];
        }
        const groups = [];
        for (const scope of scopeOptions) {
            const groupTests = tests.filter((test) => (test.tags || []).includes(scope.value));
            if (!groupTests.length) {
                continue;
            }
            groups.push({
                tag: scope.value,
                label: scope.label,
                count: groupTests.length,
                tests: groupTests,
            });
        }
        return groups;
    }

    get canRun() {
        const hasScope = this.state.scope !== false && this.state.scope !== null && this.state.scope !== "";
        return (
            !this.state.running
            && Boolean(this.state.moduleKey)
            && Boolean(this.state.providerModel)
            && hasScope
            && this.selectedTestsCount > 0
        );
    }

    getRpcErrorMessage(error) {
        if (error?.data?.message) {
            return error.data.message;
        }
        if (error?.data?.debug) {
            return error.data.debug.split("\n")[0];
        }
        return error?.message || String(error);
    }

    isTestSelected(technicalName) {
        if (Object.prototype.hasOwnProperty.call(this.state.selectedTests, technicalName)) {
            return Boolean(this.state.selectedTests[technicalName]);
        }
        return true;
    }

    syncSelectedTests() {
        const nextSelection = {};
        for (const test of this.selectedCatalogTests) {
            nextSelection[test.technical_name] = this.isTestSelected(test.technical_name);
        }
        this.state.selectedTests = nextSelection;
        this.syncTestInputs();
    }

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
    }

    isPeriodicPayrollProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_periodic_payroll";
    }

    isContractLiquidationProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_liquidacion_contrato";
    }

    isIndependentPayrollProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_nomina_independiente";
    }

    isSocialSecurityProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_seguridad_social";
    }

    isProvisionsProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_provisiones";
    }

    isPeriodClosureProcess(testOrName) {
        return this.isSocialSecurityProcess(testOrName) || this.isProvisionsProcess(testOrName);
    }

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
    }

    isPrimaProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_prima";
    }

    isCesantiasProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return (
            name === "test_simulate_cesantias"
            || name === "test_simulate_intereses_cesantias"
        );
    }

    isVacacionesProcess(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return name === "test_simulate_vacaciones";
    }

    isAbsencesParametricTest(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        return typeof name === "string" && name.startsWith("test_create_leave");
    }

    getAbsencesDefaultDestinationState(testOrName) {
        const name = typeof testOrName === "string" ? testOrName : testOrName?.technical_name;
        if (name === "test_create_leave_draft") {
            return "draft";
        }
        if (name === "test_create_leave_validate_real") {
            return "real";
        }
        return "forced";
    }

    get absencesDestinationStateChoices() {
        return [
            {value: "draft", label: "Borrador"},
            {value: "real", label: "Validada (flujo real)"},
            {value: "forced", label: "Validada (forzada)"},
        ];
    }

    get absencesLeaveTypeDomain() {
        return [["code", "!=", false]];
    }

    setAbsencesLeaveTypeSelection(technicalName, leaveTypeId, leaveTypeLabel) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                leaveTypeId: leaveTypeId || false,
                leaveTypeLabel: leaveTypeLabel || "",
            },
        };
    }

    isWageChangeProcess(testOrName) {
        return this.isPrimaProcess(testOrName) || this.isCesantiasProcess(testOrName);
    }

    syncTestInputs() {
        const nextInputs = {...this.state.testInputs};
        for (const test of this.selectedCatalogTests) {
            if (test.test_type === "process" || test.test_model || this.isAbsencesParametricTest(test)) {
                if (!nextInputs[test.technical_name]) {
                    nextInputs[test.technical_name] = this.getDefaultTestInputState(test);
                }
            }
        }
        this.state.testInputs = nextInputs;
    }

    getProcessTestInputState(technicalName) {
        const test = this.selectedCatalogTests.find((item) => item.technical_name === technicalName);
        return this.state.testInputs[technicalName] || this.getDefaultTestInputState(test);
    }

    setProcessTestInputValue(technicalName, fieldName, value) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                [fieldName]: value,
            },
        };
    }

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
    }

    setProcessReasonRetiroSelection(technicalName, reasonId, reasonLabel) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                reasonRetiroId: reasonId || false,
                reasonRetiroLabel: reasonLabel || "",
            },
        };
    }

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
    }

    toDateTimeValue(serializedValue) {
        // Reutiliza la misma instancia para que los props de DateTimeInput sean estables.
        if (!serializedValue) {
            return false;
        }
        if (!(serializedValue in this.parsedDateCache)) {
            const parsed = serializedValue.length > 10
                ? deserializeDateTime(serializedValue)
                : deserializeDate(serializedValue);
            this.parsedDateCache[serializedValue] = parsed && parsed.isValid ? parsed : false;
        }
        return this.parsedDateCache[serializedValue];
    }

    serializeDateValue(dateValue, fieldType) {
        if (!dateValue || !dateValue.isValid) {
            return "";
        }
        return fieldType === "datetime" ? serializeDateTime(dateValue) : serializeDate(dateValue);
    }

    getProcessDateValue(technicalName, fieldName) {
        return this.toDateTimeValue(this.getProcessTestInputState(technicalName)[fieldName]);
    }

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
    }

    hasProcessPeriod(technicalName) {
        const inputState = this.getProcessTestInputState(technicalName);
        return Boolean(inputState.dateStart && inputState.dateEnd);
    }

    getProcessPeriodMinDate(technicalName) {
        return this.getProcessDateValue(technicalName, "dateStart") || false;
    }

    getProcessPeriodMaxDate(technicalName) {
        return this.getProcessDateValue(technicalName, "dateEnd") || false;
    }

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
    }

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
    }

    getProcessRowRangeMinDate(technicalName, dateFromSerialized) {
        const periodMin = this.getProcessPeriodMinDate(technicalName);
        const dateFrom = this.toDateTimeValue(dateFromSerialized);
        if (dateFrom && dateFrom.isValid && periodMin && dateFrom > periodMin) {
            return dateFrom;
        }
        return periodMin || false;
    }

    getProcessRowRangeMaxDate(technicalName, dateToSerialized) {
        const periodMax = this.getProcessPeriodMaxDate(technicalName);
        const dateTo = this.toDateTimeValue(dateToSerialized);
        if (dateTo && dateTo.isValid && periodMax && dateTo < periodMax) {
            return dateTo;
        }
        return periodMax || false;
    }

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
    }

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
    }

    getProcessNovelties(technicalName) {
        return this.getProcessTestInputState(technicalName).novelties || [];
    }

    createProcessNoveltyRow() {
        this.state.testFieldUid += 1;
        return {
            uid: this.state.testFieldUid,
            workEntryTypeId: false,
            workEntryTypeLabel: "",
            dateFrom: "",
            dateTo: "",
        };
    }

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
    }

    removeProcessNovelty(technicalName, noveltyUid) {
        const current = this.getProcessTestInputState(technicalName);
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...current,
                novelties: (current.novelties || []).filter((item) => item.uid !== noveltyUid),
            },
        };
    }

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
    }

    setProcessNoveltyWorkEntryType(technicalName, noveltyUid, workEntryTypeId, workEntryTypeLabel) {
        this.updateProcessNovelty(technicalName, noveltyUid, {
            workEntryTypeId: workEntryTypeId || false,
            workEntryTypeLabel: workEntryTypeLabel || "",
        });
    }

    getProcessNoveltyDateValue(technicalName, noveltyUid, fieldName) {
        const novelty = this.getProcessNovelties(technicalName).find((item) => item.uid === noveltyUid);
        return this.toDateTimeValue(novelty ? novelty[fieldName] : "");
    }

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
    }

    getProcessSectionRows(technicalName, sectionKey) {
        return this.getProcessTestInputState(technicalName)[sectionKey] || [];
    }

    updateProcessSectionRows(technicalName, sectionKey, rows) {
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...this.getProcessTestInputState(technicalName),
                [sectionKey]: rows,
            },
        };
    }

    updateProcessSectionRow(technicalName, sectionKey, rowUid, values) {
        const rows = this.getProcessSectionRows(technicalName, sectionKey).map((item) => (
            item.uid === rowUid ? {...item, ...values} : item
        ));
        this.updateProcessSectionRows(technicalName, sectionKey, rows);
    }

    removeProcessSectionRow(technicalName, sectionKey, rowUid) {
        this.updateProcessSectionRows(
            technicalName,
            sectionKey,
            this.getProcessSectionRows(technicalName, sectionKey).filter((item) => item.uid !== rowUid)
        );
    }

    requireProcessPeriodForSection(technicalName) {
        if (!this.hasProcessPeriod(technicalName)) {
            this.notification.add(
                _t("Defina primero Fecha desde y Fecha hasta del escenario."),
                {type: "warning"}
            );
            return false;
        }
        return true;
    }

    getProcessOvertimes(technicalName) {
        return this.getProcessSectionRows(technicalName, "overtimes");
    }

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
    }

    removeProcessOvertime(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "overtimes", rowUid);
    }

    setProcessOvertimeValue(technicalName, rowUid, fieldName, value) {
        this.updateProcessSectionRow(technicalName, "overtimes", rowUid, {[fieldName]: value});
    }

    setProcessOvertimeType(technicalName, rowUid, typeOvertimeId, typeOvertimeLabel) {
        this.updateProcessSectionRow(technicalName, "overtimes", rowUid, {
            typeOvertimeId: typeOvertimeId || false,
            typeOvertimeLabel: typeOvertimeLabel || "",
        });
    }

    getProcessOvertimeDateValue(technicalName, rowUid, fieldName) {
        const row = this.getProcessOvertimes(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row[fieldName] : "");
    }

    onProcessOvertimeDateChange(technicalName, rowUid, fieldName, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.setProcessOvertimeValue(technicalName, rowUid, fieldName, serialized);
    }

    getProcessLoans(technicalName) {
        return this.getProcessSectionRows(technicalName, "loans");
    }

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
    }

    removeProcessLoan(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "loans", rowUid);
    }

    setProcessLoanValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "loans", rowUid, values);
    }

    getProcessDifferentConcepts(technicalName) {
        return this.getProcessSectionRows(technicalName, "differentConcepts");
    }

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
    }

    removeProcessDifferentConcept(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "differentConcepts", rowUid);
    }

    setProcessDifferentConceptValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "differentConcepts", rowUid, values);
    }

    getProcessDifferentConceptDateValue(technicalName, rowUid) {
        const row = this.getProcessDifferentConcepts(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row.date : "");
    }

    onProcessDifferentConceptDateChange(technicalName, rowUid, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.setProcessDifferentConceptValue(technicalName, rowUid, {date: serialized});
    }

    getProcessIndependentNovelties(technicalName) {
        return this.getProcessSectionRows(technicalName, "independentNovelties");
    }

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
    }

    removeProcessIndependentNovelty(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "independentNovelties", rowUid);
    }

    setProcessIndependentNoveltyValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "independentNovelties", rowUid, values);
    }

    getProcessIndependentNoveltyDateValue(technicalName, rowUid) {
        const row = this.getProcessIndependentNovelties(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row.date : "");
    }

    onProcessIndependentNoveltyDateChange(technicalName, rowUid, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.setProcessIndependentNoveltyValue(technicalName, rowUid, {date: serialized});
    }

    getProcessWageChanges(technicalName) {
        return this.getProcessSectionRows(technicalName, "wageChanges");
    }

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
    }

    removeProcessWageChange(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "wageChanges", rowUid);
    }

    setProcessWageChangeValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "wageChanges", rowUid, values);
    }

    getProcessEnjoyedVacations(technicalName) {
        return this.getProcessSectionRows(technicalName, "enjoyedVacations");
    }

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
    }

    removeProcessEnjoyedVacation(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "enjoyedVacations", rowUid);
    }

    setProcessEnjoyedVacationValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "enjoyedVacations", rowUid, values);
    }

    getProcessEnjoyedVacationDateValue(technicalName, rowUid, fieldName) {
        const row = this.getProcessEnjoyedVacations(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row?.[fieldName === "dateFrom" ? "dateFrom" : "dateTo"]);
    }

    onProcessEnjoyedVacationDateChange(technicalName, rowUid, fieldName, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const key = fieldName === "dateFrom" ? "dateFrom" : "dateTo";
        this.setProcessEnjoyedVacationValue(technicalName, rowUid, {[key]: serialized});
    }

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
    }

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
    }

    getProcessPaidVacations(technicalName) {
        return this.getProcessSectionRows(technicalName, "paidVacations");
    }

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
    }

    removeProcessPaidVacation(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "paidVacations", rowUid);
    }

    setProcessPaidVacationValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "paidVacations", rowUid, values);
    }

    getProcessPaidVacationDateValue(technicalName, rowUid) {
        const row = this.getProcessPaidVacations(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row?.dateStart);
    }

    onProcessPaidVacationDateChange(technicalName, rowUid, dateValue) {
        this.setProcessPaidVacationValue(
            technicalName,
            rowUid,
            {dateStart: this.serializeDateValue(dateValue, "date")}
        );
    }

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
    }

    setProcessAdvanceSeveranceValue(technicalName, value) {
        this.setProcessTestInputValue(technicalName, "advanceSeveranceValue", value);
    }

    getProcessWageChangeDateValue(technicalName, rowUid) {
        const row = this.getProcessWageChanges(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row.date : "");
    }

    onProcessWageChangeDateChange(technicalName, rowUid, dateValue) {
        const serialized = this.serializeDateValue(dateValue, "date");
        const periodStart = this.getProcessTestInputState(technicalName).dateStart || "";
        const periodEnd = this.getProcessTestInputState(technicalName).dateEnd || "";
        if (serialized && this.isNoveltyDateOutsidePeriod(serialized, periodStart, periodEnd)) {
            return;
        }
        this.setProcessWageChangeValue(technicalName, rowUid, {date: serialized});
    }

    getProcessContractConcepts(technicalName) {
        return this.getProcessSectionRows(technicalName, "contractConcepts");
    }

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
    }

    removeProcessContractConcept(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "contractConcepts", rowUid);
    }

    setProcessContractConceptValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "contractConcepts", rowUid, values);
    }

    getProcessContractConceptDateValue(technicalName, rowUid, fieldName) {
        const row = this.getProcessContractConcepts(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row[fieldName] : "");
    }

    getProcessContractConceptMinDate(technicalName, rowUid, fieldName) {
        if (fieldName !== "dateEnd") {
            return false;
        }
        return this.getProcessContractConceptDateValue(technicalName, rowUid, "dateStart") || false;
    }

    getProcessContractConceptMaxDate(technicalName, rowUid, fieldName) {
        if (fieldName !== "dateStart") {
            return false;
        }
        return this.getProcessContractConceptDateValue(technicalName, rowUid, "dateEnd") || false;
    }

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
    }

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
    }

    setProcessFixedValueRetention(technicalName, value) {
        this.setProcessTestInputValue(technicalName, "fixedValueRetentionProcedure", value);
    }

    getProcessRtfDeductions(technicalName) {
        return this.getProcessSectionRows(technicalName, "rtfDeductions");
    }

    get rtfSalaryRuleDomain() {
        return [["type_concept", "=", "tributaria"]];
    }

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
    }

    removeProcessRtfDeduction(technicalName, rowUid) {
        this.removeProcessSectionRow(technicalName, "rtfDeductions", rowUid);
    }

    setProcessRtfDeductionValue(technicalName, rowUid, values) {
        this.updateProcessSectionRow(technicalName, "rtfDeductions", rowUid, values);
    }

    getProcessRtfDeductionDateValue(technicalName, rowUid, fieldName) {
        const row = this.getProcessRtfDeductions(technicalName).find((item) => item.uid === rowUid);
        return this.toDateTimeValue(row ? row[fieldName] : "");
    }

    getProcessRtfDeductionMinDate(technicalName, rowUid, fieldName) {
        if (fieldName !== "dateEnd") {
            return false;
        }
        return this.getProcessRtfDeductionDateValue(technicalName, rowUid, "dateStart") || false;
    }

    getProcessRtfDeductionMaxDate(technicalName, rowUid, fieldName) {
        if (fieldName !== "dateStart") {
            return false;
        }
        return this.getProcessRtfDeductionDateValue(technicalName, rowUid, "dateEnd") || false;
    }

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
    }

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
    }

    getTestFieldRows(technicalName) {
        return this.state.testInputs[technicalName]?.fieldRows || [];
    }

    isTestFieldPickerOpen(technicalName) {
        return this.state.testFieldPicker.technicalName === technicalName;
    }

    async ensureTestModelFields(modelName) {
        if (this.state.testModelFieldsCache[modelName]) {
            return this.state.testModelFieldsCache[modelName];
        }
        const fields = await this.orm.call(
            "zue.testing.dashboard.session",
            "getTestModelFields",
            [modelName],
            {}
        );
        this.state.testModelFieldsCache = {
            ...this.state.testModelFieldsCache,
            [modelName]: fields || [],
        };
        return this.state.testModelFieldsCache[modelName];
    }

    async toggleTestFieldPicker(test) {
        if (this.isTestFieldPickerOpen(test.technical_name)) {
            this.closeTestFieldPicker();
            return;
        }
        await this.ensureTestModelFields(test.test_model);
        this.state.testFieldPicker = {technicalName: test.technical_name, search: ""};
    }

    closeTestFieldPicker() {
        this.state.testFieldPicker = {technicalName: false, search: ""};
    }

    getTestFieldPickerMeta(field) {
        return `${field.name} (${field.type})`;
    }

    onTestFieldPickerSearch(event) {
        this.state.testFieldPicker = {
            ...this.state.testFieldPicker,
            search: event.target.value || "",
        };
    }

    getFilteredPickerFields(test) {
        const allFields = this.state.testModelFieldsCache[test.test_model] || [];
        const usedNames = new Set(this.getTestFieldRows(test.technical_name).map((row) => row.name));
        const search = (this.state.testFieldPicker.search || "").trim().toLowerCase();
        return allFields.filter((field) => {
            if (usedNames.has(field.name)) {
                return false;
            }
            if (!search) {
                return true;
            }
            const label = (field.label || "").toLowerCase();
            const name = (field.name || "").toLowerCase();
            return label.includes(search) || name.includes(search);
        });
    }

    addTestFieldRow(test, fieldMeta) {
        const current = this.state.testInputs[test.technical_name] || this.getDefaultTestInputState(test);
        this.state.testFieldUid += 1;
        const row = {
            uid: this.state.testFieldUid,
            name: fieldMeta.name,
            label: fieldMeta.label,
            type: fieldMeta.type,
            value: "",
            options: fieldMeta.options || [],
            relation: fieldMeta.relation || false,
            relationOptions: [],
        };
        this.state.testInputs = {
            ...this.state.testInputs,
            [test.technical_name]: {
                ...current,
                fieldRows: [...current.fieldRows, row],
            },
        };
        this.closeTestFieldPicker();
        if (row.type === "many2one") {
            this.loadTestFieldRelationOptions(test, row.uid);
        }
    }

    removeTestFieldRow(technicalName, rowUid) {
        const current = this.state.testInputs[technicalName] || this.getDefaultTestInputState(
            this.selectedCatalogTests.find((item) => item.technical_name === technicalName)
        );
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...current,
                fieldRows: current.fieldRows.filter((row) => row.uid !== rowUid),
            },
        };
    }

    onTestFieldRowChange(technicalName, rowUid, event) {
        this.setTestFieldRowValue(technicalName, rowUid, event.target.value);
    }

    setTestFieldRowValue(technicalName, rowUid, value) {
        const current = this.state.testInputs[technicalName] || this.getDefaultTestInputState(
            this.selectedCatalogTests.find((item) => item.technical_name === technicalName)
        );
        this.state.testInputs = {
            ...this.state.testInputs,
            [technicalName]: {
                ...current,
                fieldRows: current.fieldRows.map((row) => (
                    row.uid === rowUid ? {...row, value} : row
                )),
            },
        };
    }

    getTestFieldRowChoices(row) {
        if (this.isBooleanTestField(row.type)) {
            return this.booleanFieldChoices;
        }
        if (this.isMany2oneTestField(row.type)) {
            return row.relationOptions || [];
        }
        return row.options || [];
    }

    isSelectMenuTestField(fieldType) {
        return this.isSelectionTestField(fieldType)
            || this.isMany2oneTestField(fieldType)
            || this.isBooleanTestField(fieldType);
    }

    ensureTestFieldRowOptions(test, row) {
        if (this.isMany2oneTestField(row.type)) {
            this.loadTestFieldRelationOptions(test, row.uid);
        }
    }

    getTestFieldRowDateValue(row) {
        return this.toDateTimeValue(row.value);
    }

    onTestFieldRowDateChange(technicalName, row, dateValue) {
        this.setTestFieldRowValue(technicalName, row.uid, this.serializeDateValue(dateValue, row.type));
    }

    async loadTestFieldRelationOptions(test, rowUid) {
        const current = this.state.testInputs[test.technical_name] || this.getDefaultTestInputState(test);
        const row = current.fieldRows.find((item) => item.uid === rowUid);
        if (!row) {
            return;
        }
        const options = await this.orm.call(
            "zue.testing.dashboard.session",
            "searchTestModelRelation",
            [test.test_model, row.name],
            {search: "", limit: 20}
        );
        this.state.testInputs = {
            ...this.state.testInputs,
            [test.technical_name]: {
                ...current,
                fieldRows: current.fieldRows.map((item) => (
                    item.uid === rowUid ? {...item, relationOptions: options || []} : item
                )),
            },
        };
    }

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
    }

    formatTestFieldDisplayValue(row) {
        const rawValue = row.value;
        if (this.isBooleanTestField(row.type)) {
            return rawValue === true || rawValue === "true" ? "Si" : "No";
        }
        if (this.isSelectionTestField(row.type)) {
            const option = (row.options || []).find((item) => String(item.value) === String(rawValue));
            return option ? option.label : String(rawValue);
        }
        if (this.isMany2oneTestField(row.type)) {
            const option = (row.relationOptions || []).find((item) => String(item.value) === String(rawValue));
            return option ? option.label : String(rawValue);
        }
        if (this.isMonetaryTestField(row.type)) {
            return this.formatMonetaryValue(rawValue) || String(rawValue);
        }
        return String(rawValue);
    }

    hasProcessResult(line) {
        return line.test_type === "process";
    }

    isBooleanTestField(fieldType) {
        return fieldType === "boolean";
    }

    isSelectionTestField(fieldType) {
        return fieldType === "selection";
    }

    isMany2oneTestField(fieldType) {
        return fieldType === "many2one";
    }

    isMonetaryTestField(fieldType) {
        return fieldType === "monetary";
    }

    isNumericTestField(fieldType) {
        return fieldType === "float" || fieldType === "integer" || fieldType === "monetary";
    }

    isDateTestField(fieldType) {
        return fieldType === "date" || fieldType === "datetime";
    }

    findModuleByProviderModel(providerModel) {
        for (const module of this.state.modules) {
            const group = (module.groups || []).find((item) => item.model === providerModel);
            if (group) {
                return {module, group};
            }
        }
        return false;
    }

    onModuleChange(moduleKey) {
        // Actualiza el modulo activo y sincroniza provider, filtro y catalogo.
        this.state.moduleKey = moduleKey;
        const groups = this.moduleGroups;
        if (!groups.some((group) => group.model === this.state.providerModel)) {
            this.state.providerModel = groups[0]?.model || false;
        }
        this.syncScopeWithProvider();
        this.syncSelectedTests();
    }

    onProviderChange(providerModel) {
        // Actualiza el provider activo y ajusta el filtro si ya no existe.
        this.state.providerModel = providerModel;
        this.state.groupSharedConfig = this.emptyGroupSharedConfig;
        this.syncScopeWithProvider();
        this.syncSelectedTests();
    }

    onScopeChange(scope) {
        // Actualiza el filtro activo para refrescar el catalogo de pruebas detectadas.
        this.state.scope = scope;
        this.syncSelectedTests();
    }

    onStatusFilterToggle(filterKey) {
        const current = this.state.statusFilters || {
            total: true,
            ok: false,
            controlled: false,
            failed: false,
        };
        const typeFilters = this.state.testTypeFilters || {parametric: false, process: false};
        const nextValue = !current[filterKey];
        const nextFilters = {...current, [filterKey]: nextValue};
        if (filterKey === "total") {
            if (nextValue) {
                nextFilters.ok = false;
                nextFilters.controlled = false;
                nextFilters.failed = false;
                this.state.testTypeFilters = {parametric: false, process: false};
            } else {
                nextFilters.total = true;
            }
        } else if (nextValue) {
            nextFilters.total = false;
        } else if (
            !nextFilters.ok
            && !nextFilters.controlled
            && !nextFilters.failed
            && !typeFilters.parametric
            && !typeFilters.process
        ) {
            nextFilters.total = true;
        }
        this.state.statusFilters = nextFilters;
    }

    isStatusFilterActive(filterKey) {
        return Boolean(this.state.statusFilters?.[filterKey]);
    }

    onTestTypeFilterToggle(filterKey) {
        // Mismo patrón que Correctas/Controladas/Fallidas: multi-selección y excluye Total.
        const current = this.state.testTypeFilters || {parametric: false, process: false};
        const statusFilters = this.state.statusFilters || {
            total: true,
            ok: false,
            controlled: false,
            failed: false,
        };
        const nextValue = !current[filterKey];
        const nextTypeFilters = {...current, [filterKey]: nextValue};
        if (nextValue) {
            this.state.statusFilters = {...statusFilters, total: false};
        } else if (
            !nextTypeFilters.parametric
            && !nextTypeFilters.process
            && !statusFilters.ok
            && !statusFilters.controlled
            && !statusFilters.failed
        ) {
            this.state.statusFilters = {...statusFilters, total: true};
        }
        this.state.testTypeFilters = nextTypeFilters;
    }

    isTestTypeFilterActive(filterKey) {
        return Boolean(this.state.testTypeFilters?.[filterKey]);
    }

    get isAnyDrawerOpen() {
        return Boolean(this.state.testsDrawerOpen || this.state.infoDrawerOpen);
    }

    onTestSelectionChange(technicalName, event) {
        const checked = event.target.checked;
        this.state.selectedTests = {
            ...this.state.selectedTests,
            [technicalName]: checked,
        };
        if (checked) {
            this.openTestsDrawer();
        }
        this.syncTestInputs();
    }

    onToggleAllTests(event) {
        const checked = event.target.checked;
        const nextSelection = {...this.state.selectedTests};
        for (const test of this.selectedCatalogTests) {
            nextSelection[test.technical_name] = checked;
        }
        this.state.selectedTests = nextSelection;
        if (checked) {
            this.openTestsDrawer();
        }
        this.syncTestInputs();
    }

    openTestsDrawer() {
        this.state.infoDrawerOpen = false;
        this.state.testsDrawerOpen = true;
    }

    closeTestsDrawer() {
        this.state.testsDrawerOpen = false;
    }

    toggleTestsDrawer() {
        if (this.state.testsDrawerOpen) {
            this.closeTestsDrawer();
            return;
        }
        this.openTestsDrawer();
    }

    openInfoDrawer() {
        this.state.testsDrawerOpen = false;
        this.state.infoDrawerOpen = true;
    }

    closeInfoDrawer() {
        this.state.infoDrawerOpen = false;
    }

    toggleInfoDrawer() {
        if (this.state.infoDrawerOpen) {
            this.closeInfoDrawer();
            return;
        }
        this.openInfoDrawer();
    }

    closeAllDrawers() {
        this.state.testsDrawerOpen = false;
        this.state.infoDrawerOpen = false;
    }

    onRunClick() {
        this.closeAllDrawers();
        return this.runSuite();
    }

    onStopClick() {
        this.closeAllDrawers();
        this.requestStop();
    }

    async onRefreshCatalogClick() {
        this.closeAllDrawers();
        await this.loadAdapterData();
    }

    async onClearClick() {
        this.closeAllDrawers();
        await this.clearScreen();
    }

    clearTestParameterization() {
        const nextInputs = {...this.state.testInputs};
        for (const test of this.selectedCatalogTests) {
            nextInputs[test.technical_name] = this.getDefaultTestInputState(test);
        }
        this.state.testInputs = nextInputs;
        if (this.isSocialBenefitsProvider || this.isGeneralLiquidationProvider || this.isPeriodClosureProvider) {
            this.state.groupSharedConfig = this.emptyGroupSharedConfig;
        }
        this.notification.add(_t("Parametrizacion de pruebas limpiada."), {type: "info"});
    }

    async loadAdapterData() {
        // Carga modulos, notas, leyenda de estados y la ultima ejecucion transient del usuario.
        const data = await this.orm.call("zue.testing.dashboard.session", "get_adapter_data", [], {});
        this.state.modules = data.modules || [];
        this.state.notes = data.notes || [];
        this.state.statusLegends = data.status_legends || [];
        if (this.restoreLastRun(data.last_run)) {
            return;
        }
        if (!this.state.moduleKey && this.state.modules.length) {
            this.state.moduleKey = this.state.modules[0].key;
        }
        if (!this.state.providerModel && this.moduleGroups.length) {
            this.state.providerModel = this.moduleGroups[0].model;
        }
        this.syncScopeWithProvider();
        this.syncSelectedTests();
    }

    restoreLastRun(lastRun) {
        // Restaura resultados previos si la sesion transient sigue existiendo.
        if (!lastRun) {
            return false;
        }
        const match = this.findModuleByProviderModel(lastRun.provider_model);
        if (!match) {
            return false;
        }
        this.state.moduleKey = match.module.key;
        this.state.providerModel = match.group.model;
        this.state.scope = lastRun.scope || false;
        this.syncScopeWithProvider();
        this.state.sessionId = lastRun.session_id || false;
        this.state.currentIndex = lastRun.current_index || 0;
        this.state.totalToRun = lastRun.total_to_run || 0;
        this.state.specs = [];
        this.state.lines.splice(0, this.state.lines.length, ...(lastRun.lines || []));
        this.state.counts = lastRun.counts || {total: 0, ok: 0, failed: 0, controlled: 0, skipped: 0};
        this.state.error = false;
        this.syncSelectedTests();
        return true;
    }

    async clearScreen() {
        // Limpia la pantalla y elimina la ultima sesion transient del usuario.
        if (this.state.running) {
            return;
        }
        try {
            await this.orm.call(
                "zue.testing.dashboard.session",
                "clear_last_run",
                [],
                {session_id: this.state.sessionId || false}
            );
            this.resetRunState();
            this.notification.add(_t("Resultados de pruebas limpiados."), {type: "info"});
        } catch (error) {
            this.state.error = this.getRpcErrorMessage(error);
            this.notification.add(this.state.error, {type: "danger"});
        }
    }

    resetRunState() {
        // Regresa contadores, progreso y resultados al estado inicial.
        this.state.sessionId = false;
        this.state.stopRequested = false;
        this.state.currentIndex = 0;
        this.state.totalToRun = 0;
        this.state.specs = [];
        this.state.lines.splice(0, this.state.lines.length);
        this.state.counts = {total: 0, ok: 0, failed: 0, controlled: 0, skipped: 0};
        this.state.statusFilters = {total: true, ok: false, controlled: false, failed: false};
        this.state.testTypeFilters = {parametric: false, process: false};
        this.state.error = false;
    }

    syncScopeWithProvider() {
        // Asegura que el filtro seleccionado exista en el provider activo.
        const scopes = this.availableScopes;
        if (!scopes.length) {
            this.state.scope = false;
            return;
        }
        const scopeExists = scopes.some((scope) => scope.value === this.state.scope);
        if (!scopeExists) {
            this.state.scope = scopes[0].value;
        }
    }

    async runSuite() {
        // Ejecuta las pruebas seleccionadas de forma secuencial mediante RPC.
        if (!this.canRun) {
            return;
        }
        const selectedTechnicalNames = this.selectedCatalogTests
            .filter((test) => this.isTestSelected(test.technical_name))
            .map((test) => test.technical_name);
        if (!selectedTechnicalNames.length) {
            this.notification.add(_t("Seleccione al menos una prueba para ejecutar."), {type: "warning"});
            return;
        }
        const noveltyValidationError = this.validateProcessNoveltiesBeforeRun(selectedTechnicalNames);
        if (noveltyValidationError) {
            this.notification.add(noveltyValidationError, {type: "warning"});
            return;
        }

        this.state.running = true;
        this.state.stopRequested = false;
        this.state.currentIndex = 0;
        this.state.totalToRun = 0;
        this.state.sessionId = false;
        this.state.specs = [];
        this.state.lines.splice(0, this.state.lines.length);
        this.state.error = false;
        this.state.counts = {total: 0, ok: 0, failed: 0, controlled: 0, skipped: 0};
        this.state.statusFilters = {total: true, ok: false, controlled: false, failed: false};
        this.state.testTypeFilters = {parametric: false, process: false};

        try {
            const scopeOption = this.availableScopes.find((scope) => scope.value === this.state.scope);
            const prepared = await this.orm.call(
                "zue.testing.dashboard.session",
                "prepare_run",
                [this.state.providerModel, this.state.scope || "all"],
                {
                    module_key: this.state.moduleKey || false,
                    module_name: this.selectedModule?.name || false,
                    scope_label: scopeOption?.label || this.state.scope || "all",
                }
            );
            const selectedNames = new Set(selectedTechnicalNames);
            const specsToRun = (prepared.specs || []).filter(
                (spec) => selectedNames.has(spec.technical_name)
            );
            this.state.sessionId = prepared.session_id;
            this.state.specs = specsToRun;
            this.state.totalToRun = specsToRun.length;
            this.state.counts = prepared.counts || this.state.counts;

            if (!specsToRun.length) {
                this.notification.add(_t("No hay pruebas seleccionadas para ejecutar."), {type: "warning"});
                return;
            }

            for (let index = 0; index < specsToRun.length; index++) {
                if (this.state.stopRequested) {
                    break;
                }
                const spec = specsToRun[index];
                const testInputPayload = this.buildTestParamsForRun(spec.technical_name);
                const result = await this.orm.call(
                    "zue.testing.dashboard.session",
                    "run_case",
                    [this.state.sessionId, spec.technical_name, index + 1],
                    {
                        test_params: testInputPayload.params,
                        test_data_lines: testInputPayload.displayLines,
                    }
                );
                this.state.lines.push(result.line);
                this.state.counts = result.counts || this.state.counts;
                this.state.currentIndex = index + 1;
            }

            if (this.state.sessionId && this.state.lines.length) {
                const finished = await this.orm.call(
                    "zue.testing.dashboard.session",
                    "finish_run",
                    [this.state.sessionId],
                    {stopped_early: this.state.stopRequested}
                );
                this.state.counts = finished.counts || this.state.counts;
                if (this.state.stopRequested) {
                    this.notification.add(_t("Ejecucion detenida antes del siguiente caso."), {type: "warning"});
                } else {
                    const message = finished.state === "success"
                        ? _t("Ejecucion finalizada sin fallos.")
                        : _t("Ejecucion finalizada con fallos.");
                    this.notification.add(message, {type: finished.state === "success" ? "success" : "danger"});
                }
            } else if (this.state.stopRequested) {
                this.notification.add(_t("Ejecucion detenida antes del siguiente caso."), {type: "warning"});
            }
        } catch (error) {
            this.state.error = this.getRpcErrorMessage(error);
            this.notification.add(this.state.error, {type: "danger"});
        } finally {
            this.state.running = false;
        }
    }

    requestStop() {
        // Solicita detener la ejecucion antes de lanzar el siguiente caso.
        this.state.stopRequested = true;
    }

    statusClass(status) {
        // Traduce el estado funcional de la linea a una clase visual del panel.
        if (status === "ok") {
            return "badge o_zue_testing_dashboard_badge_ok";
        }
        if (status === "controlled") {
            return "badge o_zue_testing_dashboard_badge_controlled";
        }
        if (status === "failed") {
            return "badge o_zue_testing_dashboard_badge_failed";
        }
        return "badge o_zue_testing_dashboard_badge_skipped";
    }

    catalogItemClass(test) {
        const classes = ["o_zue_testing_dashboard_catalog_item"];
        if (test?.test_type === "process") {
            classes.push("o_zue_testing_dashboard_catalog_item_process");
        } else if (test?.test_type === "parametric") {
            classes.push("o_zue_testing_dashboard_catalog_item_parametric");
        }
        return classes.join(" ");
    }

    testTypeClass(testType) {
        if (testType === "process") {
            return "badge o_zue_testing_dashboard_badge_test_type_process";
        }
        return "badge o_zue_testing_dashboard_badge_test_type_parametric";
    }

    testTypeLabel(testType) {
        if (testType === "process") {
            return _t("Proceso");
        }
        if (testType === "parametric") {
            return _t("Paramétrica");
        }
        return testType || "";
    }
}

registry.category("actions").add("zue_testing_dashboard.dashboard", ZueTestingDashboard);
