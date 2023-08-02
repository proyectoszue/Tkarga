odoo.define("zue_documents.KanbanController", function (require) {
    "use strict";

    const DocumentsKanbanController = require("documents.DocumentsKanbanController");
    const DocumentsControllerMixin = require("documents.controllerMixin");
    const DocumentsZueControllerMixin = require("zue_documents.DocumentsControllerMixin");

    const ZueKanbanController = DocumentsKanbanController.extend(
        DocumentsZueControllerMixin,
        {
            events: Object.assign(
                {},
                DocumentsKanbanController.prototype.events,
                DocumentsZueControllerMixin.events,
                DocumentsControllerMixin.events
            ),
            custom_events: Object.assign(
                {},
                DocumentsKanbanController.prototype.custom_events,
                DocumentsZueControllerMixin.custom_events,
                DocumentsControllerMixin.custom_events
            ),

            /**
             * @override
             */
            updateButtons() {
                this._super(...arguments);
                DocumentsControllerMixin.updateButtons.apply(this, arguments);
                DocumentsZueControllerMixin.updateButtons.apply(this, arguments);
            },
        }
    );

    return ZueKanbanController;
});
