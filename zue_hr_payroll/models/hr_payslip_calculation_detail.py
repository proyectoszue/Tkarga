# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.tools.misc import format_date
from odoo.tools.translate import LazyTranslate
from markupsafe import Markup, escape

_lt = LazyTranslate(__name__)

_SKIP_KEYS = frozenset({
    'result', 'result_qty', 'result_rate', 'result_base',
    'result_calculation_components', 'result_calculation_formula',
    'categories', 'rules', 'payslip', 'worked_days', 'inputs',
    'employee', 'version', 'contract', 'annual_parameters',
    'rules_computed', 'localdict', 'id_version_concepts',
    'values_leaves_all', 'values_leaves_law', 'leaves',
    'inherit_contrato', 'inherit_contrato_dev', 'inherit_contrato_ded',
    'inherit_contrato_ded_bases', 'inherit_prima', 'inherit_vacation',
    'inherit_nomina', 'round_payroll',
})

_VARIABLE_LABELS = {
    'dias': _lt('Días'),
    'auxtransporte': _lt('Auxilio de transporte mensual'),
    'auxtransporte_tope': _lt('Tope auxilio de transporte'),
    'aplicar': _lt('Día de cobro (aplicar)'),
    'total': _lt('Devengado salarial para tope'),
    'liquidated_aux_transport': _lt('Liquida auxilio (parametrización)'),
    'day_initial_payrroll': _lt('Día inicio periodo'),
    'day_end_payrroll': _lt('Día fin periodo'),
    'valor_dia': _lt('Valor día'),
    'already_paid': _lt('Ya liquidado'),
    'wage': _lt('Salario'),
    'obj_salary_rule': _lt('Regla salarial'),
    'liquidate_employee_pension': _lt('Liquida pensión empleado'),
    'total_salarial': _lt('Total salarial'),
    'total_no_salarial': _lt('Total no salarial'),
    'gran_total': _lt('Gran total'),
    'top_twenty_five_smmlv': _lt('Tope 25 SMMLV'),
    'statute_value': _lt('Valor estatuto'),
    'total_statute': _lt('Total estatuto'),
    'value_difference': _lt('Diferencia'),
    'value_difference_day': _lt('Diferencia diaria'),
    'value_difference_day_statute': _lt('Diferencia diaria estatuto'),
    'dias_work': _lt('Días trabajados'),
    'dias_work_act': _lt('Días trabajados del periodo'),
    'salario_minimo': _lt('Salario mínimo'),
    'pension_primera_quincena': _lt('Pensión primera quincena'),
}

# Variables / flags que no aportan al resumen funcional del popover.
_SUMMARY_SKIP_VARIABLES = frozenset({
    'liquidate_employee_pension', 'liquidated_aux_transport', 'aplicar',
    'obj_salary_rule', 'day_initial_payrroll', 'day_end_payrroll',
})


def guess_assignment_format(key, value):
    key_l = (key or '').lower()
    if key_l in ('aplicar', 'day_initial_payrroll', 'day_end_payrroll'):
        return 'number'
    if 'dias' in key_l or key_l.endswith('_days') or key_l in ('days', 'day'):
        return 'days'
    if any(token in key_l for token in (
        'aux', 'wage', 'tope', 'total', 'amount', 'valor', 'base', 'salario', 'ibc',
    )):
        return 'money'
    if abs(value) <= 100 and abs(value - round(value)) < 0.0001:
        return 'number'
    return 'money'


def snapshot_localdict_scalars(localdict):
    """Copia superficial de claves escalares presentes antes de ejecutar la regla."""
    snap = {}
    for key, value in localdict.items():
        if isinstance(value, bool):
            snap[key] = value
        elif isinstance(value, (int, float)):
            snap[key] = float(value)
    return snap


def extract_rule_assignments(localdict, before_snapshot):
    """Variables numéricas nuevas o cambiadas tras _compute_rule (última asignación)."""
    assignments = {}
    for key, value in list(localdict.items()):
        if not isinstance(key, str) or key.startswith('_') or key in _SKIP_KEYS:
            continue
        if isinstance(value, bool):
            numeric = 1.0 if value else 0.0
            fmt = 'number'
        elif isinstance(value, (int, float)):
            numeric = float(value)
            fmt = guess_assignment_format(key, numeric)
        else:
            continue
        if key in before_snapshot and before_snapshot[key] == (value if isinstance(value, bool) else numeric):
            continue
        assignments[key] = (numeric, fmt)
    return list(assignments.items())


def cleanup_rule_temp_keys(localdict, before_keys):
    """Quita del localdict variables temporales creadas por la regla."""
    for key in list(localdict.keys()):
        if key in before_keys or key in _SKIP_KEYS:
            continue
        if not isinstance(key, str) or key.startswith('_'):
            continue
        value = localdict.get(key)
        if isinstance(value, (bool, int, float)) or value is None:
            localdict.pop(key, None)


def build_calculation_components_from_trace(assignments):
    """Convierte asignaciones trazadas en componentes del popover."""
    components = []
    for name, (value, fmt) in assignments:
        if abs(value) < 0.0001 and fmt != 'days':
            continue
        label = str(_VARIABLE_LABELS.get(name) or name.replace('_', ' ').strip())
        components.append({
            'name': label,
            'variable': name,
            'amount': value,
            'format': fmt,
            'origin': _('regla'),
            'motive': _('variables de la regla'),
        })
    return components


