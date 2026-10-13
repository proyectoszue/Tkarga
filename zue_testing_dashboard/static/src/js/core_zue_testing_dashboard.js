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
import { ZueProcessResultViewer } from "@zue_testing_dashboard/js/core_process_result_viewer";

const VERSION_SEARCH_LIMIT = 7;
const VERSION_SEARCH_MORE_LIMIT = 320;

/** Core: many2one genérico del field picker / selectores del panel. */
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

/** Core: pantalla principal del panel (UI base + ganchos para dominios). */
export class ZueTestingDashboard extends Component {

    static template = "zue_testing_dashboard.ZueTestingDashboard";
    static components = {
        DateTimeInput,
        SelectMenu,
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
            groupSharedConfig: this.emptyGroupSharedConfig,
            testModelFieldsCache: {},
            testFieldPicker: {technicalName: false, search: ""},
            testFieldUid: 0,
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

    async loadProcessFormOptions() {}

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

    get showGroupSharedConfig() {
        // Dominio: si mostrar el bloque "Configuración compartida".
        return false;
    }

    applyGroupSharedConfig() {
        // Dominio: copiar config compartida a las pruebas marcadas.
    }

    get emptyGroupSharedConfig() {
        // Dominio: estado inicial de la config compartida.
        return {};
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
        const parametricChoices = [];
        const processChoices = [];
        for (const group of this.moduleGroups || []) {
            const specs = group.specs || [];
            const choice = {value: group.model, label: group.name};
            const hasProcess = specs.some((spec) => spec.test_type === "process");
            const hasParametric = specs.some((spec) => spec.test_type === "parametric");
            if (hasProcess && !hasParametric) {
                processChoices.push(choice);
            } else if (hasParametric && !hasProcess) {
                parametricChoices.push(choice);
            } else if (hasProcess) {
                processChoices.push(choice);
            } else {
                parametricChoices.push(choice);
            }
        }
        const groups = [];
        if (parametricChoices.length) {
            groups.push({label: _t("Paramétricas"), choices: parametricChoices});
        }
        if (processChoices.length) {
            groups.push({label: _t("Proceso"), choices: processChoices});
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
        return {fieldRows: []};
    }

    needsTestInputState(test) {
        // Si la prueba necesita estado de inputs en la UI.
        return test.test_type === "process" || Boolean(test.test_model);
    }

    showParametricFieldPicker(test) {
        // Si mostrar el picker genérico "+ Agregar dato".
        return Boolean(test?.test_model) && test?.test_type !== "process";
    }

    syncTestInputs() {
        const nextInputs = {...this.state.testInputs};
        for (const test of this.selectedCatalogTests) {
            if (this.needsTestInputState(test)) {
                if (!nextInputs[test.technical_name]) {
                    nextInputs[test.technical_name] = this.getDefaultTestInputState(test);
                }
            }
        }
        this.state.testInputs = nextInputs;
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

    validateBeforeRun(_selectedTechnicalNames) {
        // Dominio: mensaje de error para abortar, o false para continuar.
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
        const test = (this.selectedProvider?.specs || []).find(
            (item) => item.technical_name === technicalName
        );
        const inputState = this.state.testInputs[technicalName] || this.getDefaultTestInputState(test);
        const params = {};
        const displayLines = [];
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
        if (this.showGroupSharedConfig) {
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
        const validationError = this.validateBeforeRun(selectedTechnicalNames);
        if (validationError) {
            this.notification.add(validationError, {type: "warning"});
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
