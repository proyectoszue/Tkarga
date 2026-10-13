# -*- coding: utf-8 -*-
# Core: field picker genérico (+ Agregar dato) sobre un test_model.

from odoo import _, api, models
from odoo.exceptions import UserError

AUDIT_TEST_MODEL_FIELDS = frozenset({
    "id",
    "create_uid",
    "create_date",
    "write_uid",
    "write_date",
    "display_name",
})


class ZueTestingDashboardSession(models.TransientModel):
    _inherit = "zue.testing.dashboard.session"

    def normalizeDashboardSelectionOptions(self, selection_values):
        """Normaliza opciones selection a pares value/label (Odoo 19 puede devolver formatos mixtos)."""
        options = []
        for item in selection_values or []:
            if isinstance(item, (list, tuple)):
                if len(item) >= 2:
                    options.append({"value": item[0], "label": item[1]})
                elif len(item) == 1:
                    options.append({"value": item[0], "label": str(item[0])})
                continue
            if isinstance(item, dict):
                value = item.get("value", item.get("key"))
                label = item.get("label", item.get("name", value))
                if value is not None:
                    options.append({"value": value, "label": label})
                continue
            options.append({"value": item, "label": str(item)})
        return options

    def resolveDashboardSelectionValues(self, model, field):
        """Obtiene la lista de selection de un campo de forma compatible con Odoo 19."""
        if hasattr(field, "_description_selection"):
            try:
                return field._description_selection(model.env) or []
            except Exception:
                pass
        selection_values = field.selection
        if callable(selection_values):
            selection_values = selection_values(model)
        return selection_values or []

    @api.model
    def getTestModelFields(self, model_name):
        """Devuelve metadata de campos editables de un modelo para datos de prueba."""
        if not model_name or model_name not in self.env.registry.models:
            raise UserError(_("Modelo no disponible: %s") % model_name)
        model = self.env[model_name]
        fields_payload = []
        for field_name, field in model._fields.items():
            if field_name in AUDIT_TEST_MODEL_FIELDS:
                continue
            if field.type in ("one2many", "many2many", "binary", "html"):
                continue
            if field.compute and not field.inverse:
                continue
            if field.readonly:
                continue
            field_info = {
                "name": field_name,
                "label": field.string or field_name,
                "type": field.type,
                "required": bool(field.required),
            }
            if field.type == "selection":
                field_info["options"] = self.normalizeDashboardSelectionOptions(
                    self.resolveDashboardSelectionValues(model, field)
                )
            if field.type == "many2one":
                field_info["relation"] = field.comodel_name
            fields_payload.append(field_info)
        fields_payload.sort(key=lambda item: (item["label"] or item["name"]).lower())
        return fields_payload

    @api.model
    def searchTestModelRelation(self, model_name, field_name, search="", limit=20):
        """Busca registros para campos many2one del selector de datos de prueba."""
        if not model_name or model_name not in self.env.registry.models:
            return []
        field = self.env[model_name]._fields.get(field_name)
        if not field or field.type != "many2one":
            return []
        # sudo: required to search related records for dashboard test data picker
        records = self.env[field.comodel_name].sudo().name_search(search or "", limit=limit)
        return [{"value": record_id, "label": label} for record_id, label in records]

    @api.model
    def getDashboardSelectionOptions(self, model_name, field_name):
        """Devuelve las opciones reales de un campo selection desde el modelo de BD."""
        if not model_name or model_name not in self.env.registry.models:
            return []
        field = self.env[model_name]._fields.get(field_name)
        if not field or field.type != "selection":
            return []
        return self.normalizeDashboardSelectionOptions(
            self.resolveDashboardSelectionValues(self.env[model_name], field)
        )

    @api.model
    def searchDashboardRecords(self, model_name, search="", limit=20, ids=None, domain=None):
        """Busca registros por nombre o ids para selectores del panel de pruebas."""
        if not model_name or model_name not in self.env.registry.models:
            return []
        # sudo: required to search records for dashboard process test pickers
        model = self.env[model_name].sudo()
        search_domain = list(domain or [])
        if ids:
            records = model.browse([int(item) for item in ids if item]).exists()
            if search_domain:
                records = records.filtered_domain(search_domain)
            return [{"value": record.id, "label": record.display_name} for record in records]
        records = model.name_search(search or "", domain=search_domain, limit=limit)
        return [{"value": record_id, "label": label} for record_id, label in records]
