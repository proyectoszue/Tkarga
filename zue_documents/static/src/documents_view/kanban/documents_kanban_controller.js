/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentsKanbanController } from "@documents/views/kanban/documents_kanban_controller";
import { DocumentsZueControllerMixin } from "../documents_zue_controller_mixin";

patch(DocumentsKanbanController.prototype, DocumentsZueControllerMixin());
