import { VersionPayrunListController } from "@hr_payroll/views/payslip_run_version_list/hr_version_list_controller";
import { patch } from "@web/core/utils/patch";

patch(VersionPayrunListController.prototype, {
    buildRawRecord(rawRecord) {
        const record = super.buildRawRecord(...arguments);
        record.prima_run_reverse_id = rawRecord.prima_run_reverse_id?.id || false;
        return record;
    },
});
