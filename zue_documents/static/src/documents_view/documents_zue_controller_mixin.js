/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";

export const DocumentsZueControllerMixin = () => ({
    setup() {
        super.setup(...arguments);
        this.actionService = useService("action");
    },

    getActionService() {
        return this.actionService || this.env.services.action;
    },

    getZueActionContext() {
        const context = this.props.context || {};
        const folderId = this.env.searchModel.getSelectedFolderId();
        return {
            default_partner_id: context.default_partner_id || false,
            default_folder_id: folderId || this.env.searchModel.getFolders()[1]?.id || false,
            default_res_id: context.default_res_id || false,
            default_res_model: context.default_res_model || false,
        };
    },

    async onClickDocumentsRequestTemplate() {
        await this.getActionService().doAction("zue_documents.action_request_template_form", {
            additionalContext: this.getZueActionContext(),
            fullscreen: this.env.isSmall,
            onClose: async () => {
                await this.env.model.load();
                this.env.model.notify();
            },
        });
    },

    async onClickDocumentsMergePDFs() {
        await this.getActionService().doAction("zue_documents.action_merge_pdf_form", {
            additionalContext: this.getZueActionContext(),
            fullscreen: this.env.isSmall,
        });
    },
});
