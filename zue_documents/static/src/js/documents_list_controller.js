odoo.define("zue_documents.DocumentsListController", function (require) {
    "use strict";

    const DocumentsListController = require("documents.DocumentsListController");
    const DocumentsControllerMixin = require("documents.controllerMixin");
    const DocumentsZueControllerMixin = require("zue_documents.DocumentsControllerMixin");

    const ZueListController = DocumentsListController.extend(
        DocumentsZueControllerMixin,
        {
            events: Object.assign(
                {},
                DocumentsListController.prototype.events,
                DocumentsZueControllerMixin.events,
                DocumentsControllerMixin.events
            ),
            custom_events: Object.assign(
                {},
                DocumentsListController.prototype.custom_events,
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
    return ZueListController;
});
