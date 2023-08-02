odoo.define("zue_documents.KanbanView", function (require) {
    "use strict";

    const ZueKanbanController = require("zue_documents.KanbanController");
    const KanbanView = require("documents.DocumentsKanbanView");
    const viewRegistry = require("web.view_registry");

    const ZueKanbanView = KanbanView.extend({
        config: Object.assign({}, KanbanView.prototype.config, {
            Controller: ZueKanbanController,
        }),
    });

    viewRegistry.add("documents_kanban", ZueKanbanView);
    return ZueKanbanView;
});
