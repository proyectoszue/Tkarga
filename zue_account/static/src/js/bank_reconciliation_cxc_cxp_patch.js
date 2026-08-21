/** @odoo-module **/

import { BankRecButtonList } from "@account_accountant/components/bank_reconciliation/button_list/button_list";
import { BankReconciliationService } from "@account_accountant/components/bank_reconciliation/bank_reconciliation_service";
import { patch } from "@web/core/utils/patch";

const RECEIVABLE_PAYABLE_DOMAIN = [
    ["search_account_id.account_type", "in", ["asset_receivable", "liability_payable"]],
];

function isRestrictedRecord(record) {
    return Boolean(record?.data?.z_bank_auto_reconcile_receivable_payable_only);
}

function buildBaseDomain(records) {
    return [
        ["parent_state", "in", ["draft", "posted"]],
        [
            "partner_id",
            "in",
            records.filter((record) => !!record.data.partner_id.id).map((record) => record.data.partner_id.id),
        ],
        ["company_id", "child_of", records.map((record) => record.data.company_id.id)],
        ["search_account_id.reconcile", "=", true],
        ["display_type", "not in", ["line_section", "line_note"]],
        ["reconciled", "=", false],
        ["statement_line_id", "not in", records.map((record) => record.data.id)],
    ];
}

function buildStandardCountDomain(records) {
    return [
        ...buildBaseDomain(records),
        "|",
        ["search_account_id.account_type", "not in", ["asset_receivable", "liability_payable"]],
        ["payment_id", "=", false],
    ];
}

function buildRestrictedCountDomain(records) {
    return [...buildBaseDomain(records), ...RECEIVABLE_PAYABLE_DOMAIN];
}

patch(BankRecButtonList.prototype, {
    getReconcileButtonDomain() {
        if (!this.statementLineData.z_bank_auto_reconcile_receivable_payable_only) {
            return super.getReconcileButtonDomain();
        }
        return [
            ["parent_state", "in", ["draft", "posted"]],
            ["company_id", "child_of", this.statementLineData.company_id.id],
            ["search_account_id.reconcile", "=", true],
            ...RECEIVABLE_PAYABLE_DOMAIN,
            ["display_type", "not in", ["line_section", "line_note"]],
            ["reconciled", "=", false],
            ["statement_line_id", "!=", this.statementLineData.id],
        ];
    },
});

patch(BankReconciliationService.prototype, {
    async computeReconcileLineCountPerPartnerId(records) {
        const standardRecords = records.filter((record) => !isRestrictedRecord(record));
        const restrictedRecords = records.filter(isRestrictedRecord);
        const reconcileCountPerPartnerId = {};
        const addGroupCounts = (groups) => {
            groups.forEach((group) => {
                const partnerId = group.partner_id[0];
                reconcileCountPerPartnerId[partnerId] =
                    (reconcileCountPerPartnerId[partnerId] || 0) + group["id:count"];
            });
        };

        if (standardRecords.length) {
            const groups = await this.orm.formattedReadGroup(
                "account.move.line",
                buildStandardCountDomain(standardRecords),
                ["partner_id"],
                ["id:count"]
            );
            addGroupCounts(groups);
        }

        if (restrictedRecords.length) {
            const groups = await this.orm.formattedReadGroup(
                "account.move.line",
                buildRestrictedCountDomain(restrictedRecords),
                ["partner_id"],
                ["id:count"]
            );
            addGroupCounts(groups);
        }

        this.reconcileCountPerPartnerId = reconcileCountPerPartnerId;
    },
});
