/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentsListController } from "@documents/views/list/documents_list_controller";
import { DocumentsZueControllerMixin } from "../documents_zue_controller_mixin";

patch(DocumentsListController.prototype, DocumentsZueControllerMixin());
