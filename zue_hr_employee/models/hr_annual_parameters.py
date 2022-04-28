# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
import time

#Tabla Parametrización Certificados ingresos y retenciones
class hr_conf_certificate_income(models.Model):
    _name = 'hr.conf.certificate.income'
    _description = 'Configuración conceptos para informe de ingresos y retenciones'

    annual_parameters_id = fields.Many2one('hr.annual.parameters', string='Parametro Anual', required=True)
    sequence = fields.Integer(string='Secuencia', required=True)
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Regla Salarial', required=True)

    _sql_constraints = [('change_conf_rule_uniq', 'unique(annual_parameters_id,salary_rule_id)',
                         'Ya existe una regla salarial asignada para el reporte de ingresos y retenciones, por favor verificar')]


default_html_report_income_and_withholdings = '''
<style>
    div{
    border: none;
    padding-bottom: 20px !important;
    }
    th, td{
    padding: 0px !important;
    }
    .th_report{
    padding: 10px !important;
    }
    .rotate_text{
        -webkit-transform: rotate(-90deg);
        -moz-transform: rotate(-90deg);
        -o-transform: rotate(-90deg);
        transform: rotate(-90deg);
        height:20px;
        width:25px;
    }
    .inline-block{
        display:-moz-inline-stack;
        display:inline-block;
        zoom:1;
        *display:inline;
    }
</style>
<div class="row row_items">
    <div class="col-2" style="padding: 0px;">
        <img t-att-src="image_data_uri(o.img_header_file)" style="width: 145px; height: 48px;"/>
    </div>
    <div class="col-8">
        <b>
            <center>
                <h5>Certificado de Ingresos y Retenciones por Rentas de Trabajo y Pensiones año
                    Agravable 2021
                </h5>
            </center>
        </b>
    </div>
    <div class="col-2" style="padding: 0px;">
        <img t-att-src="image_data_uri(o.img_footer_file)" style="width: 145px;height: 55px;"/>
    </div>
</div>
<table class="table border: #2A4B6E 1px solid col-12" style="font-size: x-small">
    <tr>
        <td colspan="9" class="th_report">Antes de diligenciar este formulario lea cuidadosamente
            las instrucciones
        </td>
        <td colspan="9" class="th_report">4. Número de formulario</td>
    </tr>
    <tr>
        <td class="th_report" rowspan="2">
            <span class="rotate_text inline-block">Retenedor</span>
        </td>
        <td class="th_report" colspan="4">5. Número de Identificación Tributaria (NIT)</td>
        <td class="th_report" colspan="1">6. D.V</td>
        <td class="th_report" colspan="2">7. Primer Apellido</td>
        <td class="th_report" colspan="2">8. Segundo Apellido</td>
        <td class="th_report" colspan="2">9. Primer Nombre</td>
        <td class="th_report" colspan="2">10. Otros Nombres</td>
    </tr>
    <tr>
        <td class="th_report" colspan="12">11. Razón Social</td>
    </tr>
    <tr>
        <td class="th_report">
            <span class="rotate_text inline-block">Empleado</span>
        </td>
        <td class="th_report" colspan="2">24. Tipo de Documento</td>
        <td class="th_report" colspan="2">25. Número de Identificación</td>
        <td class="th_report" colspan="2">26. Primer Apellido</td>
        <td class="th_report" colspan="2">27. Segundo Apellido</td>
        <td class="th_report" colspan="2">28. Primer Nombre</td>
        <td class="th_report" colspan="2">29. Otros Nombres</td>
    </tr>
    <tr>
        <td class="th_report" colspan="5">Período de Certificación 30. DE 31. A:</td>
        <td class="th_report" colspan="2">32. Fecha de expedición</td>
        <td class="th_report" colspan="3">33. Lugar donde se practicó la retención</td>
        <td class="th_report" colspan="2">34. Cód.Dpto</td>
        <td class="th_report" colspan="2">35. Cód.Ciudad/Municipio</td>
    </tr>
</table>
<table class="table table-striped border: #2A4B6E 1px solid" style="font-size: x-small;">
    <tr>
        <td colspan="3">
            <center>
                <b>Concepto de los Ingresos</b>
            </center>
        </td>
        <td colspan="1">
            <b></b>
        </td>
        <td colspan="2">
            <center>
                <b>Valor</b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="3">Pagos por salarios o emolumentos eclesiásticos</td>
        <td colspan="1">36</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pagos realizados con bonos electrónicos o de papel de servicio, cheques,
            tarjetas,
            vales, etc.
        </td>
        <td colspan="1">37</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pagos por honorarios</td>
        <td colspan="1">38</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pagos por servicios</td>
        <td colspan="1">39</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pagos por comisiones</td>
        <td colspan="1">40</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pagos por prestaciones sociales</td>
        <td colspan="1">41</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pagos por viáticos</td>
        <td colspan="1">42</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pagos por gastos de representación</td>
        <td colspan="1">43</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pagos por compensaciones por el trabajo asociado cooperativo</td>
        <td colspan="1">44</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Otros pagos</td>
        <td colspan="1">45</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Cesantías e intereses de cesantías efectivamente pagadas al empleado
        </td>
        <td colspan="1">46</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Cesantías consignadas al fondo de cesantias</td>
        <td colspan="1">47</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Pensiones de jubilación, vejez o invalidez</td>
        <td colspan="1">48</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Total de ingresos brutos (Sume 36 a 48)</td>
        <td colspan="1">49</td>
        <td colspan="2"></td>
    </tr>
    <!--                        Concepto de los Aportes-->
    <tr>
        <td colspan="3">
            <center>
                <b>Concepto de los Aportes</b>
            </center>
        </td>
        <td colspan="1">
            <b></b>
        </td>
        <td colspan="2">
            <center>
                <b>Valor</b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="3">Aportes obligatorios por salud a cargo del trabajador</td>
        <td colspan="1">50</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Aportes obligatorios a fondos de pensiones y solidaridad pensional a
            cargo del
            trabajador
        </td>
        <td colspan="1">51</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Cotizaciones voluntarias al régimen de ahorro individual con solidaridad
            - RAIS
        </td>
        <td colspan="1">52</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Aportes voluntarios a fondos de pensiones</td>
        <td colspan="1">53</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3">Aportes a cuentas AFC</td>
        <td colspan="1">54</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3" style="background:#335E8B; color: white">Valor de la retención en la
            fuente por ingresos laborales y de pensiones
        </td>
        <td colspan="1">55</td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="6">Nombre del pagador o agente retenedor</td>
    </tr>
    <!--                            Datos a cargo del trabajador o pensionado-->
    <tr>
        <td colspan="5">
            <center>
                <b>Datos a cargo del trabajador o pensionado</b>
            </center>
        </td>
    </tr>
    <tr>
        <td>
            <center>
                <b>Concepto de otros ingreos</b>
            </center>
        </td>
        <td colspan="1">
            <b></b>
        </td>
        <td>
            <center>
                <b>Valor Recibido</b>
            </center>
        </td>
        <td>
            <b></b>
        </td>
        <td>
            <center>
                <b>Valor Retenido</b>
            </center>
        </td>
    </tr>
    <tr>
        <td>Arrendamientos</td>
        <td colspan="1">56</td>
        <td></td>
        <td>63</td>
        <td></td>
    </tr>
    <tr>
        <td>Honorarios, comisiones y servicios</td>
        <td colspan="1">57</td>
        <td></td>
        <td>64</td>
        <td></td>
    </tr>
    <tr>
        <td>Intereses y rendimientos financieros</td>
        <td colspan="1">58</td>
        <td></td>
        <td>65</td>
        <td></td>
    </tr>
    <tr>
        <td>Enajenación de activos fijos</td>
        <td colspan="1">59</td>
        <td></td>
        <td>66</td>
        <td></td>
    </tr>
    <tr>
        <td>Loterías, rifas, apuestas y similares</td>
        <td colspan="1">60</td>
        <td></td>
        <td>67</td>
        <td></td>
    </tr>
    <tr>
        <td>Otros</td>
        <td colspan="1">61</td>
        <td></td>
        <td>68</td>
        <td></td>
    </tr>
    <tr>
        <td>Totales: (Valor recibido: Sume 57 a 61), (Valor retenido: Sume 63 a 68)</td>
        <td colspan="1">62</td>
        <td></td>
        <td>69</td>
        <td></td>
    </tr>
    <tr>
        <td colspan="3">Total retenciones año gravable 2021 (Sume 55 + 69)</td>
        <td colspan="1">70</td>
        <td></td>
    </tr>
    <!--                        Identificación de los bienes y derechos poseídos-->
    <tr>
        <td colspan="1">
            <center>
                <b>Item</b>
            </center>
        </td>
        <td colspan="3">
            <center>
                <b>71. Identificación de los bienes y derechos poseídos</b>
            </center>
        </td>
        <td colspan="2">
            <center>
                <b>72. Valor patrimonial</b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="1">1</td>
        <td colspan="3"></td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="1">2</td>
        <td colspan="3"></td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="1">3</td>
        <td colspan="3"></td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="1">4</td>
        <td colspan="3"></td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="1">5</td>
        <td colspan="3"></td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="1">6</td>
        <td colspan="3"></td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="3" style="background:#335E8B; color: white">Deudas vigentes a 31 de
            diciembre de 2021
        </td>
        <td colspan="1">73</td>
        <td colspan="2"></td>
    </tr>
    <!--                             Identificación del dependiente económico de acuerdo al parágrafo 2 del artículo 387 del Estatuto Tributario-->
    <tr>
        <td colspan="6">
            <center>
                <b>Identificación del dependiente económico de acuerdo al parágrafo 2 del artículo
                    387 del Estatuto Tributario
                </b>
            </center>
        </td>
    </tr>
    <tr>
        <td>74. Tipo documento</td>
        <td>75. No. Documento</td>
        <td colspan="2">76. Apellidos y Nombres</td>
        <td>77. Parentesco</td>
    </tr>
    <tr>
        <td colspan="3">
            Certifico que durante el año gravable 2021:
            <br/>
            1. Mi patrimonio bruto no excedió de 4.500 UVT ($163.386.000).
            <br/>
            2. Mis ingresos brutos fueron inferiores a 1.400 UVT ($50.831.000).
            <br/>
            3. No fui responsable del impuesto sobre las ventas.
            <br/>
            4. Mis consumos mediante tarjeta de crédito no excedieron la suma de 1.400 UVT
            ($50.831.000).
            <br/>
            5. Que el total de mis compras y consumos no superaron la suma de 1.400 UVT
            ($50.831.000).
            <br/>
            6. Que el valor total de mis consignaciones bancarias, depósitos o inversiones
            financieras no excedieron los 1.400 UVT ($50.831.000).
            <br/>
            Por lo tanto, manifiesto que no estoy obligado a presentar declaración de renta y
            complementario por el año gravable 2021
        </td>
        <td colspan="3">
            Firma del Trabajador o Pensionado
        </td>
    </tr>
</table>
<p style="font-size: x-small">
    <b>Nota:</b>
    este certificado sustituye para todos los efectos legales la declaración de Renta y
    Complementario para el trabajador o pensionado que lo firme.
    <br/>
    Para aquellos trabajadores independientes contribuyentes del impuesto unificado deberán
    presentar la declaración anual consolidada del Régimen Simple de Tributación (SIMPLE).
</p>

'''

