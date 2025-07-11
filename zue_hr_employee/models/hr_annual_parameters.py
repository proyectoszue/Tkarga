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
    calculation = fields.Selection([('info', 'Información'),
                                    ('sum_rule', 'Sumatoria Reglas'),
                                    ('sum_sequence', 'Sumatoria secuencias anteriores'),
                                    ('amount_last_six_months', 'Ingreso laboral promedio de los últimos seis meses anteriores'),
                                    ('date_issue', 'Fecha expedición'),
                                    ('start_date_year', 'Fecha certificación inicial'),
                                    ('end_date_year', 'Fecha certificación final'),
                                    ('dependents_type_vat', 'Dependientes - Tipo documento'),
                                    ('dependents_vat', 'Dependientes - No. Documento'),
                                    ('dependents_name', 'Dependientes - Apellidos y Nombres'),
                                    ('dependents_type', 'Dependientes - Parentesco'),], string='Tipo Cálculo',
                                   default='info', required=True)
    type_partner = fields.Selection([('employee', 'Empleado'), ('company', 'Compañía')], string='Origen Información')
    information_fields_id = fields.Many2one('ir.model.fields', string="Información",domain="[('model_id.model', 'in', ['hr.employee','res.partner','hr.contract'])]")
    information_fields_relation = fields.Char(related='information_fields_id.relation', string='Relación del objeto',store=True)
    related_field_id = fields.Many2one('ir.model.fields', string='Campo Relación',domain="[('model_id.model', '=', information_fields_relation)]")
    salary_rule_id = fields.Many2many('hr.salary.rule', string='Regla Salarial')
    origin_severance_pay = fields.Selection([('employee', 'Empleado'), ('fund', 'Fondo')], string='Pago cesantías')
    accumulated_previous_year = fields.Boolean(string='Acumulado año anterior')
    z_show_format_income_and_pensions = fields.Boolean(string='Mostrar en formato 2276')
    z_name_format_income_and_pensions = fields.Char(string='Titulo en formato 2276')
    sequence_list_sum = fields.Char(string='Sum secuencias')

    _sql_constraints = [('change_conf_rule_uniq', 'unique(annual_parameters_id,sequence)',
                         'Ya existe esta secuencia, por favor verificar')]