class ZueHrPayslipCalculationDetail(models.Model):
    _name = 'zue.hr.payslip.calculation.detail'
    _description = 'Detalle del cálculo de liquidación'
    _order = 'sequence, id'

    payslip_id = fields.Many2one('hr.payslip', string='Liquidación', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(string='Secuencia')
    code = fields.Char(string='Código')
    name = fields.Char(string='Concepto')
    amount_base = fields.Float(string='Base')
    quantity = fields.Float(string='Cantidad')
    rate = fields.Float(string='Porcentaje')
    amount = fields.Float(string='Valor')
    total = fields.Float(string='Total')
    z_system_calculated_total = fields.Float(string='Total calculado por el sistema')
    z_manual_adjustment = fields.Boolean(string='Ajuste manual')
    z_summary = fields.Html(string='Resumen', sanitize=False)
    detail = fields.Html(string='Desglose técnico', sanitize=False)


class HrPayslipLineCalculationDetail(models.Model):
    _inherit = 'hr.payslip.line'

    z_calculation_base_components = fields.Json(string='Componentes de la base')
    z_system_calculated_total = fields.Float(string='Total calculado por el sistema')
    z_manual_adjustment = fields.Boolean(string='Ajuste manual')
    z_calculation_detail = fields.Html(string='Cómo se calculó', compute='_compute_z_calculation_detail', sanitize=False)

    @api.depends('sequence', 'name', 'slip_id', 'slip_id.z_calculation_detail_ids', 'slip_id.z_calculation_detail_ids.sequence',
                 'slip_id.z_calculation_detail_ids.name', 'slip_id.z_calculation_detail_ids.z_summary')
    def _compute_z_calculation_detail(self):
        for line in self:
            detail = line.slip_id.z_calculation_detail_ids.filtered(lambda d: d.sequence == line.sequence and d.name == line.name)[:1]
            line.z_calculation_detail = detail.z_summary if detail else False


class HrPayslipCalculationDetail(models.Model):
    _inherit = 'hr.payslip'

    z_calculation_detail_ids = fields.One2many('zue.hr.payslip.calculation.detail', 'payslip_id', string='Detalle del cálculo')
    z_show_calculation_detail = fields.Boolean(string='Mostrar detalle del cálculo', compute='_compute_z_show_calculation_detail')
    z_has_calculation_detail = fields.Boolean(string='Tiene detalle del cálculo', compute='_compute_z_has_calculation_detail')

    def isCalculationDetailEnabled(self):
        return self.env['ir.config_parameter'].sudo().get_param('zue_hr_payroll.z_show_payslip_calculation_detail') in ('True', 'true', '1')

    @api.depends_context('company')
    def _compute_z_show_calculation_detail(self):
        enabled = self.isCalculationDetailEnabled()
        for payslip in self:
            payslip.z_show_calculation_detail = enabled

    @api.depends('z_calculation_detail_ids')
    def _compute_z_has_calculation_detail(self):
        for payslip in self:
            payslip.z_has_calculation_detail = bool(payslip.z_calculation_detail_ids)

    def compute_sheet(self):
        res = super().compute_sheet()
        self.syncCalculationDetailAfterCompute()
        return res

    def syncCalculationDetailAfterCompute(self):
        """Marca totales de sistema y regenera el detalle visual (no altera el cálculo)."""
        enabled = self.isCalculationDetailEnabled()
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'validated']):
            payslip.z_calculation_detail_ids.unlink()
            if not enabled:
                continue
            for line in payslip.line_ids:
                line.z_system_calculated_total = line.total or 0.0
                line.z_manual_adjustment = False
            payslip.rebuild_calculation_details()

    def restart_payroll(self):
        self.mapped('z_calculation_detail_ids').unlink()
        return super().restart_payroll()

    def action_edit_payslip_lines(self):
        action = super().action_edit_payslip_lines()
        wizard = self.env['hr.payroll.edit.payslip.lines.wizard'].browse(action['res_id'])
        for wizard_line, payslip_line in zip(wizard.line_ids, self.line_ids):
            wizard_line.write({
                'z_origin_payslip_line_id': payslip_line.id,
                'z_origin_total': payslip_line.total,
                'z_system_calculated_total': payslip_line.z_system_calculated_total or payslip_line.total,
                'z_manual_adjustment': False,
                'z_calculation_base_components': payslip_line.z_calculation_base_components,
            })
        return action

    def compute_salary_rule_amount(self, rule, localdict):
        """Misma firma que rule._compute_rule; guarda el detalle visual en localdict."""
        amount, qty, rate, detail = self.compute_salary_rule_with_trace(rule, localdict)
        localdict['_zue_rule_calculation_detail'] = detail or {}
        return amount, qty, rate

    def take_rule_calculation_detail(self, localdict):
        """Devuelve y limpia el detalle guardado por compute_salary_rule_amount."""
        return localdict.pop('_zue_rule_calculation_detail', None) or {}

    def format_calculation_amount(self, amount):
        """Monto es_CO sin decimales: $2.049.095 / -$X"""
        self.ensure_one()
        value = int(float_round(amount or 0.0, precision_digits=0))
        sign = '-' if value < 0 else ''
        grouped = '{:,}'.format(abs(value)).replace(',', '.')
        return '%s$%s' % (sign, grouped)

    def format_calculation_rate(self, rate):
        if abs((rate or 0.0) - round(rate or 0.0)) < 0.0001:
            return '%d%%' % int(round(rate or 0.0))
        return '%g%%' % (rate or 0.0)

    def format_calculation_quantity(self, qty):
        if abs((qty or 0.0) - round(qty or 0.0)) < 0.0001:
            return '%d' % int(round(qty or 0.0))
        return '%g' % (qty or 0.0)

    def format_calculation_component_amount(self, component):
        """Monto de componente: dinero por defecto; días/número sin símbolo $."""
        amount = component.get('amount') or 0.0
        fmt = component.get('format') or 'money'
        if fmt == 'days':
            qty = self.format_calculation_quantity(amount)
            return _('%s días') % qty
        if fmt in ('number', 'qty', 'quantity'):
            return self.format_calculation_quantity(amount)
        return self.format_calculation_amount(amount)

    def pop_rule_calculation_detail(self, localdict):
        """Extrae del localdict detalle explícito (si alguna regla lo dejó; no requerido)."""
        components = localdict.pop('result_calculation_components', None)
        amount_base = localdict.pop('result_base', None)
        formula = localdict.pop('result_calculation_formula', None)
        detail = {}
        comps = list(components) if components else []
        if formula:
            comps.append({
                'format': 'formula',
                'operation': formula,
                'amount': 0.0,
            })
        if comps:
            detail['z_calculation_base_components'] = comps
        if amount_base is not None:
            detail['amount_base'] = amount_base
        return detail

    def compute_salary_rule_with_trace(self, rule, localdict):
        """Ejecuta la regla y desglosa variables numéricas intermedias (solo visual)."""
        before_keys = set(localdict.keys())
        before_snapshot = snapshot_localdict_scalars(localdict)
        amount, qty, rate = rule._compute_rule(localdict)
        assignments = extract_rule_assignments(localdict, before_snapshot)
        detail = self.pop_rule_calculation_detail(localdict)
        cleanup_rule_temp_keys(localdict, before_keys)
        if not detail.get('z_calculation_base_components'):
            components = build_calculation_components_from_trace(assignments)
            if components:
                detail['z_calculation_base_components'] = components
        return amount, qty, rate, detail

    def format_calculation_date(self, value):
        if not value:
            return ''
        if isinstance(value, str):
            try:
                value = fields.Date.to_date(value)
            except (ValueError, TypeError):
                return value
        return format_date(self.env, value)

    def format_calculation_period(self, date_from, date_to):
        self.ensure_one()
        start = self.format_calculation_date(date_from)
        end = self.format_calculation_date(date_to)
        if start and end:
            return _('del %s al %s') % (start, end)
        return start or end or ''

    def build_calculation_formula(self, line, base, uses_percent):
        money = self.format_calculation_amount
        rate_txt = self.format_calculation_rate
        qty_txt = self.format_calculation_quantity
        code = line.code or ''
        qty = line.quantity or 0.0
        rate = line.rate or 100.0
        amount = line.amount or 0.0
        qty_is_one = abs(qty - 1.0) < 0.0001

        if code == 'TOTALDEV':
            return _('Suma de conceptos de devengo')
        if code == 'TOTALDED':
            return _('Suma de conceptos de deducción')
        if code == 'NET':
            return _('Total de devengos + Total de deducciones')
        if code == 'INTCESANTIAS' and uses_percent:
            return _('%(amount)s × %(qty)s días × %(rate)s') % {
                'amount': money(amount),
                'qty': qty_txt(qty),
                'rate': rate_txt(rate),
            }
        if code in ('CESANTIAS', 'PRIMA', 'VACCONTRATO', 'VACDISFRUTADAS', 'VACREMUNERADAS'):
            return _('%(amount)s × %(qty)s días') % {
                'amount': money(amount),
                'qty': qty_txt(qty),
            }
        if uses_percent and base and qty_is_one:
            return _('%(base)s × %(rate)s') % {
                'base': money(base),
                'rate': rate_txt(rate),
            }
        if uses_percent and qty_is_one:
            return _('%(amount)s × %(rate)s') % {
                'amount': money(amount),
                'rate': rate_txt(rate),
            }
        if uses_percent:
            return _('%(amount)s × %(qty)s × %(rate)s') % {
                'amount': money(amount),
                'qty': qty_txt(qty),
                'rate': rate_txt(rate),
            }
        if qty_is_one:
            return money(amount)
        return _('%(amount)s × %(qty)s') % {
            'amount': money(amount),
            'qty': qty_txt(qty),
        }

    def index_calculation_components_by_variable(self, components):
        by_var = {}
        for component in components or []:
            variable = component.get('variable') or ''
            if not variable:
                motive = component.get('motive') or ''
                if '«' in motive and '»' in motive:
                    variable = motive.split('«', 1)[1].split('»', 1)[0].strip()
            if variable:
                by_var[variable] = component
        return by_var

    def calculation_formula_matches_total(self, value, total):
        if value is None or total is None:
            return False
        return abs(round(value, 0) - round(total, 0)) <= 1 or abs((value or 0.0) - (total or 0.0)) <= 1.0

    def build_calculation_total_formula_with_values(
        self, line, components, base, uses_percent, formula_override=None
    ):
        """Fórmula del Total con valores reales; aplica a todas las reglas (solo visual)."""
        if formula_override:
            return formula_override
        money = self.format_calculation_amount
        qty_txt = self.format_calculation_quantity
        rate_txt = self.format_calculation_rate
        code = line.code or ''
        qty = line.quantity or 0.0
        rate = line.rate or 100.0
        amount = line.amount or 0.0
        total = line.total or 0.0
        target = total if abs(total) > 0.0001 else amount
        by_var = self.index_calculation_components_by_variable(components)
        days_comps = [
            c for c in (components or [])
            if (c.get('format') or '') == 'days' and abs(c.get('amount') or 0.0) > 0.0001
        ]
        money_comps = [
            c for c in (components or [])
            if (c.get('format') or 'money') == 'money' and abs(c.get('amount') or 0.0) > 0.0001
        ]

        dias = by_var.get('dias')
        aux = by_var.get('auxtransporte')
        already = by_var.get('already_paid')
        if dias and aux:
            days_v = dias.get('amount') or 0.0
            aux_v = aux.get('amount') or 0.0
            paid_v = abs(already.get('amount') or 0.0) if already else 0.0
            computed = round(days_v * aux_v / 30) - paid_v
            if self.calculation_formula_matches_total(computed, target):
                days = qty_txt(days_v)
                aux_txt = money(aux_v)
                if paid_v > 0.0001:
                    return _('round(%(days)s × %(aux)s / 30) − %(paid)s') % {
                        'days': days, 'aux': aux_txt, 'paid': money(paid_v),
                    }
                return _('round(%(days)s × %(aux)s / 30)') % {'days': days, 'aux': aux_txt}
        valor_dia = by_var.get('valor_dia')
        if dias and valor_dia:
            days_v = dias.get('amount') or 0.0
            day_v = valor_dia.get('amount') or 0.0
            if self.calculation_formula_matches_total(days_v * day_v, target) or self.calculation_formula_matches_total(round(days_v * day_v), target):
                return _('%(days)s × %(day_value)s') % {
                    'days': qty_txt(days_v),
                    'day_value': money(day_v),
                }

        for day_comp in days_comps:
            days_v = day_comp.get('amount') or 0.0
            days_lbl = qty_txt(days_v)
            for money_comp in money_comps:
                money_v = money_comp.get('amount') or 0.0
                money_lbl = money(money_v)
                for divisor, label in ((30, '30'), (360, '360'), (720, '720')):
                    computed = round(days_v * money_v / divisor) if divisor else 0.0
                    if self.calculation_formula_matches_total(computed, target):
                        return _('round(%(days)s × %(value)s / %(div)s)') % {
                            'days': days_lbl, 'value': money_lbl, 'div': label,
                        }
                if self.calculation_formula_matches_total(days_v * money_v, target):
                    return _('%(days)s × %(value)s') % {'days': days_lbl, 'value': money_lbl}

        if base:
            if code in ('CESANTIAS', 'PRIMA', 'INTCESANTIAS') and qty:
                day_value = round(base / 360.0, 0)
                if self.calculation_formula_matches_total(day_value, amount) or abs(qty - 1.0) > 0.0001:
                    if uses_percent:
                        return _('%(base)s ÷ 360 × %(qty)s días × %(rate)s') % {
                            'base': money(base), 'qty': qty_txt(qty), 'rate': rate_txt(rate),
                        }
                    return _('%(base)s ÷ 360 × %(qty)s días') % {
                        'base': money(base), 'qty': qty_txt(qty),
                    }
            if code in ('VACCONTRATO', 'VACDISFRUTADAS', 'VACREMUNERADAS') and qty:
                return _('%(base)s ÷ 720 × %(qty)s días') % {
                    'base': money(base), 'qty': qty_txt(qty),
                }

        if uses_percent:
            if base and self.calculation_formula_matches_total(base * rate / 100.0, target):
                return _('%(base)s × %(rate)s') % {'base': money(base), 'rate': rate_txt(rate)}
            for money_comp in money_comps:
                money_v = money_comp.get('amount') or 0.0
                if self.calculation_formula_matches_total(money_v * rate / 100.0, target):
                    return _('%(value)s × %(rate)s') % {
                        'value': money(money_v), 'rate': rate_txt(rate),
                    }
            if abs(qty - 1.0) > 0.0001:
                return _('%(amount)s × %(qty)s × %(rate)s') % {
                    'amount': money(amount), 'qty': qty_txt(qty), 'rate': rate_txt(rate),
                }
            return _('%(amount)s × %(rate)s') % {'amount': money(amount), 'rate': rate_txt(rate)}

        if abs(qty - 1.0) > 0.0001:
            return _('%(amount)s × %(qty)s') % {'amount': money(amount), 'qty': qty_txt(qty)}

        matching_money = [
            c for c in money_comps
            if self.calculation_formula_matches_total(c.get('amount') or 0.0, target)
        ]
        if len(matching_money) == 1:
            return money(matching_money[0].get('amount') or 0.0)

        if days_comps and money_comps:
            day_comp = days_comps[0]
            money_comp = money_comps[0]
            days_v = day_comp.get('amount') or 0.0
            money_v = money_comp.get('amount') or 0.0
            if abs(money_v) > 0.0001 and abs((target / money_v) - days_v) <= 0.05:
                return _('%(days)s × %(value)s') % {
                    'days': qty_txt(days_v), 'value': money(money_v),
                }
            if abs(days_v) > 0.0001:
                day_value = target / days_v
                if abs(day_value) >= 1:
                    return _('%(days)s × %(value)s') % {
                        'days': qty_txt(days_v), 'value': money(day_value),
                    }

        return self.build_calculation_formula(line, base, uses_percent)

    def build_calculation_component_meta_lines(self, component, skip_origin=False, skip_motive=False):
        """Líneas ORIGEN / PERIODO / MOTIVO / extras, cada una en su renglón."""
        lines = []
        origin = component.get('origin') or ''
        motive = component.get('motive') or component.get('note') or ''
        period = self.format_calculation_period(
            component.get('period_from'), component.get('period_to')
        )
        if origin and not skip_origin:
            lines.append((_('ORIGEN'), origin))
        if period:
            lines.append((_('PERIODO'), period))
        if motive and not skip_motive:
            lines.append((_('MOTIVO'), motive))
        for key, label in (
            ('detail', _('DETALLE')),
            ('operation', _('OPERACIÓN')),
            ('condition', _('CONDICIÓN')),
        ):
            extra = component.get(key)
            if extra:
                lines.append((label, extra))
        return lines

    def build_calculation_component_meta_html(self, component, skip_origin=False, skip_motive=False):
        lines = self.build_calculation_component_meta_lines(
            component, skip_origin=skip_origin, skip_motive=skip_motive
        )
        if not lines:
            return ''
        return ''.join(
            '<div class="text-muted small">%s: %s</div>' % (escape(label), escape(value))
            for label, value in lines
        )

    def build_shared_calculation_rule_meta_html(self, components):
        """ORIGEN + MOTIVO únicos bajo 'Cálculo de la regla' (no repetir por variable)."""
        origins = []
        for component in components:
            origin = (component.get('origin') or '').strip()
            if origin and origin not in origins:
                origins.append(origin)
        if len(origins) != 1:
            return '', False
        return (
            '<div class="text-muted small mb-2">'
            '<div>%s: %s</div>'
            '<div>%s: %s</div>'
            '</div>' % (
                escape(_('ORIGEN')),
                escape(origins[0]),
                escape(_('MOTIVO')),
                escape(_('variables de la regla')),
            ),
            True,
        )

    def get_calculation_presentation_context(self, line):
        """Datos comunes para resumen funcional y desglose técnico."""
        self.ensure_one()
        code = line.code or ''
        category_code = line.category_id.code if line.category_id else ''
        qty = line.quantity or 0.0
        rate = line.rate or 100.0
        amount = line.amount or 0.0
        total = line.total or 0.0
        base = line.amount_base or 0.0
        raw_components = line.z_calculation_base_components or []
        formula_override = None
        components = []
        for component in raw_components:
            if (component.get('format') or '') == 'formula':
                formula_override = component.get('operation') or component.get('motive') or formula_override
                continue
            components.append(component)
        uses_percent = abs(rate - 100.0) > 0.0001
        if not base and uses_percent and abs(qty - 1.0) < 0.0001:
            expected = amount * rate / 100.0
            if abs(total - expected) <= 1.0 or abs(total - round(expected)) <= 1.0:
                base = amount
        divisor = False
        if base:
            if code in ('CESANTIAS', 'PRIMA', 'INTCESANTIAS'):
                divisor = 360
            elif code in ('VACCONTRATO', 'VACDISFRUTADAS', 'VACREMUNERADAS'):
                divisor = 720
        formula = self.build_calculation_total_formula_with_values(
            line, components, base, uses_percent, formula_override=formula_override
        )
        return {
            'code': code,
            'category_code': category_code,
            'qty': qty,
            'rate': rate,
            'amount': amount,
            'total': total,
            'base': base,
            'components': components,
            'uses_percent': uses_percent,
            'divisor': divisor,
            'show_day_value': bool(
                base and divisor and abs(round(base / divisor, 0) - round(amount, 0)) <= 1
            ),
            'formula': formula,
            'by_var': self.index_calculation_components_by_variable(components),
        }

    def is_calculation_flag_component(self, component):
        fmt = component.get('format') or 'money'
        amount = component.get('amount') or 0.0
        variable = (component.get('variable') or '').strip()
        if variable in _SUMMARY_SKIP_VARIABLES:
            return True
        if fmt in ('number', 'qty', 'quantity') and abs(amount) in (0.0, 1.0):
            name = (component.get('name') or variable or '').lower()
            if any(token in name for token in ('liquida', 'aplica', 'flag', 'parametr')):
                return True
        return False

    def find_calculation_component(self, ctx, variables=(), name_tokens=(), formats=()):
        """Busca un componente por variable, texto del nombre o formato."""
        by_var = ctx['by_var']
        for variable in variables:
            comp = by_var.get(variable)
            if comp:
                return comp
        for component in ctx['components']:
            if self.is_calculation_flag_component(component):
                continue
            fmt = component.get('format') or 'money'
            if formats and fmt not in formats:
                continue
            name = '%s %s' % (component.get('variable') or '', component.get('name') or '')
            name_l = name.lower().replace('_', ' ')
            if name_tokens and any(token in name_l for token in name_tokens):
                return component
            if formats and fmt in formats and abs(component.get('amount') or 0.0) > 0.0001:
                return component
        return False

    def is_calculation_application_component(self, component):
        """Componentes del prorrateo/ajuste final, no de la formación de la base."""
        if self.is_calculation_flag_component(component):
            return True
        fmt = component.get('format') or 'money'
        if fmt == 'days':
            return True
        name = '%s %s' % (component.get('variable') or '', component.get('name') or '')
        name_l = name.lower().replace('_', ' ')
        return any(token in name_l for token in (
            'already', 'ya pag', 'ya liquid', 'primera quincena',
            'valor dia', 'valor día', 'difference day',
            'dias work', 'días', 'dias ',
        ))

    def is_calculation_rich_base_component(self, component):
        """Tiene origen/motivo/periodo útiles para explicar la base."""
        motive = (component.get('motive') or '').strip().lower()
        origin = (component.get('origin') or '').strip().lower()
        if component.get('period_from') or component.get('period_to'):
            return True
        if motive and 'variables de la regla' not in motive:
            return True
        if origin and origin not in ('regla', 'rule'):
            return True
        return False

    def pick_calculation_base_components(self, ctx):
        """Componentes que explican cómo se forma la base."""
        base = ctx['base'] or 0.0
        if not base:
            return []
        candidates = []
        for component in ctx['components']:
            if self.is_calculation_application_component(component):
                continue
            amount = component.get('amount') or 0.0
            if abs(amount) < 0.0001:
                continue
            fmt = component.get('format') or 'money'
            if fmt in ('number', 'qty', 'quantity') and abs(amount) <= 100:
                continue
            candidates.append(component)
        if not candidates:
            return []
        rich = [c for c in candidates if self.is_calculation_rich_base_component(c)]
        if rich:
            return rich[:8]
        matching = [
            c for c in candidates
            if self.calculation_formula_matches_total(c.get('amount') or 0.0, base)
        ]
        if matching:
            return matching[:4]
        preferred_vars = (
            'wage', 'total', 'total_salarial', 'total_no_salarial', 'gran_total',
            'statute_value', 'total_statute', 'top_twenty_five_smmlv', 'salario_minimo',
        )
        by_var = ctx['by_var']
        preferred = [by_var[name] for name in preferred_vars if name in by_var]
        preferred = [
            c for c in preferred
            if c in candidates and abs(c.get('amount') or 0.0) > 0.0001
        ]
        if preferred:
            return preferred[:6]
        return candidates[:6]

    def build_calculation_base_narrative_steps(self, line, ctx, base_components):
        """Explica primero de dónde sale la base."""
        money = self.format_calculation_amount
        base = ctx['base'] or 0.0
        if not base:
            return []
        base_label = _('base de cotización (IBC)') if ctx['category_code'] == 'SSOCIAL' else _('base')
        if not base_components:
            return [_('La %(base)s del concepto es %(amount)s.') % {
                'base': base_label,
                'amount': money(base),
            }]

        origins = []
        for component in base_components:
            origin = (component.get('origin') or '').strip()
            if origin and origin not in origins:
                origins.append(origin)

        if len(base_components) == 1:
            comp = base_components[0]
            name = (comp.get('name') or '').strip() or _('valor de referencia')
            period = self.format_calculation_period(comp.get('period_from'), comp.get('period_to'))
            amount_txt = self.format_calculation_component_amount(comp)
            if period:
                return [_('La %(base)s se obtiene de %(name)s (%(amount)s) %(period)s.') % {
                    'base': base_label,
                    'name': name,
                    'amount': amount_txt,
                    'period': period,
                }]
            return [_('La %(base)s se obtiene de %(name)s: %(amount)s.') % {
                'base': base_label,
                'name': name,
                'amount': amount_txt,
            }]

        if origins and not all(o.lower() in ('regla', 'rule') for o in origins):
            return [_('La %(base)s (%(amount)s) se arma con: %(origins)s.') % {
                'base': base_label,
                'amount': money(base),
                'origins': ', '.join(origins),
            }]
        return [_('La %(base)s (%(amount)s) se obtiene a partir de estos valores del periodo.') % {
            'base': base_label,
            'amount': money(base),
        }]

    def pick_calculation_summary_facts(self, line, ctx, include_base=True):
        """Datos del cálculo del concepto (tarifa, días, ajustes)."""
        money = self.format_calculation_amount
        qty_txt = self.format_calculation_quantity
        rate_txt = self.format_calculation_rate
        facts = []
        seen = set()

        def add_fact(label, value):
            key = (label, value)
            if key in seen or not value:
                return
            seen.add(key)
            facts.append((label, value))

        if include_base and ctx['base']:
            label = _('Base / IBC') if ctx['category_code'] == 'SSOCIAL' else _('Base')
            add_fact(label, money(ctx['base']))
        if ctx['uses_percent']:
            add_fact(_('Tarifa'), rate_txt(ctx['rate']))

        days_comp = self.find_calculation_component(
            ctx,
            variables=('dias', 'dias_work', 'dias_work_act'),
            name_tokens=('dias work', 'días', 'dias'),
            formats=('days',),
        )
        if days_comp:
            add_fact(_('Días'), self.format_calculation_component_amount(days_comp))
        elif abs(ctx['qty'] - 1.0) > 0.0001:
            add_fact(_('Cantidad'), qty_txt(ctx['qty']))

        valor_dia = self.find_calculation_component(
            ctx,
            variables=('valor_dia', 'value_difference_day'),
            name_tokens=('valor dia', 'valor día', 'difference day'),
        )
        if valor_dia:
            add_fact(_('Valor día'), self.format_calculation_component_amount(valor_dia))

        already = self.find_calculation_component(
            ctx,
            variables=('already_paid', 'pension_primera_quincena'),
            name_tokens=('ya pag', 'ya liquid', 'primera quincena'),
        )
        if already and abs(already.get('amount') or 0.0) > 0.0001:
            add_fact(_('Ya liquidado'), self.format_calculation_component_amount(already))

        if not ctx['base']:
            for variables, tokens, label in (
                (('total',), ('devengado salarial',), _('Devengado salarial')),
                (('total_salarial',), ('total salarial',), _('Total salarial')),
                (('gran_total',), ('gran total',), _('Gran total')),
                (('wage',), ('salario',), _('Salario')),
            ):
                comp = self.find_calculation_component(ctx, variables=variables, name_tokens=tokens)
                if comp and abs(comp.get('amount') or 0.0) > 0.0001:
                    add_fact(label, self.format_calculation_component_amount(comp))
                    break

        return facts[:6]

    def build_calculation_concept_narrative_steps(self, line, ctx):
        """Pasos del cálculo del concepto (después de conocer la base)."""
        money = self.format_calculation_amount
        rate_txt = self.format_calculation_rate
        qty_txt = self.format_calculation_quantity
        code = ctx['code']
        steps = []

        if code == 'TOTALDEV':
            return [_('Se suman los conceptos de devengo de la liquidación.')]
        if code == 'TOTALDED':
            return [_('Se suman los conceptos de deducción de la liquidación.')]
        if code == 'NET':
            return [_('Se obtiene el neto sumando el total de devengos y el total de deducciones.')]

        if not ctx['base']:
            if line.loan_id:
                steps.append(_('Se toma el valor desde el préstamo asociado.'))
            elif line.entity_id:
                steps.append(_('Se toma el valor desde la entidad %s.') % line.entity_id.display_name)
            else:
                steps.append(_('Se calcula el valor según la regla del concepto.'))

        if ctx['uses_percent']:
            if ctx['base']:
                steps.append(
                    _('Sobre esa base se aplica la tarifa del %s.') % rate_txt(ctx['rate'])
                )
            else:
                steps.append(_('Se aplica la tarifa del %s.') % rate_txt(ctx['rate']))

        days_comp = self.find_calculation_component(
            ctx,
            variables=('dias', 'dias_work', 'dias_work_act'),
            name_tokens=('dias work', 'días', 'dias'),
            formats=('days',),
        )
        already = self.find_calculation_component(
            ctx,
            variables=('already_paid', 'pension_primera_quincena'),
            name_tokens=('ya pag', 'ya liquid', 'primera quincena'),
        )
        already_amount = abs(already.get('amount') or 0.0) if already else 0.0
        if days_comp and already_amount > 0.0001:
            steps.append(
                _('Se prorratea por %s y se descuenta lo ya liquidado (%s).') % (
                    self.format_calculation_component_amount(days_comp),
                    self.format_calculation_component_amount(already),
                )
            )
        elif days_comp:
            steps.append(
                _('Se prorratea según %s del periodo.') % (
                    self.format_calculation_component_amount(days_comp),
                )
            )
        elif already_amount > 0.0001:
            steps.append(
                _('Se descuenta lo ya liquidado: %s.') % (
                    self.format_calculation_component_amount(already),
                )
            )
        elif ctx['show_day_value']:
            steps.append(
                _('Se obtiene el valor día (%s ÷ %s) y se aplica al periodo.') % (
                    money(ctx['base']), ctx['divisor'],
                )
            )
        elif abs(ctx['qty'] - 1.0) > 0.0001:
            steps.append(_('Se multiplica por la cantidad del periodo: %s.') % qty_txt(ctx['qty']))

        return steps[:3]

    def build_calculation_base_section_html(self, line, ctx, base_components):
        """Bloque inicial: cómo se obtiene la base."""
        if not ctx['base']:
            return ''
        money = self.format_calculation_amount
        base_label = _('Base / IBC') if ctx['category_code'] == 'SSOCIAL' else _('Base')
        parts = [
            '<div class="mb-2"><strong>%s</strong></div>' % escape(_('Cómo se obtiene la base')),
        ]
        steps = self.build_calculation_base_narrative_steps(line, ctx, base_components)
        if steps:
            parts.append('<ol class="mb-2 ps-3">')
            for step in steps:
                parts.append('<li class="mb-1">%s</li>' % escape(step))
            parts.append('</ol>')
        if base_components:
            parts.append('<ul class="mb-2 ps-3">')
            for component in base_components:
                meta_html = self.build_calculation_component_meta_html(component)
                parts.append(
                    '<li class="mb-1">'
                    '<div>%s: %s</div>'
                    '%s'
                    '</li>' % (
                        escape(component.get('name') or ''),
                        escape(self.format_calculation_component_amount(component)),
                        meta_html,
                    )
                )
            parts.append('</ul>')
        parts.append(
            '<div class="mb-3"><strong>%s:</strong> %s</div>' % (
                escape(base_label), escape(money(ctx['base'])),
            )
        )
        return ''.join(parts)

    def build_calculation_manual_note_html(self, line, total):
        if not line.z_manual_adjustment:
            return ''
        money = self.format_calculation_amount
        system_total = line.z_system_calculated_total
        if (line.code or '') in ('TOTALDEV', 'TOTALDED', 'NET'):
            note_title = _('Total actualizado por un ajuste manual en otra línea.')
        else:
            note_title = _('Se realizó un ajuste manual.')
        return (
            '<div class="o_zue_calc_manual alert alert-warning py-1 px-2 mb-2 small">'
            '<div class="fw-bold">%s</div>'
            '<div>%s: %s</div>'
            '<div>%s: %s</div>'
            '</div>'
        ) % (
            escape(note_title),
            escape(_('Valor calculado por el sistema')),
            escape(money(system_total)),
            escape(_('Valor en la liquidación')),
            escape(money(total)),
        )

    def build_calculation_header_html(self, line, total):
        money = self.format_calculation_amount
        return (
            '<table class="table table-sm table-borderless mb-2 w-100">'
            '<tr class="border-bottom">'
            '<td class="fw-normal text-start pe-2">%s</td>'
            '<td class="fw-bold text-end text-nowrap">%s</td>'
            '</tr>'
            '</table>'
        ) % (escape(line.name or ''), escape(money(total)))

    def build_calculation_summary_html(self, line):
        """Popover: primero la base (si existe), luego el cálculo del concepto."""
        self.ensure_one()
        ctx = self.get_calculation_presentation_context(line)
        money = self.format_calculation_amount
        base_components = self.pick_calculation_base_components(ctx)
        concept_steps = self.build_calculation_concept_narrative_steps(line, ctx)
        facts = self.pick_calculation_summary_facts(line, ctx, include_base=False)
        body = [self.build_calculation_base_section_html(line, ctx, base_components)]
        if concept_steps:
            title = _('Cómo se calcula el concepto') if ctx['base'] else _('Cómo se calculó')
            body.append('<div class="mb-2"><strong>%s</strong></div>' % escape(title))
            body.append('<ol class="mb-2 ps-3">')
            for step in concept_steps:
                body.append('<li class="mb-1">%s</li>' % escape(step))
            body.append('</ol>')
        if facts:
            body.append('<div class="mb-2"><strong>%s</strong></div>' % escape(_('Datos usados')))
            body.append('<ul class="mb-2 ps-3">')
            for label, value in facts:
                body.append(
                    '<li class="mb-1"><div>%s: %s</div></li>' % (
                        escape(label), escape(value),
                    )
                )
            body.append('</ul>')
        body.append(
            '<div class="mb-0"><strong>%s:</strong> %s = %s</div>' % (
                escape(_('Resultado')),
                escape(ctx['formula']),
                escape(money(ctx['total'])),
            )
        )
        html = (
            '<div class="o_zue_calculation_detail%s">'
            '%s%s%s'
            '</div>'
        ) % (
            ' o_zue_calc_manual' if line.z_manual_adjustment else '',
            self.build_calculation_header_html(line, ctx['total']),
            self.build_calculation_manual_note_html(line, ctx['total']),
            ''.join(body),
        )
        return Markup(html)

    def build_calculation_detail_html(self, line):
        """Grilla: desglose técnico completo de variables intermedias."""
        self.ensure_one()
        money = self.format_calculation_amount
        ctx = self.get_calculation_presentation_context(line)
        code = ctx['code']
        category_code = ctx['category_code']
        qty = ctx['qty']
        rate = ctx['rate']
        amount = ctx['amount']
        total = ctx['total']
        base = ctx['base']
        components = ctx['components']
        uses_percent = ctx['uses_percent']
        divisor = ctx['divisor']
        show_day_value = ctx['show_day_value']
        formula = ctx['formula']
        show_components = bool(components)
        show_base = bool(base) and (
            show_components
            or code in ('CESANTIAS', 'PRIMA', 'INTCESANTIAS', 'VACCONTRATO', 'VACDISFRUTADAS', 'VACREMUNERADAS')
            or category_code == 'SSOCIAL'
            or uses_percent
        )

        body = []
        step = 1
        base_components = self.pick_calculation_base_components(ctx) if show_base else []
        application_components = [
            c for c in components
            if c not in base_components
        ] if show_base else components

        if show_base:
            body.append(
                '<div class="mb-2"><strong>%s. %s</strong></div>' % (
                    step, escape(_('Cómo se obtiene la base')),
                )
            )
            body.append('<ul class="mb-2 ps-3">')
            if base_components:
                for component in base_components:
                    meta_html = self.build_calculation_component_meta_html(component)
                    body.append(
                        '<li class="mb-1">'
                        '<div>%s: %s</div>'
                        '%s'
                        '</li>' % (
                            escape(component.get('name') or ''),
                            escape(self.format_calculation_component_amount(component)),
                            meta_html,
                        )
                    )
            elif category_code == 'SSOCIAL':
                body.append(
                    '<li class="mb-1">'
                    '<div>%s: %s</div>'
                    '<div class="text-muted small">%s: %s</div>'
                    '</li>' % (
                        escape(_('Salario / IBC')),
                        escape(money(base)),
                        escape(_('MOTIVO')),
                        escape(_('Base de cotización usada por la regla')),
                    )
                )
            body.append('</ul>')
            body.append(
                '<div class="mb-2"><strong>%s:</strong> %s</div>' % (
                    escape(_('Base')), escape(money(base)),
                )
            )
            step += 1

        if application_components or (show_components and not show_base):
            body.append(
                '<div class="mb-2"><strong>%s. %s</strong></div>' % (
                    step, escape(_('Cálculo de la regla')),
                )
            )
            shared_meta_html, skip_shared = self.build_shared_calculation_rule_meta_html(
                application_components or components
            )
            if shared_meta_html:
                body.append(shared_meta_html)
            body.append('<ul class="mb-2 ps-3">')
            for component in (application_components or components):
                comp_amount = component.get('amount') or 0.0
                meta_html = self.build_calculation_component_meta_html(
                    component,
                    skip_origin=skip_shared,
                    skip_motive=skip_shared,
                )
                if abs(comp_amount) < 0.0001 and not meta_html and not component.get('name'):
                    continue
                body.append(
                    '<li class="mb-1">'
                    '<div>%s: %s</div>'
                    '%s'
                    '</li>' % (
                        escape(component.get('name') or ''),
                        escape(self.format_calculation_component_amount(component)),
                        meta_html,
                    )
                )
            body.append('</ul>')
            step += 1
        elif code not in ('TOTALDEV', 'TOTALDED', 'NET') and not show_base:
            if line.loan_id:
                source = _('préstamo')
            elif line.entity_id:
                source = _('entidad %s') % line.entity_id.display_name
            elif category_code == 'SSOCIAL':
                source = _('ley')
            else:
                source = _('contrato / novedad')
            body.append(
                '<div class="mb-2"><strong>%s.</strong> %s</div>' % (
                    step,
                    escape(_('Valor tomado de %(source)s: %(amount)s') % {
                        'source': source,
                        'amount': money(amount if amount else total),
                    }),
                )
            )
            step += 1

        if show_day_value:
            body.append(
                '<div class="mb-2"><strong>%s. %s:</strong> %s ÷ %s = %s</div>' % (
                    step,
                    escape(_('Valor día')),
                    escape(money(base)),
                    divisor,
                    escape(money(amount)),
                )
            )
            step += 1

        body.append(
            '<div class="mb-0"><strong>%s. %s:</strong> %s = %s</div>' % (
                step,
                escape(_('Total')),
                escape(formula),
                escape(money(total)),
            )
        )

        html = (
            '<div class="o_zue_calculation_detail%s">'
            '%s%s'
            '<div class="text-muted small mb-2">%s</div>'
            '%s'
            '</div>'
        ) % (
            ' o_zue_calc_manual' if line.z_manual_adjustment else '',
            self.build_calculation_header_html(line, total),
            self.build_calculation_manual_note_html(line, total),
            escape(_('Desglose técnico de variables usadas por la regla')),
            ''.join(body),
        )
        return Markup(html)

    def rebuild_calculation_details(self):
        """Arma resumen (ícono) y desglose técnico (pestaña) desde las líneas."""
        Detail = self.env['zue.hr.payslip.calculation.detail']
        for payslip in self:
            payslip.z_calculation_detail_ids.unlink()
            vals_list = []
            for line in payslip.line_ids.sorted(key=lambda l: (l.sequence, l.id)):
                if not line.total and line.code not in ('TOTALDEV', 'TOTALDED', 'NET'):
                    continue
                vals_list.append({
                    'payslip_id': payslip.id,
                    'sequence': line.sequence,
                    'code': line.code,
                    'name': line.name,
                    'amount_base': line.amount_base,
                    'quantity': line.quantity,
                    'rate': line.rate,
                    'amount': line.amount,
                    'total': line.total,
                    'z_manual_adjustment': bool(line.z_manual_adjustment),
                    'z_system_calculated_total': line.z_system_calculated_total,
                    'z_summary': payslip.build_calculation_summary_html(line),
                    'detail': payslip.build_calculation_detail_html(line),
                })
            if vals_list:
                Detail.create(vals_list)


