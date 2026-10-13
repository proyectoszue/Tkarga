# -*- coding: utf-8 -*-
# Payroll: formateo de historial para SS / provisiones.

from odoo import models


class ZueTestingDashboardLinePayroll(models.TransientModel):
    """Formateo de historial para layouts de cierres de periodo (SS / Provisiones)."""

    _inherit = "zue.testing.dashboard.line"

    def formatObtainedInfoResultText(self, records):
        if (
            len(records) == 1
            and isinstance(records[0], dict)
            and records[0].get("layout") == "social_security"
        ):
            return self.formatSocialSecurityResultText(records[0])
        if (
            len(records) == 1
            and isinstance(records[0], dict)
            and records[0].get("layout") == "provisions"
        ):
            return self.formatProvisionsResultText(records[0])
        return super().formatObtainedInfoResultText(records)

    def formatSocialSecurityResultText(self, payload):
        """Texto legible del resultado SS para el historial."""
        header_info = payload.get("header_info") or {}
        lines = [
            "Empleado: %s" % (payload.get("employee") or header_info.get("employee") or "-"),
            "Contrato: %s" % (payload.get("contract") or header_info.get("contract") or "-"),
            "Periodo: %s" % (payload.get("period") or header_info.get("period") or "-"),
            "Compania: %s" % (header_info.get("company") or "-"),
            "Lineas: %s" % (header_info.get("line_count") if header_info.get("line_count") is not None else "-"),
            "Tiempo: %s" % (header_info.get("time_process") or "-"),
            "Estado: %s" % (header_info.get("state_label") or payload.get("header_state") or "-"),
            "Cabecera: %s" % (payload.get("header") or header_info.get("header_name") or "-"),
        ]
        for segment in payload.get("segments") or []:
            if not isinstance(segment, dict):
                continue
            lines.append("")
            lines.append(segment.get("label") or "Tramo")
            for section_key, section_label in (
                ("info_days", "Info y dias"),
                ("health", "Salud"),
                ("pension", "Pension"),
                ("arp", "ARP"),
                ("parafiscales", "Parafiscales"),
                ("absence_dates", "Ausencia y fechas"),
            ):
                fields = segment.get(section_key) or []
                if not fields:
                    continue
                lines.append("  [%s]" % section_label)
                for field_row in fields:
                    if not isinstance(field_row, dict):
                        continue
                    value_type = field_row.get("value_type") or "text"
                    lines.append("    %s: %s" % (
                        field_row.get("label") or "-",
                        self.formatProcessResultCell(
                            field_row.get("value"),
                            monetary=value_type == "monetary",
                        ),
                    ))
        warnings = payload.get("warnings") or []
        if warnings:
            lines.append("")
            lines.append("[Advertencias]")
            for warning in warnings:
                if isinstance(warning, dict):
                    lines.append(
                        "  - %s | %s | %s"
                        % (
                            warning.get("employee") or "-",
                            warning.get("branch") or "-",
                            warning.get("description") or "-",
                        )
                    )
        accounting = payload.get("accounting") or False
        if isinstance(accounting, dict):
            lines.append("")
            lines.append("[Contabilizacion]")
            lines.append("  Asiento: %s" % (accounting.get("move_name") or "-"))
            lines.append("  Referencia: %s" % (accounting.get("move_ref") or "-"))
            lines.append("  Estado: %s" % (accounting.get("move_state") or "-"))
            lines.append("  Fecha: %s" % (accounting.get("move_date") or "-"))
            for process in accounting.get("processes") or []:
                if not isinstance(process, dict):
                    continue
                lines.append("  [%s]" % (process.get("label") or process.get("code") or "-"))
                for move_line in process.get("lines") or []:
                    if not isinstance(move_line, dict):
                        continue
                    lines.append(
                        "    %s | %s | D:%s C:%s"
                        % (
                            move_line.get("name") or "-",
                            move_line.get("account") or "-",
                            self.formatProcessResultCell(move_line.get("debit"), monetary=True),
                            self.formatProcessResultCell(move_line.get("credit"), monetary=True),
                        )
                    )
        return "\n".join(lines)

    def formatProvisionsResultText(self, payload):
        """Texto legible del resultado de provisiones para el historial."""
        header_info = payload.get("header_info") or {}
        lines = [
            "Empleado: %s" % (payload.get("employee") or header_info.get("employee") or "-"),
            "Contrato: %s" % (payload.get("contract") or header_info.get("contract") or "-"),
            "Periodo: %s" % (payload.get("period") or header_info.get("period") or "-"),
            "Compania: %s" % (header_info.get("company") or "-"),
            "Lineas: %s" % (header_info.get("line_count") if header_info.get("line_count") is not None else "-"),
            "Tiempo: %s" % (header_info.get("time_process") or "-"),
            "Estado: %s" % (header_info.get("state_label") or payload.get("header_state") or "-"),
            "Cabecera: %s" % (payload.get("header") or header_info.get("header_name") or "-"),
            "",
            "[Provisiones]",
        ]
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            lines.append(
                "  %s | liquidado:%s | pagos:%s | a pagar:%s | provision mes:%s%s"
                % (
                    row.get("label") or row.get("code") or "-",
                    self.formatProcessResultCell(row.get("amount"), monetary=True),
                    self.formatProcessResultCell(row.get("value_payments"), monetary=True),
                    self.formatProcessResultCell(row.get("current_payable_value"), monetary=True),
                    self.formatProcessResultCell(row.get("value_balance"), monetary=True),
                    " (sin detalle)" if row.get("missing") else "",
                )
            )
            detail = row.get("detail") or {}
            if isinstance(detail, dict):
                for column_key, column_label in (
                    ("column_left", "Columna izquierda"),
                    ("column_right", "Columna derecha"),
                ):
                    fields = detail.get(column_key) or []
                    if not fields:
                        continue
                    lines.append("    [%s]" % column_label)
                    for field_row in fields:
                        if not isinstance(field_row, dict):
                            continue
                        value_type = field_row.get("value_type") or "text"
                        lines.append("      %s: %s" % (
                            field_row.get("label") or "-",
                            self.formatProcessResultCell(
                                field_row.get("value"),
                                monetary=value_type == "monetary",
                            ),
                        ))
        warnings = payload.get("warnings") or []
        if warnings:
            lines.append("")
            lines.append("[Advertencias]")
            for warning in warnings:
                if isinstance(warning, dict):
                    lines.append(
                        "  - %s | %s | %s"
                        % (
                            warning.get("employee") or "-",
                            warning.get("contract") or "-",
                            warning.get("description") or "-",
                        )
                    )
        accounting = payload.get("accounting") or False
        if isinstance(accounting, dict):
            lines.append("")
            lines.append("[Contabilizacion]")
            lines.append("  Asiento: %s" % (accounting.get("move_name") or "-"))
            lines.append("  Referencia: %s" % (accounting.get("move_ref") or "-"))
            lines.append("  Estado: %s" % (accounting.get("move_state") or "-"))
            lines.append("  Fecha: %s" % (accounting.get("move_date") or "-"))
            for process in accounting.get("processes") or []:
                if not isinstance(process, dict):
                    continue
                lines.append("  [%s]" % (process.get("label") or process.get("code") or "-"))
                for move_line in process.get("lines") or []:
                    if not isinstance(move_line, dict):
                        continue
                    lines.append(
                        "    %s | %s | D:%s C:%s"
                        % (
                            move_line.get("name") or "-",
                            move_line.get("account") or "-",
                            self.formatProcessResultCell(move_line.get("debit"), monetary=True),
                            self.formatProcessResultCell(move_line.get("credit"), monetary=True),
                        )
                    )
        return "\n".join(lines)