# Tabla de parametros anuales
class hr_annual_parameters(models.Model):
    _name = 'hr.annual.parameters'
    _description = 'Parámetros anuales'

    year = fields.Integer('Año', required=True)
    # Básicos Salario Minimo
    smmlv_monthly = fields.Float('Valor mensual SMMLV', required=True)
    smmlv_daily = fields.Float('Valor diario SMMLV', compute='_values_smmlv', store=True)
    top_four_fsp_smmlv = fields.Float('Tope 4 salarios FSP', compute='_values_smmlv', store=True)
    top_twenty_five_smmlv = fields.Float('Tope 25 salarios', compute='_values_smmlv', store=True)
    top_ten_smmlv = fields.Float('Tope 10 salarios', compute='_values_smmlv', store=True)
    # Básicos Auxilio de transporte
    transportation_assistance_monthly = fields.Float('Valor mensual Auxilio Transporte', required=True)
    transportation_assistance_daily = fields.Float('Valor diario Auxilio Transporte',
                                                   compute='_value_transportation_assistance_daily', store=True)
    top_max_transportation_assistance = fields.Float('Tope maxímo para pago', compute='_values_smmlv', store=True)
    # Básicos Salario Integral
    min_integral_salary = fields.Float('Salario mínimo integral', compute='_values_smmlv', store=True)
    porc_integral_salary = fields.Integer('Porcentaje salarial', required=True)
    value_factor_integral_salary = fields.Float('Valor salarial', compute='_values_integral_salary', store=True)
    value_factor_integral_performance = fields.Float('Valor prestacional', compute='_values_integral_salary',
                                                     store=True)
    # Básicos Horas Laborales
    hours_daily = fields.Integer('Horas diarias', required=True)
    hours_weekly = fields.Integer('Horas semanales', compute='_values_hours', store=True)
    hours_fortnightly = fields.Integer('Horas quincenales', compute='_values_hours', store=True)
    hours_monthly = fields.Integer('Horas mensuales', compute='_values_hours', store=True)
    # Seguridad Social
    weight_contribution_calculations = fields.Boolean('Cálculos de aportes al peso')
    # Salud
    value_porc_health_company = fields.Float('Porcentaje empresa salud', required=True)
    value_porc_health_employee = fields.Float('Porcentaje empleado salud', required=True)
    value_porc_health_total = fields.Float('Porcentaje total salud', compute='_value_porc_health_total', store=True)
    value_porc_health_employee_foreign = fields.Float('Porcentaje aporte extranjero', required=True)
    # Pension
    value_porc_pension_company = fields.Float('Porcentaje empresa pensión', required=True)
    value_porc_pension_employee = fields.Float('Porcentaje empleado pensión', required=True)
    value_porc_pension_total = fields.Float('Porcentaje total pensión', compute='_value_porc_pension_total', store=True)
    # Aportes parafiscales
    value_porc_compensation_box_company = fields.Float('Caja de compensación', required=True)
    value_porc_sena_company = fields.Float('SENA', required=True)
    value_porc_icbf_company = fields.Float('ICBF', required=True)
    # Provisiones prestaciones
    value_porc_provision_bonus = fields.Float('Prima', required=True)
    value_porc_provision_cesantias = fields.Float('Cesantías', required=True)
    value_porc_provision_intcesantias = fields.Float('Intereses Cesantías', required=True)
    value_porc_provision_vacation = fields.Float('Vacaciones', required=True)
    # Tope Ley 1395
    value_porc_statute_1395 = fields.Integer('Porcentaje (%)', required=True)
    # Tributario
    # Retención en la fuente
    value_uvt = fields.Float('Valor UVT', required=True)
    value_top_source_retention = fields.Float('Tope para el calculo de retención en la fuente', required=True)
    # Incrementos
    value_porc_increment_smlv = fields.Float('Incremento SMLV', required=True)
    value_porc_ipc = fields.Float('Porcentaje IPC', required=True)
    # Certificado Ingresos/Retencion
    taxable_year = fields.Integer(string='Año gravable')
    gross_equity = fields.Float(string='Patrimonio bruto')
    total_revenues = fields.Float(string='Ingresos totales')
    credit_card = fields.Float(string='Tarjeta de crédito')
    purchases_and_consumption = fields.Float(string='Compras y consumos')
    conf_certificate_income_ids = fields.One2many('hr.conf.certificate.income', 'annual_parameters_id',
                                                  string='Configuración de reglas salariales')
    # Imagen Dia y Formato Número
    img_header_file = fields.Binary('Logo Dian')
    img_header_filename = fields.Char('Logo Dian filename')
    img_footer_file = fields.Binary('Número de formato')
    img_footer_filename = fields.Char('Número de formato filename')
    # HTML Certificado Ingreso y retenciones
    report_income_and_withholdings = fields.Html('Estructura Certificado ingresos y retenciones',default=default_html_report_income_and_withholdings)

    # Metodos
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{}".format(str(record.year))))
        return result

    @api.depends('smmlv_monthly')
    def _values_smmlv(self):
        self.smmlv_daily = self.smmlv_monthly / 30
        self.top_four_fsp_smmlv = 4 * self.smmlv_monthly
        self.top_twenty_five_smmlv = 25 * self.smmlv_monthly
        self.top_ten_smmlv = 10 * self.smmlv_monthly
        self.top_max_transportation_assistance = 2 * self.smmlv_monthly
        self.min_integral_salary = 13 * self.smmlv_monthly

    @api.depends('transportation_assistance_monthly')
    def _value_transportation_assistance_daily(self):
        self.transportation_assistance_daily = self.transportation_assistance_monthly / 30

    @api.depends('porc_integral_salary')
    def _values_integral_salary(self):
        porc_integral_salary_rest = 100 - self.porc_integral_salary
        value_factor_integral_salary = round(self.min_integral_salary / ((porc_integral_salary_rest / 100) + 1), 0)
        value_factor_integral_performance = round(self.min_integral_salary - value_factor_integral_salary, 0)
        self.value_factor_integral_salary = value_factor_integral_salary
        self.value_factor_integral_performance = value_factor_integral_performance

    @api.depends('hours_daily')
    def _values_hours(self):
        self.hours_weekly = 7 * self.hours_daily
        self.hours_fortnightly = 15 * self.hours_daily
        self.hours_monthly = 30 * self.hours_daily

    @api.depends('value_porc_health_company', 'value_porc_health_employee')
    def _value_porc_health_total(self):
        self.value_porc_health_total = self.value_porc_health_company + self.value_porc_health_employee

    @api.depends('value_porc_pension_company', 'value_porc_pension_employee')
    def _value_porc_pension_total(self):
        self.value_porc_pension_total = self.value_porc_pension_company + self.value_porc_pension_employee

    # Validaciones
    @api.onchange('porc_integral_salary')
    def _onchange_porc_integral_salary(self):
        for record in self:
            if record.porc_integral_salary > 100:
                raise UserError(_('El porcentaje salarial integral no puede ser mayor a 100. Por favor verificar.'))

                # Funcionalidades

    # Obtener salario integral, el parametro get_value | 0 = Valor Salarial & 1 = Valor Prestacional
    def get_values_integral_salary(self, integral_salary, get_value):
        porc_integral_salary_rest = 100 - self.porc_integral_salary
        value_factor_integral_salary = round(integral_salary / ((porc_integral_salary_rest / 100) + 1), 0)
        value_factor_integral_performance = round(integral_salary - value_factor_integral_salary, 0)
        value_factor_integral_salary = value_factor_integral_salary
        value_factor_integral_performance = value_factor_integral_performance
        return value_factor_integral_salary if get_value == 0 else value_factor_integral_performance

    _sql_constraints = [
        ('change_year_uniq', 'unique(year)', 'Ya existe una parametrización para el año digitado, por favor verificar')]