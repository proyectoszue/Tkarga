# -*- coding: utf-8 -*-

from odoo import fields, models


class ZueTestingDashboardRun(models.TransientModel):
    _name = "zue.testing.dashboard.run"
    _description = "Historial de ejecuciones del panel de pruebas ZUE"
    _order = "started_at desc, id desc"
    _transient_max_hours = 24.0

    name = fields.Char(string="Referencia", required=True, readonly=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Usuario",
        required=True,
        readonly=True,
        default=lambda self: self.env.user,
    )
    module_key = fields.Char(string="Clave modulo", readonly=True)
    module_name = fields.Char(string="Modulo", readonly=True)
    provider_model = fields.Char(string="Modelo proveedor", readonly=True)
    provider_name = fields.Char(string="Grupo", readonly=True)
    suite_scope = fields.Char(string="Filtro tecnico", readonly=True)
    scope_label = fields.Char(string="Filtro", readonly=True)
    state = fields.Selection(
        selection=[
            ("success", "Exitoso"),
            ("error", "Con fallos"),
            ("partial", "Detenido"),
        ],
        string="Estado ejecución",
        readonly=True,
    )
    started_at = fields.Datetime(string="Inicio", readonly=True)
    finished_at = fields.Datetime(string="Fin", readonly=True)
    ok_count = fields.Integer(string="Correctas", readonly=True)
    controlled_count = fields.Integer(string="Controladas", readonly=True)
    failed_count = fields.Integer(string="Fallidas", readonly=True)
    skipped_count = fields.Integer(string="Omitidas", readonly=True)
    total_count = fields.Integer(string="Total", readonly=True)
    test_catalog = fields.Text(string="Pruebas ejecutadas", readonly=True)
    line_ids = fields.One2many(
        comodel_name="zue.testing.dashboard.run.line",
        inverse_name="run_id",
        string="Resultados",
        readonly=True,
    )


class ZueTestingDashboardRunLine(models.TransientModel):
    _name = "zue.testing.dashboard.run.line"
    _description = "Linea de historial del panel de pruebas ZUE"
    _order = "sequence, id"
    _transient_max_hours = 24.0

    run_id = fields.Many2one(
        comodel_name="zue.testing.dashboard.run",
        string="Ejecución",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    sequence = fields.Integer(string="Secuencia", readonly=True)
    provider_model = fields.Char(string="Modelo proveedor", readonly=True)
    provider_name = fields.Char(string="Proveedor", readonly=True)
    technical_name = fields.Char(string="Nombre tecnico", readonly=True, index=True)
    module_name = fields.Char(string="Origen", readonly=True)
    summary = fields.Char(string="Prueba", readonly=True)
    test_type = fields.Selection(
        selection=[
            ("parametric", "Paramétrica"),
            ("process", "Proceso"),
        ],
        string="Tipo de prueba",
        readonly=True,
    )
    status = fields.Selection(
        selection=[
            ("ok", "Correcto"),
            ("controlled", "Controlado"),
            ("failed", "Fallido"),
            ("skipped", "Omitido"),
        ],
        string="Estado",
        readonly=True,
    )
    message = fields.Char(string="Mensaje", readonly=True)
    functional_log = fields.Text(string="Log funcional", readonly=True)
    detail = fields.Text(string="Detalle", readonly=True)
    test_data = fields.Text(string="Datos de prueba", readonly=True)
    calculated_lines = fields.Text(string="Conceptos calculados", readonly=True)
    worked_days_lines = fields.Text(string="Dias trabajados", readonly=True)
    not_applied_lines = fields.Text(string="Reglas no aplicadas", readonly=True)
    obtained_info = fields.Text(string="Informacion del recibo", readonly=True)
    result_payload = fields.Text(string="Resultado de proceso", readonly=True)
    duration = fields.Float(string="Segundos", digits=(12, 3), readonly=True)
