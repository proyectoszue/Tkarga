odoo.define("zue_documents.DocumentsControllerMixin", function (require) {
    "use strict";

        const config = require('web.config');
        const { _t, qweb } = require('web.core');

        const DocumentsZueControllerMixin = {
        events: {
            'click .o_documents_kanban_request_template': '_onClickDocumentsRequestTemplate',
            'click .o_documents_kanban_merge_pdfs': '_onClickDocumentsMergePDFs',
        },

        _onClickDocumentsRequestTemplate(ev) {
            ev.preventDefault();
            const context = this.model.get(this.handle, {raw: true}).getContext();
                this.do_action('zue_documents.action_request_template_form', {
                additional_context: {
                    default_partner_id: context.default_partner_id || false,
                },
                fullscreen: config.device.isMobile,
                on_close: () => this.reload(),
            });
        },

        _onClickDocumentsMergePDFs(ev) {
            ev.preventDefault();
            const context = this.model.get(this.handle, {raw: true}).getContext();
                this.do_action('zue_documents.action_merge_pdf_form', {
                fullscreen: config.device.isMobile,
                on_close: () => this.reload(),
            });
        },

        updateButtons() {
            const selectedFolderId = this.searchModel.get("selectedFolderId");
            this.$buttons[0].querySelector(
                ".o_documents_kanban_request_template"
            ).disabled = !selectedFolderId;
            this.$buttons[0].querySelector(
                ".o_documents_kanban_merge_pdfs"
            ).disabled = !selectedFolderId;
        },
    };

    return DocumentsZueControllerMixin;
});