class HrPayrollEditPayslipLinesWizardCalculationDetail(models.TransientModel):
    _inherit = 'hr.payroll.edit.payslip.lines.wizard'

    def action_validate_edition(self):
        # standard Odoo version "19"
        enabled = self.env['hr.payslip'].isCalculationDetailEnabled()
        for wizard in self:
            origin_by_id = {
                line.id: line
                for line in wizard.payslip_id.line_ids
            }
            for wizard_line in wizard.line_ids:
                origin = origin_by_id.get(wizard_line.z_origin_payslip_line_id)
                if origin:
                    system_total = origin.z_system_calculated_total or origin.total
                    origin_total = origin.total
                    components = origin.z_calculation_base_components
                else:
                    system_total = wizard_line.z_system_calculated_total or wizard_line.total
                    origin_total = wizard_line.z_origin_total or wizard_line.total
                    components = wizard_line.z_calculation_base_components
                wizard_line.z_system_calculated_total = system_total
                wizard_line.z_calculation_base_components = components or False
                wizard_line.z_manual_adjustment = abs(
                    (wizard_line.total or 0.0) - (origin_total or 0.0)
                ) > 0.005
        res = super().action_validate_edition()
        if enabled:
            self.mapped('payslip_id').rebuild_calculation_details()
        else:
            self.mapped('payslip_id.z_calculation_detail_ids').unlink()
        return res


class HrPayrollEditPayslipLineCalculationDetail(models.TransientModel):
    _inherit = 'hr.payroll.edit.payslip.line'

    z_origin_payslip_line_id = fields.Integer(string='Línea origen')
    z_origin_total = fields.Float(string='Total al abrir edición')
    z_system_calculated_total = fields.Float(string='Total calculado por el sistema')
    z_manual_adjustment = fields.Boolean(string='Ajuste manual')
    z_calculation_base_components = fields.Json(string='Componentes de la base')

    def _export_to_payslip_line(self):
        lines = super()._export_to_payslip_line()
        for wizard_line, vals in zip(self, lines):
            vals.update({
                'z_system_calculated_total': wizard_line.z_system_calculated_total,
                'z_manual_adjustment': wizard_line.z_manual_adjustment,
                'z_calculation_base_components': wizard_line.z_calculation_base_components,
            })
        return lines


class ResConfigSettingsCalculationDetail(models.TransientModel):
    _inherit = 'res.config.settings'

    z_show_payslip_calculation_detail = fields.Boolean(string='Mostrar detalle del cálculo en liquidaciones', config_parameter='zue_hr_payroll.z_show_payslip_calculation_detail', default=False)
