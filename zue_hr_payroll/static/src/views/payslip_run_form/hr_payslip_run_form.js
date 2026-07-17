import { markup } from "@odoo/owl";
import { serializeDate } from "@web/core/l10n/dates";
import { PayslipBatchFormController } from "@hr_payroll/views/payslip_run_form/hr_payslip_run_form"
import { patch } from "@web/core/utils/patch";

patch(PayslipBatchFormController.prototype, {
    async selectEmployees() {
        const employeeListAction = await this.orm.call("hr.payslip.run", "action_payroll_hr_version_list_view_payrun", [
            [this.model.root.resId],
            serializeDate(this.model.root.data.date_start),
            serializeDate(this.model.root.data.date_end),
            this.model.root.data.structure_id?.id,
            this.model.root.data.company_id?.id,
            this.model.root.data.schedule_pay,
            this.model.root.data.z_filter_state_finished,
            this.model.root.data.method_schedule_pay,
            this.model.root.data.prima_run_reverse_id?.id || false,
        ]);
        return this.actionService.doAction({
            ...employeeListAction,
            help: markup(employeeListAction.help),
            context: {
                raw_record: this.model.root.data,
            },
        });
    }
});
