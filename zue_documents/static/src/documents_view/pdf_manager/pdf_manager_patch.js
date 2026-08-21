/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PdfManager } from "@documents/owl/components/pdf_manager/pdf_manager";

patch(PdfManager.prototype, {
    async onClickSplit() {
        this.state.keepDocument = true;
        if (this.props.documents.length > 1) {
            const allPages = this.sortedPagesIds;
            if (!allPages.length) {
                this._displayErrorNotification(_t("No document has been selected"));
                return;
            }
            this.state.groupData = {};
            this.state.groupIds = [];
            this._createGroup({
                name: _t("Merged Document"),
                pageIds: allPages,
                isSelected: true,
            });
            await this._applyChanges();
            return;
        }
        this._applyChanges();
    },
});
