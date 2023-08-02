odoo.define("zue_documents.ListView", function (require) {
    "use strict";

    const ZueListController = require("zue_documents.DocumentsListController");
    const ListView = require("documents.DocumentsListView");
    const viewRegistry = require("web.view_registry");

    const ZueListView = ListView.extend({
        config: Object.assign({}, ListView.prototype.config, {
            Controller: ZueListController,
        }),
    });

    viewRegistry.add("documents_list", ZueListView);
    return ZueListView;
});
