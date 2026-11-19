# -*- coding: utf-8 -*-
"""Detalle informativo «Cómo se calculó» en provisiones (solo visual)."""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.tools.misc import format_date
from markupsafe import Markup, escape


class HrExecutingProvisionsDetailsCalculationDetail(models.Model):
    _inherit = 'hr.executing.provisions.details'

    z_calculation_base_components = fields.Json(string='Componentes de la base')
    z_show_calculation_detail = fields.Boolean(string='Mostrar detalle del cálculo', compute='_compute_z_show_calculation_detail')
    z_calculation_detail = fields.Html(string='Cómo se calculó', compute='_compute_z_calculation_detail', sanitize=False)

    def is_calculation_detail_enabled(self):
        # sudo: leer parámetro de configuración global sin depender de permisos del usuario
        return self.env['ir.config_parameter'].sudo().get_param(
            'zue_hr_social_security.z_show_provisions_calculation_detail'
        ) in ('True', 'true', '1')

    def _compute_z_show_calculation_detail(self):
        enabled = self.is_calculation_detail_enabled()
        for detail in self:
            detail.z_show_calculation_detail = enabled

    @api.depends(
        'provision', 'value_base', 'time', 'amount', 'value_payments', 'value_balance',
        'current_payable_value', 'value_wage', 'z_calculation_base_components', 'version_id',
        'executing_provisions_id', 'executing_provisions_id.year', 'executing_provisions_id.month',
        'executing_provisions_id.date_end',
    )
    def _compute_z_calculation_detail(self):
        for detail in self:
            detail.z_calculation_detail = detail.build_calculation_detail_html()

    def format_calculation_amount(self, amount):
        value = int(float_round(amount or 0.0, precision_digits=0))
        sign = '-' if value < 0 else ''
        return '%s$%s' % (sign, '{:,}'.format(abs(value)).replace(',', '.'))

    def format_calculation_quantity(self, qty):
        if abs((qty or 0.0) - round(qty or 0.0)) < 0.0001:
            return '%d' % int(round(qty or 0.0))
        return '%g' % (qty or 0.0)

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
        start = self.format_calculation_date(date_from)
        end = self.format_calculation_date(date_to)
        if start and end:
            return _('del %s al %s') % (start, end)
        return start or end or ''

    def amounts_match(self, left, right, tolerance=1.0):
        return abs((left or 0.0) - (right or 0.0)) <= tolerance

    def get_calculation_period_dates(self):
        self.ensure_one()
        parent = self.executing_provisions_id
        if parent.year and parent.month:
            date_start = datetime(parent.year, int(parent.month), 1).date()
            date_end = parent.date_end or (date_start + relativedelta(months=1) - timedelta(days=1))
            return date_start, date_end
        return False, False

    def get_previous_calculation_snapshot(self):
        self.ensure_one()
        date_start, _date_end = self.get_calculation_period_dates()
        if not date_start or not self.version_id:
            return {'payable': 0.0, 'amount': 0.0}
        previous = self.search([
            ('executing_provisions_id.state', 'in', ['done', 'accounting']),
            ('executing_provisions_id', '!=', self.executing_provisions_id.id),
            ('executing_provisions_id.date_end', '=', date_start - timedelta(days=1)),
            ('provision', '=', self.provision),
            ('version_id', '=', self.version_id.id),
        ])
        return {
            'payable': sum(previous.mapped('current_payable_value')),
            'amount': sum(previous.mapped('amount')),
        }

    def get_calculation_divisor(self):
        return 720 if self.provision == 'vacaciones' else 360

    def get_calculation_payment_codes(self):
        return {
            'vacaciones': 'VACCONTRATO, VACDISFRUTADAS, VACREMUNERADAS',
            'cesantias': 'CESANTIAS',
            'intcesantias': 'INTCESANTIAS',
            'prima': 'PRIMA',
        }.get(self.provision, '')

    def build_calculation_row_html(self, label, name_formula, value_formula, note=''):
        """Estilo modal: fórmula con nombres, valores en negrita y nota gris."""
        note_html = Markup('<div class="text-muted small">%s</div>') % escape(note) if note else ''
        value_html = Markup('<div class="fw-bold">%s</div>') % escape(value_formula) if value_formula else ''
        return Markup(
            '<tr class="border-bottom">'
            '<td class="align-top fw-bold text-start pe-3 py-2 text-nowrap">%s</td>'
            '<td class="align-top py-2">'
            '<div>%s</div>%s%s'
            '</td>'
            '</tr>'
        ) % (escape(label), escape(name_formula), value_html, note_html)

    def build_calculation_component_meta_html(self, component):
        """ORIGEN / PERIODO / MOTIVO por componente (mismo criterio que liquidaciones)."""
        lines = []
        origin = (component.get('origin') or '').strip()
        motive = (component.get('motive') or component.get('note') or '').strip()
        period = self.format_calculation_period(
            component.get('period_from'), component.get('period_to'))
        if origin:
            lines.append((_('ORIGEN'), origin))
        if period:
            lines.append((_('PERIODO'), period))
        if motive:
            lines.append((_('MOTIVO'), motive))
        if not lines:
            return ''
        return Markup('').join(
            Markup('<div class="text-muted small">%s: %s</div>') % (escape(label), escape(value))
            for label, value in lines
        )

    def build_calculation_base_row(self):
        """Cómo se obtiene la base: cada valor que suma hasta el total."""
        money = self.format_calculation_amount
        base, wage = self.value_base or 0.0, self.value_wage or 0.0
        components = [
            c for c in (self.z_calculation_base_components or [])
            if isinstance(c, dict) and (c.get('name') or abs(c.get('amount') or 0.0) > 0.0001)
        ]
        if not components:
            if self.amounts_match(base, wage):
                return self.build_calculation_row_html(
                    _('Base'), _('Salario del contrato'), money(base),
                    _('Misma cifra que el salario del contrato'))
            return self.build_calculation_row_html(
                _('Base'), _('Base de la provisión'), money(base),
                _('Base tomada de la simulación de liquidación'))

        names = [((c.get('name') or '').strip() or _('Valor')) for c in components]
        values = [money(c.get('amount') or 0.0) for c in components]
        items = []
        for component, name, value in zip(components, names, values):
            items.append(Markup(
                '<li class="mb-1"><div>%s: %s</div>%s</li>'
            ) % (escape(name), escape(value), self.build_calculation_component_meta_html(component)))
        formula_names = ' + '.join(names)
        formula_values = _('%(parts)s = %(result)s') % {
            'parts': ' + '.join(values), 'result': money(base),
        }
        body = Markup(
            '<div>%s</div>'
            '<ul class="mb-1 ps-3">%s</ul>'
            '<div class="fw-bold">%s</div>'
        ) % (escape(formula_names), Markup('').join(items), escape(formula_values))
        return Markup(
            '<tr class="border-bottom">'
            '<td class="align-top fw-bold text-start pe-3 py-2 text-nowrap">%s</td>'
            '<td class="align-top py-2">%s</td>'
            '</tr>'
        ) % (escape(_('Base')), body)

    def build_calculation_units_row(self):
        return self.build_calculation_row_html(
            _('Unidades'), _('Días / unidades de causación'),
            _('%s días') % self.format_calculation_quantity(self.time),
            _('Cantidad usada en la simulación de la provisión'))

    def build_calculation_liquidated_row(self):
        money, qty = self.format_calculation_amount, self.format_calculation_quantity
        base, units, liquidated = self.value_base or 0.0, self.time or 0.0, self.amount or 0.0
        divisor = self.get_calculation_divisor()
        expected = float_round((base / divisor) * units, precision_digits=0) if divisor else 0.0
        note = _('Acumulado a la fecha')
        if not self.amounts_match(expected, liquidated, tolerance=2.0):
            note = _('Valor liquidado guardado en la provisión (redondeo de valor día)')
        return self.build_calculation_row_html(
            _('Valor liquidado'),
            _('Base × Unidades ÷ %(divisor)s') % {'divisor': divisor},
            _('%(base)s × %(units)s ÷ %(divisor)s = %(result)s') % {
                'base': money(base), 'units': qty(units), 'divisor': divisor, 'result': money(liquidated),
            },
            note,
        )

    def build_calculation_payments_row(self):
        money = self.format_calculation_amount
        payments, codes = self.value_payments or 0.0, self.get_calculation_payment_codes()
        name = _('Suma de pagos de nómina del periodo (%s)') % codes if codes else _(
            'Suma de pagos de nómina del periodo')
        note = _('Sin pagos registrados') if abs(payments) < 0.0001 else _(
            'Líneas de nómina validadas del mes')
        return self.build_calculation_row_html(_('Pagos realizados'), name, money(payments), note)

    def resolve_current_payable_formula(self, previous_payable):
        money = self.format_calculation_amount
        liquidated, payments = self.amount or 0.0, self.value_payments or 0.0
        payable, previous = self.current_payable_value or 0.0, previous_payable or 0.0

        if self.provision == 'vacaciones' and payments > 0:
            intermediate = previous - payments
            if intermediate < 0 and self.amounts_match(payable, 0.0):
                return _('Vacaciones anticipadas: se deja en cero'), money(0.0), _('Caso vacaciones anticipadas')
            if intermediate >= 0 and self.amounts_match(payable, liquidated):
                return (
                    _('Valor liquidado'),
                    _('%(liq)s = %(result)s') % {'liq': money(liquidated), 'result': money(payable)},
                    _('Tras pagos del periodo se toma el liquidado'),
                )
            return (
                _('Valor a pagar actual mes anterior − Pagos realizados'),
                _('%(prev)s − %(pay)s = %(result)s') % {
                    'prev': money(previous), 'pay': money(payments), 'result': money(payable),
                },
                '',
            )

        if self.amounts_match(payable, 0.0) and payments > 0 and self.provision != 'vacaciones':
            return _('Cierre del periodo (pagos / liquidación)'), money(0.0), _('A pagar actual en cero por cierre')

        note = _('Caso normal: los pagos no superan lo provisionado') if payable >= 0 else _(
            'Los pagos superan lo liquidado')
        return (
            _('Valor liquidado − Pagos realizados'),
            _('%(liq)s − %(pay)s = %(result)s') % {
                'liq': money(liquidated), 'pay': money(payments), 'result': money(payable),
            },
            note,
        )

    def resolve_provision_month_formula(self, previous_payable, previous_amount):
        money = self.format_calculation_amount
        liquidated, payments = self.amount or 0.0, self.value_payments or 0.0
        provision_month, payable = self.value_balance or 0.0, self.current_payable_value or 0.0
        previous, previous_liq = previous_payable or 0.0, previous_amount or 0.0
        _date_start, date_end = self.get_calculation_period_dates()
        month = date_end.month if date_end else 0

        if self.provision == 'vacaciones' and payments > 0:
            intermediate = previous - payments
            expected_anticipadas = abs(intermediate) - abs(liquidated)
            if intermediate < 0 and self.amounts_match(provision_month, expected_anticipadas):
                return (
                    _('abs(Valor a pagar actual mes anterior − Pagos realizados) − Valor liquidado'),
                    _('abs(%(prev)s − %(pay)s) − %(liq)s = %(result)s') % {
                        'prev': money(previous), 'pay': money(payments),
                        'liq': money(liquidated), 'result': money(provision_month),
                    },
                    _('Vacaciones anticipadas'),
                )
            expected_with_payments = liquidated - intermediate
            if intermediate >= 0 and self.amounts_match(provision_month, expected_with_payments):
                return (
                    _('Valor liquidado − (Valor a pagar actual mes anterior − Pagos realizados)'),
                    _('%(liq)s − (%(prev)s − %(pay)s) = %(result)s') % {
                        'liq': money(liquidated), 'prev': money(previous),
                        'pay': money(payments), 'result': money(provision_month),
                    },
                    _('Hubo pagos de vacaciones en el periodo'),
                )

        if (
            self.provision != 'vacaciones' and month in (6, 12)
            and self.amounts_match(payable, 0.0)
            and self.amounts_match(provision_month, payments - previous_liq)
        ):
            return (
                _('Pagos realizados − Valor liquidado mes anterior'),
                _('%(pay)s − %(prev_liq)s = %(result)s') % {
                    'pay': money(payments), 'prev_liq': money(previous_liq), 'result': money(provision_month),
                },
                _('Cierre de provisión (junio / diciembre)'),
            )

        if self.amounts_match(provision_month, liquidated - previous):
            return (
                _('Valor liquidado − Valor a pagar actual mes anterior'),
                _('%(liq)s − %(prev)s = %(result)s') % {
                    'liq': money(liquidated), 'prev': money(previous), 'result': money(provision_month),
                },
                _('Diferencia del mes frente al saldo anterior'),
            )

        return _('Valor provisión mes (resultado del proceso)'), money(provision_month), _(
            'Valor guardado en la ejecución')

    def build_calculation_detail_html(self):
        self.ensure_one()
        if not self.provision:
            return False
        previous = self.get_previous_calculation_snapshot()
        payable_name, payable_values, payable_note = self.resolve_current_payable_formula(previous['payable'])
        month_name, month_values, month_note = self.resolve_provision_month_formula(
            previous['payable'], previous['amount'])
        rows = [
            self.build_calculation_base_row(),
            self.build_calculation_units_row(),
            self.build_calculation_row_html(_('Valor provisión mes'), month_name, month_values, month_note),
            self.build_calculation_liquidated_row(),
            self.build_calculation_payments_row(),
            self.build_calculation_row_html(_('Valor a pagar actual'), payable_name, payable_values, payable_note),
        ]
        return Markup(
            '<div class="o_zue_calculation_detail">'
            '<table class="table table-sm table-borderless mb-0 w-100">%s</table>'
            '</div>'
        ) % Markup('').join(rows)


class ResConfigSettingsProvisionsCalculationDetail(models.TransientModel):
    _inherit = 'res.config.settings'

    z_show_provisions_calculation_detail = fields.Boolean(string='Mostrar detalle del cálculo en provisiones', config_parameter='zue_hr_social_security.z_show_provisions_calculation_detail', default=False)