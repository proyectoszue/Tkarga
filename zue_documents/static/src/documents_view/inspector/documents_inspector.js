/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DateTimeField } from "@web/views/fields/datetime/datetime_field";
import { DETAIL_PANEL_REQUIRED_FIELDS } from "@documents/views/hooks";
import { DocumentsDetailsPanel } from "@documents/components/documents_details_panel/documents_details_panel";

if (!DETAIL_PANEL_REQUIRED_FIELDS.includes("expiration_date")) {
    DETAIL_PANEL_REQUIRED_FIELDS.push("expiration_date");
}

patch(DocumentsDetailsPanel, {
    components: {
        ...DocumentsDetailsPanel.components,
        DateTimeField,
    },
});