default_html_report_income_and_withholdings = '''
<table class="table border_report col-12" style="font-size: x-small;margin: 0px;">
    <tr>
        <td colspan="2"></td>
        <td colspan="8">
            <b>
                <center>
                    <h5>Certificado de Ingresos y Retenciones por Rentas de Trabajo y Pensiones
                        año
                        Agravable 2021
                    </h5>
                </center>
            </b>
        </td>
        <td colspan="2"></td>
    </tr>
    <tr>
        <td colspan="7">
            <br/>
            <center>
                <b>Antes de diligenciar este formulario lea
                    cuidadosamente
                    las instrucciones
                </b>
            </center>
        </td>
        <td colspan="5">4. Número de formulario
            <br/>
            $_val4_$
        </td>
    </tr>
    <tr>
        <td class="th_report rotate" rowspan="2">
            <div style="padding-right: 60px !important;">
                <b>Retenedor</b>
            </div>
        </td>
        <td colspan="2">
            5. Número de Identificación Tributaria (NIT)
            <br/>
            $_val5_$
        </td>
        <td class="width_items" colspan="1">6. D.V
            <br/>
            $_val6_$
        </td>

        <td colspan="2">7. Primer Apellido
            <br/>
            $_val7_$
        </td>

        <td colspan="2">8. Segundo Apellido
            <br/>
            $_val8_$
        </td>
        <td colspan="2">9. Primer Nombre
            <br/>
            $_val9_$
        </td>
        <td colspan="2">10. Otros Nombres
            <br/>
            $_val10_$
        </td>
    </tr>
    <tr>
        <td colspan="11">11. Razón Social
            <br/>
            $_val11_$
        </td>
    </tr>
    <tr>
        <td class="rotate">
            <div style="padding-right: 30px !important;">
                <b>Empleado</b>
            </div>
        </td>
        <td colspan="1">24. Tipo de Documento
            <br/>
            $_val24_$
        </td>
        <td colspan="3">25. Número de Identificación
            <br/>
            $_val25_$
        </td>
        <td colspan="2">26. Primer Apellido
            <br/>
            $_val26_$
        </td>
        <td colspan="2">27. Segundo Apellido
            <br/>
            $_val27_$
        </td>
        <td colspan="2">28. Primer Nombre
            <br/>
            $_val28_$
        </td>
        <td colspan="2">29. Otros Nombres
            <br/>
            $_val29_$
        </td>
    </tr>
    <tr>
        <td colspan="5">Período de Certificación
            <br/>
            30. DE $_val30_$ 31. A $_val31_$
        </td>
        <td colspan="2">32. Fecha de expedición
            <br/>
            $_val32_$
        </td>
        <td colspan="3">33. Lugar donde se practicó la retención
            <br/>
            $_val33_$
        </td>
        <td  colspan="1">34. Cód.Dpto
            <br/>
            $_val34_$
        </td>
        <td colspan="1">35. Cód.Ciudad/Municipio
            <br/>
            $_val35_$
        </td>
    </tr>
</table>
<table class="table table-striped border_report col-12" style="font-size: x-small;margin: 0px;">
    <tr>
        <td colspan="9">
            <center>
                <b>Concepto de los Ingresos</b>
            </center>
        </td>
        <td colspan="1" class="width_items">
            <b></b>
        </td>
        <td colspan="2" class="width_values">
            <center>
                <b>Valor</b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="9">Pagos por salarios o emolumentos eclesiásticos</td>
        <td colspan="1" class="width_items">36</td>
        <td colspan="2" class="width_values">$_val36_$</td>
    </tr>
    <tr>
        <td colspan="9">Pagos realizados con bonos electrónicos o de papel de servicio, cheques,
            tarjetas,
            vales, etc.
        </td>
        <td colspan="1" class="width_items">37</td>
        <td colspan="2" class="width_values">$_val37_$</td>
    </tr>
    <tr>
        <td colspan="9">Pagos por honorarios</td>
        <td colspan="1" class="width_items">38</td>
        <td colspan="2" class="width_values">$_val38_$</td>
    </tr>
    <tr>
        <td colspan="9">Pagos por servicios</td>
        <td colspan="1" class="width_items">39</td>
        <td colspan="2" class="width_values">$_val39_$</td>
    </tr>
    <tr>
        <td colspan="9">Pagos por comisiones</td>
        <td colspan="1" class="width_items">40</td>
        <td colspan="2" class="width_values">$_val40_$</td>
    </tr>
    <tr>
        <td colspan="9">Pagos por prestaciones sociales</td>
        <td colspan="1" class="width_items">41</td>
        <td colspan="2" class="width_values">$_val41_$</td>
    </tr>
    <tr>
        <td colspan="9">Pagos por viáticos</td>
        <td colspan="1" class="width_items">42</td>
        <td colspan="2" class="width_values">$_val42_$</td>
    </tr>
    <tr>
        <td colspan="9">Pagos por gastos de representación</td>
        <td colspan="1" class="width_items">43</td>
        <td colspan="2" class="width_values">$_val43_$</td>
    </tr>
    <tr>
        <td colspan="9">Pagos por compensaciones por el trabajo asociado cooperativo</td>
        <td colspan="1" class="width_items">44</td>
        <td colspan="2" class="width_values">$_val44_$</td>
    </tr>
    <tr>
        <td colspan="9">Otros pagos</td>
        <td colspan="1" class="width_items">45</td>
        <td colspan="2" class="width_values">$_val45_$</td>
    </tr>
    <tr>
        <td colspan="9">Cesantías e intereses de cesantías efectivamente pagadas al empleado</td>
        <td colspan="1" class="width_items">46</td>
        <td colspan="2" class="width_values">$_val46_$</td>
    </tr>
    <tr>
        <td colspan="9">Cesantías consignadas al fondo de cesantias</td>
        <td colspan="1" class="width_items">47</td>
        <td colspan="2" class="width_values">$_val47_$</td>
    </tr>
    <tr>
        <td colspan="9">Pensiones de jubilación, vejez o invalidez</td>
        <td colspan="1" class="width_items">48</td>
        <td colspan="2" class="width_values">$_val48_$</td>
    </tr>
    <tr>
        <td colspan="9">Total de ingresos brutos (Sume 36 a 48)</td>
        <td colspan="1" class="width_items">49</td>
        <td colspan="2" class="width_values">$_val49_$</td>
    </tr>
    <!--Concepto de los Aportes-->
    <tr>
        <td colspan="9">
            <center>
                <b>Concepto de los Aportes</b>
            </center>
        </td>
        <td colspan="1" class="width_items">
            <b></b>
        </td>
        <td colspan="2" class="width_values">
            <center>
                <b>Valor</b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="9">Aportes obligatorios por salud a cargo del trabajador</td>
        <td colspan="1" class="width_items">50</td>
        <td colspan="2" class="width_values">$_val50_$</td>
    </tr>
    <tr>
        <td colspan="9">Aportes obligatorios a fondos de pensiones y solidaridad pensional a
            cargo del
            trabajador
        </td>
        <td colspan="1" class="width_items">51</td>
        <td colspan="2" class="width_values">$_val51_$</td>
    </tr>
    <tr>
        <td colspan="9">Cotizaciones voluntarias al régimen de ahorro individual con solidaridad
            - RAIS
        </td>
        <td colspan="1" class="width_items">52</td>
        <td colspan="2" class="width_values">$_val52_$</td>
    </tr>
    <tr>
        <td colspan="9">Aportes voluntarios a fondos de pensiones</td>
        <td colspan="1" class="width_items">53</td>
        <td colspan="2" class="width_values">$_val53_$</td>
    </tr>
    <tr>
        <td colspan="9">Aportes a cuentas AFC</td>
        <td colspan="1" class="width_items">54</td>
        <td colspan="2" class="width_values">$_val54_$</td>
    </tr>
    <tr>
        <td colspan="9" style="background:#335E8B; color: white">Valor de la retención en la
            fuente por ingresos laborales y de pensiones
        </td>
        <td colspan="1" class="width_items">55</td>
        <td colspan="2" class="width_values">$_val55_$</td>
    </tr>
    <tr>
        <td colspan="12">Nombre del pagador o agente retenedor</td>
    </tr>
    <!--                            Datos a cargo del trabajador o pensionado-->
    <tr>
        <td colspan="12">
            <center>
                <b>Datos a cargo del trabajador o pensionado</b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="6">
            <center>
                <b>Concepto de otros ingresos</b>
            </center>
        </td>
        <td colspan="1" class="width_items"></td>
        <td colspan="2" class="width_values">
            <center>
                <b>Valor Recibido</b>
            </center>
        </td>
        <td colspan="1" class="width_items"></td>
        <td colspan="2" class="width_values">
            <center>
                <b>Valor Retenido</b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="6">Arrendamientos</td>
        <td colspan="1" class="width_items">56</td>
        <td colspan="2" class="width_values">$_val56_$</td>
        <td colspan="1" class="width_items">63</td>
        <td colspan="2" class="width_values">$_val63_$</td>
    </tr>
    <tr>
        <td colspan="6">Honorarios, comisiones y servicios</td>
        <td colspan="1" class="width_items">57</td>
        <td colspan="2" class="width_values">$_val57_$</td>
        <td colspan="1" class="width_items">64</td>
        <td colspan="2" class="width_values">$_val64_$</td>
    </tr>
    <tr>
        <td colspan="6">Intereses y rendimientos financieros</td>
        <td colspan="1" class="width_items">58</td>
        <td colspan="2" class="width_values">$_val58_$</td>
        <td colspan="1" class="width_items">65</td>
        <td colspan="2" class="width_values">$_val65_$</td>
    </tr>
    <tr>
        <td colspan="6">Enajenación de activos fijos</td>
        <td colspan="1" class="width_items">59</td>
        <td colspan="2" class="width_values">$_val59_$</td>
        <td colspan="1" class="width_items">66</td>
        <td colspan="2" class="width_values">$_val66_$</td>
    </tr>
    <tr>
        <td colspan="6">Loterías, rifas, apuestas y similares</td>
        <td colspan="1" class="width_items">60</td>
        <td colspan="2" class="width_values">$_val60_$</td>
        <td colspan="1" class="width_items">67</td>
        <td colspan="2" class="width_values">$_val67_$</td>
    </tr>
    <tr>
        <td colspan="6">Otros</td>
        <td colspan="1" class="width_items">61</td>
        <td colspan="2" class="width_values">$_val61_$</td>
        <td colspan="1" class="width_items">68</td>
        <td colspan="2" class="width_values">$_val68_$</td>
    </tr>
    <tr>
        <td colspan="6">Totales: (Valor recibido: Sume 57 a 61), (Valor retenido: Sume 63 a 68)</td>
        <td colspan="1" class="width_items">62</td>
        <td colspan="2" class="width_values">$_val62_$</td>
        <td colspan="1" class="width_items">69</td>
        <td colspan="2" class="width_values">$_val69_$</td>
    </tr>
    <tr>
        <td colspan="9">Total retenciones año gravable 2021 (Sume 55 + 69)</td>
        <td colspan="1" class="width_items">70</td>
        <td colspan="2" class="width_values">$_val70_$</td>
    </tr>
    <!--Identificación de los bienes y derechos poseídos-->
    <tr>
        <td colspan="1" class="width_items">
            <center>
                <b>Item</b>
            </center>
        </td>
        <td colspan="9">
            <center>
                <b>71. Identificación de los bienes y derechos poseídos</b>
            </center>
        </td>
        <td colspan="2" class="width_values">
            <center>
                <b>72. Valor patrimonial</b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="1" class="width_items">1</td>
        <td colspan="9">$_val71.1_$</td>
        <td colspan="2" class="width_values">$_val72.1_$</td>
    </tr>
    <tr>
        <td colspan="1" class="width_items">2</td>
        <td colspan="9">$_val71.2_$</td>
        <td colspan="2" class="width_values">$_val72.2_$</td>
    </tr>
    <tr>
        <td colspan="1" class="width_items">3</td>
        <td colspan="9">$_val71.3_$</td>
        <td colspan="2" class="width_values">$_val72.3_$</td>
    </tr>
    <tr>
        <td colspan="1" class="width_items">4</td>
        <td colspan="9">$_val71.4_$</td>
        <td colspan="2" class="width_values">$_val72.4_$</td>
    </tr>
    <tr>
        <td colspan="1" class="width_items">5</td>
        <td colspan="9">$_val71.5_$</td>
        <td colspan="2" class="width_values">$_val72.5_$</td>
    </tr>
    <tr>
        <td colspan="1" class="width_items">6</td>
        <td colspan="9">$_val71.6_$</td>
        <td colspan="2" class="width_values">$_val72.6_$</td>
    </tr>
    <tr>
        <td colspan="9" style="background:#335E8B; color: white">Deudas vigentes a 31 de
            diciembre de 2021
        </td>
        <td colspan="1" class="width_items">73</td>
        <td colspan="2" class="width_values">$_val73_$</td>
    </tr>
</table>
<table class="table border_report col-12" style="font-size: x-small;margin: 0px;">
    <!--Identificación del dependiente económico de acuerdo al parágrafo 2 del artículo 387 del Estatuto Tributario-->
    <tr>
        <td colspan="12">
            <center>
                <b>Identificación del dependiente económico de acuerdo al parágrafo 2 del
                    artículo
                    387 del Estatuto Tributario
                </b>
            </center>
        </td>
    </tr>
    <tr>
        <td colspan="2" class="th_report">74. Tipo documento
            <br/>
            $_val74_$
        </td>
        <td colspan="2" class="th_report">75. No. Documento
            <br/>
            $_val75_$
        </td>
        <td colspan="6" class="th_report">76. Apellidos y Nombres
            <br/>
            $_val76_$
        </td>
        <td colspan="2" class="th_report">77. Parentesco
            <br/>
            $_val77_$
        </td>
    </tr>
    <tr>
        <td colspan="8">
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
        <td colspan="4">
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
    _inherit = ['mail.thread', 'mail.activity.mixin']

    year = fields.Integer('Año', required=True, tracking=True)
    # Básicos Salario Minimo
    smmlv_monthly = fields.Float('Valor mensual SMMLV', required=True, tracking=True)
    smmlv_daily = fields.Float('Valor diario SMMLV', compute='_values_smmlv', store=True, tracking=True)
    top_four_fsp_smmlv = fields.Float('Tope 4 salarios FSP', compute='_values_smmlv', store=True, tracking=True)
    top_twenty_five_smmlv = fields.Float('Tope 25 salarios', compute='_values_smmlv', store=True, tracking=True)
    top_ten_smmlv = fields.Float('Tope 10 salarios', compute='_values_smmlv', store=True, tracking=True)
    # Básicos Auxilio de transporte
    transportation_assistance_monthly = fields.Float('Valor mensual Auxilio Transporte', required=True, tracking=True)
    transportation_assistance_daily = fields.Float('Valor diario Auxilio Transporte',
                                                   compute='_value_transportation_assistance_daily', store=True, tracking=True)
    top_max_transportation_assistance = fields.Float('Tope maxímo para pago', compute='_values_smmlv', store=True, tracking=True)
    # Básicos Salario Integral
    min_integral_salary = fields.Float('Salario mínimo integral', compute='_values_smmlv', store=True, tracking=True)
    porc_integral_salary = fields.Integer('Porcentaje salarial', required=True)
    value_factor_integral_salary = fields.Float('Valor salarial', compute='_values_integral_salary', store=True, tracking=True)
    value_factor_integral_performance = fields.Float('Valor prestacional', compute='_values_integral_salary',
                                                     store=True, tracking=True)
    # Básicos Horas Laborales
    hours_daily = fields.Float('Horas diarias', required=True, tracking=True)
    hours_weekly = fields.Float('Horas semanales', required=True, tracking=True)
    hours_fortnightly = fields.Float('Horas quincenales', required=True, tracking=True)
    hours_monthly = fields.Float('Horas mensuales', required=True, tracking=True)
    # Seguridad Social
    weight_contribution_calculations = fields.Boolean('Cálculos de aportes al peso', tracking=True)
    # Salud
    value_porc_health_company = fields.Float('Porcentaje empresa salud', required=True, tracking=True)
    value_porc_health_employee = fields.Float('Porcentaje empleado salud', required=True, tracking=True)
    value_porc_health_total = fields.Float('Porcentaje total salud', compute='_value_porc_health_total', store=True, tracking=True)
    value_porc_health_employee_foreign = fields.Float('Porcentaje aporte extranjero', required=True, tracking=True)
    # Pension
    value_porc_pension_company = fields.Float('Porcentaje empresa pensión', required=True, tracking=True)
    value_porc_pension_employee = fields.Float('Porcentaje empleado pensión', required=True, tracking=True)
    value_porc_pension_total = fields.Float('Porcentaje total pensión', compute='_value_porc_pension_total', store=True, tracking=True)
    # Aportes parafiscales
    value_porc_compensation_box_company = fields.Float('Caja de compensación', required=True, tracking=True)
    value_porc_sena_company = fields.Float('SENA', required=True, tracking=True)
    value_porc_icbf_company = fields.Float('ICBF', required=True, tracking=True)
    # Provisiones prestaciones
    value_porc_provision_bonus = fields.Float('Prima', required=True, tracking=True)
    value_porc_provision_cesantias = fields.Float('Cesantías', required=True, tracking=True)
    value_porc_provision_intcesantias = fields.Float('Intereses Cesantías', required=True, tracking=True)
    value_porc_provision_vacation = fields.Float('Vacaciones', required=True, tracking=True)
    # Tope Ley 1395
    value_porc_statute_1395 = fields.Integer('Porcentaje (%)', required=True, tracking=True)
    # Tributario
    # Retención en la fuente
    value_uvt = fields.Float('Valor UVT', required=True, tracking=True)
    value_top_source_retention = fields.Float('Tope para el calculo de retención en la fuente', required=True, tracking=True)
    # Incrementos
    value_porc_increment_smlv = fields.Float('Incremento SMLV', required=True, tracking=True)
    value_porc_ipc = fields.Float('Porcentaje IPC', required=True, tracking=True)
    # Certificado Ingresos/Retencion
    taxable_year = fields.Integer(string='Año gravable', tracking=True)
    gross_equity = fields.Float(string='Patrimonio bruto', tracking=True)
    total_revenues = fields.Float(string='Ingresos totales', tracking=True)
    credit_card = fields.Float(string='Tarjeta de crédito', tracking=True)
    purchases_and_consumption = fields.Float(string='Compras y consumos', tracking=True)
    conf_certificate_income_ids = fields.One2many('hr.conf.certificate.income', 'annual_parameters_id',
                                                  string='Configuración de reglas salariales', tracking=True)
    # HTML Certificado Ingreso y retenciones
    report_income_and_withholdings = fields.Html('Estructura Certificado ingresos y retenciones',default=default_html_report_income_and_withholdings, tracking=True)
    #PRESTACIONES SOCIALES SECTOR PUBLICO Y DISTRITAL
    z_food_subsidy_amount = fields.Integer(string="Subsidio de alimentación", tracking=True)
    z_bonus_services_rendered = fields.Integer(string="Tope Bonificación por servicios prestados (B.S.P)", tracking=True)
    z_food_subsidy_tope = fields.Integer(string="Tope Subsidio de alimentación", tracking=True)
    z_percentage_public = fields.Integer(string="Porcentaje Emp. Publicos", tracking=True)
    # Grilla UPC
    z_upc_lines_ids = fields.One2many('zue.upc.annual.parameters', 'z_upc_id', string='Líneas UPC', tracking=True)
    # Grilla Fondo de solidaridad y subsistencia
    z_fds_lines_ids = fields.One2many('zue.fds.annual.parameters', 'z_fds_id', string='Líneas Fondo de solidaridad y subsistencia', tracking=True)

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

    @api.onchange('hours_daily')
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

class zue_upc_annual_parameters(models.Model):
    _name = 'zue.upc.annual.parameters'
    _description = 'Parámetros anuales UPC'

    z_upc_id = fields.Many2one('hr.annual.parameters', string="UPC")
    z_age_group_upc = fields.Selection([
        ('age<1', 'Menores de 1 año'),
        ('age>1 and age<=4', 'De 1 a 4 años'),
        ('age>=5 and age<=14', 'De 5 a 14 años'),
        ('age>=15 and age<=18', 'De 15 a 18 años'),
        ('age>=19 and age<=44', 'De 19 a 44 años'),
        ('age>=45 and age<=49', 'De 45 a 49 años'),
        ('age>=50 and age<=54', 'De 50 a 54 años'),
        ('age>=55 and age<=59', 'De 55 a 59 años'),
        ('age>=60 and age<=64', 'De 60 a 64 años'),
        ('age>=65 and age<=69', 'De 65 a 69 años'),
        ('age>=70 and age<=74', 'De 70 a 74 años'),
        ('age>=75', 'De 75 y más años')
    ], string='Grupo de edades')
    z_normal_zone_upc = fields.Float(string="Zona normal")
    z_special_zone_upc = fields.Float(string="Zona especial")
    z_cities_upc = fields.Float(string="Ciudades")
    z_islands_upc = fields.Float(string="Islas")
    z_gender_upc = fields.Selection([('masculino', 'Masculino'), ('femenino', 'Femenino'), ('otro', 'Otro')],
                                    string="Genero", required=True)

class zue_fds_annual_parameters(models.Model):
    _name = 'zue.fds.annual.parameters'
    _description = 'Parámetros anuales Fondo de Solidaridad y Subsistencia'

    z_fds_id = fields.Many2one('hr.annual.parameters', string="Fondo de solidaridad y subsistencia")
    z_initial_value = fields.Float('Rango inicial')
    z_final_value = fields.Float('Rango final')
    z_porcentage_solidarity_fund = fields.Float('Porcentaje Fondo de solidaridad')
    z_porcentage_subsistence_fund = fields.Float('Porcentaje Fondo de subsistencia')

