/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { router } from "@web/core/browser/router";
import { _t } from "@web/core/l10n/translation";
import { fileUploadService } from "@web/core/file_upload/file_upload_service";
import { DocumentService } from "@documents/core/document_service";
import { DocumentsKanbanModel } from "@documents/views/kanban/documents_kanban_model";
import { DocumentsListModel } from "@documents/views/list/documents_list_model";
import * as documentsUtils from "@documents/views/utils";

/** Controlador activo durante /documents/upload (handler estándar de Odoo se omite). */
let activeUploadController = null;

function isDocumentsUpload(upload) {
    const url = upload?.xhr?.responseURL || "";
    return url.includes("/documents/upload");
}

function prepareDocumentsUpload(component) {
    const model = component.model;
    if (!model || model.config?.resModel !== "documents.document") {
        return;
    }
    activeUploadController = component;
    model._skipSelectionReapply = true;
    model.originalSelection = [];
    delete component.props?.state?.modelState?.sharedSelection;
    model.root?.selection?.forEach((record) => record?.toggleSelection?.(false));
    component.documentService?.setPreviewedDocument?.(null);
}

export function patchDocumentsUploadHandlers(component) {
    if (component._zueDocumentsUploadPatched) {
        return;
    }
    component._zueDocumentsUploadPatched = true;

    const wrap = (handler) => {
        if (!handler) {
            return handler;
        }
        return async (...args) => {
            prepareDocumentsUpload(component);
            return handler.apply(component, args);
        };
    };

    component.uploadFiles = wrap(component.uploadFiles);
    component.onFileInputChange = wrap(component.onFileInputChange);
}

function parseUploadDocumentIds(xhr) {
    const response = xhr.response;
    if (typeof response !== "string") {
        return null;
    }
    const trimmed = response.trim();
    if (!trimmed || trimmed.startsWith("<") || trimmed.startsWith("<!")) {
        return null;
    }
    try {
        const parsed = JSON.parse(trimmed);
        return Array.isArray(parsed) ? parsed : null;
    } catch {
        return null;
    }
}

async function handleDocumentsUploadLoaded(payload) {
    const component = activeUploadController;
    activeUploadController = null;
    if (!component) {
        return;
    }

    const { upload } = payload;
    const xhr = upload.xhr;
    const notification = component.notification;
    const documentService = component.documentService;
    const env = component.env;
    const model = component.model;

    if (xhr.status !== 200) {
        notification.add(
            _t("status code: %(status)s, message: %(message)s", {
                status: xhr.status,
                message: xhr.response,
            }),
            { type: "danger", sticky: true }
        );
        return;
    }

    const newDocumentIds = parseUploadDocumentIds(xhr);
    if (newDocumentIds === null) {
        notification.add(
            _t("La respuesta del servidor no es válida. Verifique el filestore o los logs."),
            { type: "danger", sticky: true }
        );
        return;
    }

    model._skipSelectionReapply = true;
    model.originalSelection = [];

    await env.model.load(component.props);

    if (!newDocumentIds.length) {
        return;
    }

    model.root.selection.forEach((record) => record?.toggleSelection?.(false));
    const newRecords = env.model.root.records.filter(
        (record) => record && newDocumentIds.includes(record.resId)
    );
    newRecords.forEach((record) => record.toggleSelection(true));
    if (newRecords[0]) {
        documentService.focusRecord(newRecords[0]);
    }
}

const originalFileUploadStart = fileUploadService.start;
patch(fileUploadService, {
    start(env, services) {
        const result = originalFileUploadStart.call(fileUploadService, env, services);
        if (!result.bus._zueDocumentsUploadGuard) {
            result.bus._zueDocumentsUploadGuard = true;
            const originalTrigger = result.bus.trigger.bind(result.bus);
            result.bus.trigger = (name, payload) => {
                if (
                    name === "FILE_UPLOAD_LOADED" &&
                    isDocumentsUpload(payload?.upload) &&
                    activeUploadController
                ) {
                    void handleDocumentsUploadLoaded(payload);
                    return;
                }
                if (name === "FILE_UPLOAD_ERROR") {
                    activeUploadController = null;
                }
                return originalTrigger(name, payload);
            };
        }
        return result;
    },
});

function patchDocumentsModelProto(proto) {
    if (proto._zueDocumentsModelPatched) {
        return;
    }
    proto._zueDocumentsModelPatched = true;

    const originalLoad = proto.load;
    const originalReapplySelection = proto._reapplySelection;

    patch(proto, {
        get targetRecords() {
            const previewed = this.documentService.rightPanelReactive.previewedDocument;
            const records = previewed ? [previewed.record] : this.root.selection;
            return records.filter((record) => record);
        },

        exportSelection() {
            return this.targetRecords.map((record) => record.resId);
        },

        async load() {
            const selection = this.root?.selection;
            if (this._skipSelectionReapply) {
                this.originalSelection = [];
            } else if (!this.originalSelection && selection?.length > 0) {
                this.originalSelection = selection
                    .filter((record) => record)
                    .map((record) => record.resId);
            }
            return originalLoad.call(this, ...arguments);
        },

        _reapplySelection() {
            if (this._skipSelectionReapply) {
                delete this._skipSelectionReapply;
                delete this.originalSelection;
                return;
            }
            return originalReapplySelection.call(this, ...arguments);
        },
    });
}

patchDocumentsModelProto(Object.getPrototypeOf(DocumentsKanbanModel.prototype));
patchDocumentsModelProto(Object.getPrototypeOf(DocumentsListModel.prototype));

const originalGetCommonEmbeddedActions = documentsUtils.getCommonEmbeddedActions;
patch(documentsUtils, {
    getCommonEmbeddedActions(documents) {
        return originalGetCommonEmbeddedActions(documents?.filter((doc) => doc) ?? []);
    },
});

patch(DocumentService.prototype, {
    updateDocumentURL(folderChange, inspectedDocuments, forceInspected) {
        let accessToken;
        if (folderChange) {
            accessToken = folderChange.access_token;
            this.currentFolderAccessToken = accessToken;
        } else if (inspectedDocuments?.length === 1) {
            const record = inspectedDocuments[0];
            if (
                record &&
                (forceInspected ||
                    record.selected ||
                    record.isContainer ||
                    this.rightPanelReactive.previewedDocument?.record?.id === record.id)
            ) {
                accessToken = record.data?.access_token;
            }
        } else if (!inspectedDocuments?.length) {
            accessToken = this.currentFolderAccessToken;
        }
        if (accessToken) {
            router.pushState({ access_token: accessToken });
        }
    },

    focusRecord(record, forceSelected) {
        if (!record) {
            if (this.focusedRecord) {
                this.rightPanelReactive.focusedRecord = null;
                this.updateDocumentURL(null, null, forceSelected);
            }
            return;
        }
        return super.focusRecord(record, forceSelected);
    },
});

