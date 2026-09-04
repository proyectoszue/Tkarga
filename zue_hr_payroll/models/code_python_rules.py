#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------LIQUIDACION DE NÓMINA--------------------------------------------------------
#---------------------------------------Basic Salary--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC',employee.type_employee.id)
if obj_salary_rule and version.modality_salary != 'integral' and version.modality_salary != 'sostenimiento' and version.subcontract_type not in ('obra_parcial','obra_integral'):
    if worked_days.WORK100 != 0.0:
        result =  round(worked_days.WORK100.number_of_days * (version.wage /30))

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC',employee.type_employee.id)
if obj_salary_rule and version.modality_salary != 'integral' and version.modality_salary != 'sostenimiento':
    if (worked_days.WORK100 or 0) != 0.0:
        result =  round((worked_days.WORK100.number_of_days or 0) * (version.wage /30))
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC', employee.type_employee.id)
if obj_salary_rule and version.modality_salary != 'integral' and (version.modality_salary != 'sostenimiento') and (version.subcontract_type not in ('obra_parcial', 'obra_integral')):
    if (worked_days.WORK100 or 0) != 0.0:
        result = round((worked_days.WORK100.number_of_days or 0) * (version.wage / 30))
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC', employee.type_employee.id)
if obj_salary_rule and version.modality_salary != 'integral' and version.modality_salary != 'sostenimiento' and version.subcontract_type not in ('obra_parcial','obra_integral'):
    if (worked_days.WORK100 or 0) != 0.0:
        result =  round((worked_days.WORK100.number_of_days or 0) * (version.wage /30))    
#V19 Tkarga
result = 0.0 
obj_salary_rule = payslip.get_salary_rule('BASIC', employee.type_employee.id) 
if obj_salary_rule and version.modality_salary != 'integral' and (version.modality_salary != 'sostenimiento') and (version.subcontract_type not in ('obra_parcial', 'obra_integral')): 
    if (worked_days.WORK100 or 0) != 0.0: 
        result = round((worked_days.WORK100.number_of_days or 0) * (version.wage / 30))
#---------------------------------------Basic Salary DOCENTES HORAS CATEDRA--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC', employee.type_employee.id)
if obj_salary_rule and version.modality_salary != 'integral' and version.modality_salary != 'sostenimiento' and version.subcontract_type not in ('obra_parcial', 'obra_integral'):
    if worked_days.WORK100 != 0.0:
        result = round(worked_days.WORK100.number_of_days * (version.wage / 30))
if obj_salary_rule and version.z_category_educators_id:
    if version.z_category_educators_id.z_wage == version.wage:
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_overtime.shift_hours > 0:
                result = version.wage
                result_qty = obj_overtime.shift_hours
#---------------------------------------Basic Salary Integral--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC002',employee.type_employee.id)
if obj_salary_rule and version.modality_salary == 'integral':
    wage = annual_parameters.get_values_integral_salary(version.wage,0) + annual_parameters.get_values_integral_salary(version.wage,1)
    if worked_days.WORK100 != 0.0:
        result =  round(worked_days.WORK100.number_of_days * (wage/30)) 

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC002',employee.type_employee.id)
if obj_salary_rule and version.modality_salary == 'integral':
    wage = annual_parameters.get_values_integral_salary(version.wage,0) + annual_parameters.get_values_integral_salary(version.wage,1)
    if (worked_days.WORK100 or 0) != 0.0:
        result =  round((worked_days.WORK100.number_of_days or 0) * (wage/30))
#V19 Molpartes, Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC002', employee.type_employee.id)
if obj_salary_rule and version.modality_salary == 'integral':
    wage = annual_parameters.get_values_integral_salary(version.wage, 0) + annual_parameters.get_values_integral_salary(version.wage, 1)
    if (worked_days.WORK100 or 0) != 0.0:
        result = round((worked_days.WORK100.number_of_days or 0) * (wage / 30))
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC002', employee.type_employee.id)
if obj_salary_rule and version.modality_salary == 'integral':
    wage = annual_parameters.get_values_integral_salary(version.wage,0) + annual_parameters.get_values_integral_salary(version.wage,1)
    if (worked_days.WORK100 or 0) != 0.0:
        result =  round((worked_days.WORK100.number_of_days or 0) * (wage/30))
#---------------------------------------Basic Cuota Sostenimiento--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC003',employee.type_employee.id)
if obj_salary_rule and version.modality_salary == 'sostenimiento':
    if worked_days.WORK100 != 0.0:
        result =  round(worked_days.WORK100.number_of_days * (version.wage /30))

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC003',employee.type_employee.id)
if obj_salary_rule and version.modality_salary == 'sostenimiento':
    if (worked_days.WORK100 or 0) != 0.0:
        result =  round((worked_days.WORK100.number_of_days or 0) * (version.wage /30))
#V19 Molpartes, Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC003', employee.type_employee.id)
if obj_salary_rule and version.modality_salary == 'sostenimiento':
    if (worked_days.WORK100 or 0) != 0.0:
        result = round((worked_days.WORK100.number_of_days or 0) * (version.wage / 30))
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC003', employee.type_employee.id)
if obj_salary_rule and version.modality_salary == 'sostenimiento':
    if (worked_days.WORK100 or 0) != 0.0:
        result =  round((worked_days.WORK100.number_of_days or 0) * (version.wage /30))       
# ---------------------------------------Basic Por turno SERVAGRO--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASICTURNOS',employee.type_employee.id)
if obj_salary_rule and version.subcontract_type in ('obra_parcial','obra_integral'):
    obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
    if obj_overtime:
        if obj_overtime.shift_hours > 0:
            result = (version.wage/240)
            result_qty = obj_overtime.shift_hours
#---------------------------------------Auxilio de transporte--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX000',employee.type_employee.id)
aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
aplicar = 30 if version.z_pay_auxtransportation==True and inherit_contrato==0 else aplicar
dias = 0 if aplicar == 0 else payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to) + payslip.sum_days_works('COMPENSATORIO', payslip.date_from, payslip.date_to)
dias += worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
if worked_days.COMPENSATORIO != 0.0:
    dias += worked_days.COMPENSATORIO.number_of_days
liquidated_aux_transport = payslip.get_parameterization_contributors().liquidated_aux_transport if len(payslip.get_parameterization_contributors()) > 0 else True
liquidated_aux_transport = False if payslip.settle_payroll_concepts == False and inherit_contrato!=0 else liquidated_aux_transport
if obj_salary_rule and version.z_not_pay_auxtransportation == False and liquidated_aux_transport and dias != 0.0 and version.contract_type != 'aprendizaje' and version.subcontract_type not in ('obra_parcial','obra_integral'):
    auxtransporte = annual_parameters.transportation_assistance_monthly
    auxtransporte_tope = annual_parameters.top_max_transportation_assistance
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        if dias != 0.0:
            if version.not_validate_top_auxtransportation == True:
                result = round(dias * auxtransporte / 30)
            else:
                if (version.wage <= auxtransporte_tope) and (total <= auxtransporte_tope):
                    result = round(dias * auxtransporte /30)
# V17
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX000',employee.type_employee.id)
aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
dias = 0 if aplicar == 0 else payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to) + payslip.sum_days_works('COMPENSATORIO', payslip.date_from, payslip.date_to)
dias += worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
if worked_days.COMPENSATORIO != 0.0:
    dias += worked_days.COMPENSATORIO.number_of_days
liquidated_aux_transport = payslip.get_parameterization_contributors().liquidated_aux_transport if len(payslip.get_parameterization_contributors()) > 0 else True
liquidated_aux_transport = False if payslip.settle_payroll_concepts == False and inherit_contrato!=0 else liquidated_aux_transport
if obj_salary_rule and liquidated_aux_transport and dias != 0.0 and version.z_not_pay_auxtransportation == False and version.subcontract_type not in ('obra_parcial','obra_integral'):
    auxtransporte = annual_parameters.transportation_assistance_monthly
    auxtransporte_tope = annual_parameters.top_max_transportation_assistance
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        if dias != 0.0:
            if version.not_validate_top_auxtransportation == True:
                result = round(dias * auxtransporte / 30)
            else:
                if (version.wage <= auxtransporte_tope) and (total <= auxtransporte_tope):
                    result = round(dias * auxtransporte /30)

#V19
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX000', employee.type_employee.id)

if obj_salary_rule:
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)

    # =============================================================
    # DÍAS WORK100 + COMPENSATORIO
    # aplicar==0 → solo días actuales (incluso en liquidación,
    #              para no doblar días ya pagados en quincena previa)
    # aplicar!=0 → días previos del mes + días actuales
    # =============================================================
    dias = 0 if aplicar == 0 else (
        payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        + payslip.sum_days_works('COMPENSATORIO', payslip.date_from, payslip.date_to)
    )
    if (worked_days.WORK100 or 0) != 0.0:
        dias += worked_days.WORK100.number_of_days or 0
    if (worked_days.COMPENSATORIO or 0) != 0.0:
        dias += worked_days.COMPENSATORIO.number_of_days or 0

    # =============================================================
    # PARÁMETRO LIQUIDATED_AUX_TRANSPORT
    # Controla si el tipo/subtipo de cotizante liquida auxilio.
    # En liquidación de contrato sin conceptos: forzar a False.
    # =============================================================
    liquidated_aux_transport = (
        payslip.get_parameterization_contributors().liquidated_aux_transport
        if len(payslip.get_parameterization_contributors()) > 0
        else True
    )
    if payslip.settle_payroll_concepts == False and inherit_contrato != 0:
        liquidated_aux_transport = False

    # =============================================================
    # CONDICIONES DE ENTRADA
    #  1. Regla activa para el tipo de empleado
    #  2. Flag "no pagar auxilio" en el contrato/empleado NO marcado
    #  3. Parametrización de cotizante autoriza el auxilio
    #  4. Hay días a pagar
    #  5. No es subcontrato de obra parcial o integral
    # =============================================================
    if (
        obj_salary_rule
        and version.z_not_pay_auxtransportation == False
        and liquidated_aux_transport
        and dias != 0.0
        and version.subcontract_type not in ('obra_parcial', 'obra_integral')
    ):
        auxtransporte     = annual_parameters.transportation_assistance_monthly
        auxtransporte_tope = annual_parameters.top_max_transportation_assistance
        day_initial_payrroll = payslip.date_from.day
        day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day

        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):

            # Base devengado salarial para validar tope
            total = (
                categories.DEV_SALARIAL or 0
                if aplicar == 0
                else (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            )

            if dias != 0.0:
                # =================================================
                # TOPE SALARIAL
                # Si el contrato tiene marcada la excepción de tope:
                #   paga sin validar wage ni devengado.
                # Si no: solo paga si wage <= tope Y devengado <= tope.
                # =================================================
                if version.not_validate_top_auxtransportation == True:
                    result = round(dias * auxtransporte / 30)
                elif version.wage <= auxtransporte_tope and total <= auxtransporte_tope:
                    result = round(dias * auxtransporte / 30)
#---------------------------------------Auxilio de transporte turnos SERVAGRO--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX000TURNOS',employee.type_employee.id)
if obj_salary_rule and version.subcontract_type in ('obra_parcial','obra_integral'):
    auxtransporte = annual_parameters.transportation_assistance_monthly
    #auxtransporte_tope = annual_parameters.top_max_transportation_assistance
    obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
    if obj_overtime:
        if obj_overtime.days_actually_worked > 0:
        #if (version.wage <= auxtransporte_tope) and (total <= auxtransporte_tope):
            result = auxtransporte/30
            result_qty = obj_overtime.days_actually_worked
#---------------------------------------Viaticos prestacionales SERVAGRO // Molpartes, Sole--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VIATICOS_PRESTACIONALES',employee.type_employee.id)
if obj_salary_rule and rules_computed.dict.get('VIATICOS_TOTAL', 0) > 0:
    total = (categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL) - rules_computed.dict.get('VIATICOS_TOTAL', 0)
    forty_percent = total*0.4
    if rules_computed.dict.get('VIATICOS_TOTAL', 0) > forty_percent:
        result = rules_computed.dict.get('VIATICOS_TOTAL', 0) - forty_percent
    else:
        result = rules_computed.dict.get('VIATICOS_TOTAL', 0)

#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VIATICOS_PRESTACIONALES',employee.type_employee.id)
if obj_salary_rule and rules_computed.dict.get('VIATICOS_TOTAL', 0) > 0:
    total = ((categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0)) - rules_computed.dict.get('VIATICOS_TOTAL', 0)
    forty_percent = total*0.4
    if rules_computed.dict.get('VIATICOS_TOTAL', 0) > forty_percent:
        result = rules_computed.dict.get('VIATICOS_TOTAL', 0) - forty_percent
    else:
        result = rules_computed.dict.get('VIATICOS_TOTAL', 0)
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VIATICOS_PRESTACIONALES', employee.type_employee.id)
if obj_salary_rule and rules_computed.dict.get('VIATICOS_TOTAL', 0) > 0:
    total = (categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL) - rules_computed.dict.get('VIATICOS_TOTAL', 0)
    forty_percent = total*0.4
    if rules_computed.dict.get('VIATICOS_TOTAL', 0) > forty_percent:
        result = rules_computed.dict.get('VIATICOS_TOTAL', 0) - forty_percent
    else:
        result = rules_computed.dict.get('VIATICOS_TOTAL', 0)
#---------------------------------------Viaticos NO prestacionales SERVAGRO--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VIATICOS_NO_PRESTACIONALES',employee.type_employee.id)
if obj_salary_rule and rules_computed.dict.get('VIATICOS_PRESTACIONALES', 0) > 0:
    result = rules_computed.dict.get('VIATICOS_TOTAL', 0) - rules_computed.dict.get('VIATICOS_PRESTACIONALES', 0)
#-----------Viaticos totales SERVAGRO // Utilizados en los viaticos y cargados desde novedades diferentes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VIATICOS_TOTAL',employee.type_employee.id)
if obj_salary_rule and rules_computed.dict.get('VIATICOS_TOTAL', 0) > 0:
    result = rules_computed.dict.get('VIATICOS_TOTAL', 0)*-1
#---------------------------------------Salud Empleado--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL001',employee.type_employee.id)
liquidated_eps_employee = payslip.get_parameterization_contributors().liquidated_eps_employee if len(payslip.get_parameterization_contributors()) > 0 else True
if obj_salary_rule and liquidated_eps_employee and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        porc = annual_parameters.value_porc_health_employee/100
        total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        total_validation = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        #Ley 1393
        if payslip.date_from.day > 15 or (inherit_contrato != 0):
            total_salarial = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from,
                                                                               payslip.date_to)
            auxtransporte = AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
            vac_no_salarial = categories.VNS + + payslip.sum_mount('VNS', payslip.date_from,payslip.date_to)
            total_no_salarial = categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,
                                                                               payslip.date_to) - auxtransporte - vac_no_salarial
            gran_total = total_salarial + total_no_salarial
            statute_value = (gran_total/100)*annual_parameters.value_porc_statute_1395
            total_statute = total_no_salarial-statute_value
            if total_statute > 0:
                total += total_statute
        # Fin Ley 1393
        dias_work = payslip.sum_days_contribution_base(payslip.date_from, payslip.date_to)
        dias_work_act = 0
        for wd in worked_days.dict.values():
            dias_work_act += wd.number_of_days if wd.work_entry_type_id.not_contribution_base == False else 0
        dias_validation = dias_work + dias_work_act
        dias_validation = dias_validation if dias_validation > 0 else 1
        dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
        top_twenty_five_smmlv = (annual_parameters.top_twenty_five_smmlv / 30) * dias_validation
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary/100
            total = total*porc_integral_salary
            total_validation = total_validation * porc_integral_salary
            total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
        else:
            total = ((annual_parameters.top_twenty_five_smmlv / 30) * dias_work_act) if total_validation >= top_twenty_five_smmlv else total
            #Validar que el aporte sea almenos por el smlv cuando la modalidad de salario sea basico
            salario_minimo = annual_parameters.smmlv_monthly
            if version.modality_salary == 'basico' and version.wage < salario_minimo and total > 0:
                salario_minimo = salario_minimo / 30
                salario_minimo = salario_minimo*dias_work
                total = salario_minimo if total < salario_minimo else total
        result = (round((total)*porc) if round((total)*porc) % 100 == 0 else round((total)*porc) + 100 - round((total)*porc) % 100)*-1

#V17
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL001',employee.type_employee.id)
liquidated_eps_employee = payslip.get_parameterization_contributors().liquidated_eps_employee if len(payslip.get_parameterization_contributors()) > 0 else True
if obj_salary_rule and liquidated_eps_employee and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        porc = annual_parameters.value_porc_health_employee/100
        total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        total_validation = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        # Incluir indemnización de contrato indefinido a la base solo en liquidación de contrato
        indemnizacion_indefinido = 0.0
        if rules_computed.INDEMNIZACION:
            indemnizacion_indefinido = rules_computed.INDEMNIZACION or 0.0
        else:
            indemnizacion_indefinido = payslip.sum_mount_x_rule('INDEMNIZACION', payslip.date_from, payslip.date_to) or 0.0
        if inherit_contrato != 0:
            total += indemnizacion_indefinido
            total_validation += indemnizacion_indefinido
        #Ley 1393
        if total_validation > 0 and (payslip.date_from.day > 0 or (inherit_contrato != 0)):
            total_salarial = categories.DEV_SALARIAL #+ payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            auxtransporte = rules_computed.AUX000#+ payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
            vac_no_salarial = categories.VNS #+ payslip.sum_mount('VNS', payslip.date_from,payslip.date_to)
            total_no_salarial = categories.DEV_NO_SALARIAL - auxtransporte - vac_no_salarial #+ payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            gran_total = total_salarial + total_no_salarial
            statute_value = (gran_total/100)*annual_parameters.value_porc_statute_1395
            total_statute = total_no_salarial-statute_value
            if total_statute > 0:
                total += total_statute
        # Fin Ley 1393
        dias_work = payslip.sum_days_contribution_base(payslip.date_from, payslip.date_to)
        dias_work_act = 0
        for wd in worked_days.dict.values():
            dias_work_act += wd.number_of_days if wd.work_entry_type_id.not_contribution_base == False else 0
        dias_validation = dias_work + dias_work_act
        dias_validation = dias_validation if dias_validation > 0 else 1
        dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
        top_twenty_five_smmlv = (annual_parameters.top_twenty_five_smmlv / 30) * dias_validation
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary/100
            total = total*porc_integral_salary
            total_validation = total_validation * porc_integral_salary
            total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
        else:
            total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
            #Validar que el aporte sea almenos por el smlv cuando la modalidad de salario sea basico
            salario_minimo = annual_parameters.smmlv_monthly
            if version.modality_salary == 'basico' and version.wage < salario_minimo and total > 0:
                salario_minimo = salario_minimo / 30
                salario_minimo = salario_minimo*dias_work
                total = salario_minimo if total < salario_minimo else total
        result = round((total)*porc)*-1 if not annual_parameters.weight_contribution_calculations else (round((total)*porc) if round((total)*porc) % 100 == 0 else round((total)*porc) + 100 - round((total)*porc) % 100)*-1

#V19
# =====================================================================
# SSOCIAL001 — Salud Empleado (UNIFICADA) — Odoo 19
# Único código para desplegar en Molpartes / Tkarga / AlianzaT / Servagro
# ---------------------------------------------------------------------
# Decisiones de unificación:
#  - Entrada:            liquidated_eps_employee (NO contract_type)
#  - Objeto contrato:    SIEMPRE version
#  - Ley 1393/1395:      total_validation > 0  (estilo Molpartes/Tkarga)
#  - Tope 25 SMMLV:      SIEMPRE prorrateado /30 * dias_validation
#  - Piso SMMLV:         SIEMPRE (rama no integral)
#  - Resta 1ª quincena:  SOLO si aplicar == 0 (cobro quincenal/"Siempre")
#  - Redondeo:           configurable por weight_contribution_calculations
#  - Cotizante 51:       rama por horas (Tkarga)
#  - IBC mes anterior/vacaciones: rama Molpartes (gated z_enable_ibc_previous_month)
# =====================================================================
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL001', employee.type_employee.id)
liquidated_eps_employee = payslip.get_parameterization_contributors().liquidated_eps_employee if len(payslip.get_parameterization_contributors()) > 0 else True
 
if obj_salary_rule and liquidated_eps_employee:
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)
 
    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        porc = annual_parameters.value_porc_health_employee / 100
 
        # =============================================================
        # RAMA A — Cotizante 51 (cálculo por horas)  [Tkarga]
        # Cortocircuita el resto del flujo (sin Ley1393/tope/piso).
        # =============================================================
        if employee.tipo_coti_id.code == '51':
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime and obj_overtime.shift_hours > 0:
                days = obj_overtime.shift_hours / 8
                total = payslip.get_payroll_value_contributor_51(payslip.date_from.year, days)
                result = (round(total * porc) * -1) if not annual_parameters.weight_contribution_calculations else ((round(total * porc) if round(total * porc) % 100 == 0 else round(total * porc) + 100 - round(total * porc) % 100) * -1)
                if aplicar == 0 and inherit_contrato == 0:
                    salud_primera_quincena = payslip.sum_mount_x_rule('SSOCIAL001', payslip.date_from.replace(day=1), payslip.date_to)
                    result = result - salud_primera_quincena
 
        # =============================================================
        # RAMA B — Resto de cotizantes
        # =============================================================
        else:
            total = 0.0
            total_validation = 0.0
 
            # ---- B.1  IBC mes anterior + vacaciones disfrutadas (regla computada) [Molpartes] ----
            if annual_parameters.z_enable_ibc_previous_month and (worked_days.VACDISFRUTADAS or 0) and (rules_computed.dict.get('VACDISFRUTADAS', 0) > 0):
                total = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                total_validation = total
                if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                    total_salarial = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                    auxtransporte = rules_computed.AUX000
                    vac_no_salarial = payslip.sum_mount_before('VNS', payslip.date_from)
                    total_no_salarial = payslip.sum_mount_before('DEV_NO_SALARIAL', payslip.date_from) - auxtransporte - vac_no_salarial
                    gran_total = total_salarial + total_no_salarial
                    statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                    total_statute = total_no_salarial - statute_value
                    if total_statute > 0:
                        total += total_statute
                total = total / 30 * leaves.VACDISFRUTADAS
 
            # ---- B.2  IBC vacaciones (estructura 'vacaciones') o estándar [Molpartes] ----
            elif annual_parameters.z_enable_ibc_previous_month and (worked_days.VACDISFRUTADAS or 0):
                if payslip.struct_id.process == 'vacaciones':
                    total = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                    total_validation = total
                    if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                        total_salarial = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                        auxtransporte = rules_computed.AUX000
                        vac_no_salarial = payslip.sum_mount_before('VNS', payslip.date_from)
                        total_no_salarial = payslip.sum_mount_before('DEV_NO_SALARIAL', payslip.date_from) - auxtransporte - vac_no_salarial
                        gran_total = total_salarial + total_no_salarial
                        statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                        total_statute = total_no_salarial - statute_value
                        if total_statute > 0:
                            total += total_statute
                    total = total / 30 * leaves.VACDISFRUTADAS
                else:
                    total = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                    total_validation = total
                    if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                        total_salarial = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                        auxtransporte = rules_computed.AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
                        vac_no_salarial = (categories.VNS or 0) + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
                        total_no_salarial = (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) - auxtransporte - vac_no_salarial
                        gran_total = total_salarial + total_no_salarial
                        statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                        total_statute = total_no_salarial - statute_value
                        if total_statute > 0:
                            total += total_statute
 
            # ---- B.3  IBC estándar (devengado del periodo) [Tkarga/Servagro/AlianzaT normalizado] ----
            else:
                total = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                total_validation = total
                if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                    total_salarial = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                    auxtransporte = rules_computed.AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
                    vac_no_salarial = (categories.VNS or 0) + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
                    total_no_salarial = (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) - auxtransporte - vac_no_salarial
                    gran_total = total_salarial + total_no_salarial
                    statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                    total_statute = total_no_salarial - statute_value
                    if total_statute > 0:
                        total += total_statute
 
            # ---- Cola común B: días, tope 25 SMMLV (prorrateado), integral, piso, redondeo, resta 1ª quincena ----
            if total_validation > 0:
                dias_work = payslip.sum_days_contribution_base(payslip.date_from, payslip.date_to)
                dias_work_act = 0
                for wd in worked_days.dict.values():
                    dias_work_act += wd.number_of_days if wd.work_entry_type_id.not_contribution_base == False else 0
                dias_validation = dias_work + dias_work_act
                dias_validation = dias_validation if dias_validation > 0 else 1
                dias_work = dias_work_act if aplicar == 0 else dias_work + dias_work_act
                top_twenty_five_smmlv = annual_parameters.top_twenty_five_smmlv / 30 * dias_validation
                if version.modality_salary == 'integral':
                    porc_integral_salary = annual_parameters.porc_integral_salary / 100
                    total = total * porc_integral_salary
                    total_validation = total_validation * porc_integral_salary
                    total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
                else:
                    total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
                    salario_minimo = annual_parameters.smmlv_monthly
                    if version.modality_salary == 'basico' and version.wage < salario_minimo and total > 0:
                        salario_minimo = salario_minimo / 30
                        salario_minimo = salario_minimo * dias_work
                        total = salario_minimo if total < salario_minimo else total
                result = (round(total * porc) * -1) if not annual_parameters.weight_contribution_calculations else ((round(total * porc) if round(total * porc) % 100 == 0 else round(total * porc) + 100 - round(total * porc) % 100) * -1)
                if aplicar == 0 and inherit_contrato == 0:
                    salud_primera_quincena = payslip.sum_mount_x_rule('SSOCIAL001', payslip.date_from.replace(day=1), payslip.date_to)
                    result = result - salud_primera_quincena
#---------------------------------------Pension Empleado--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL002',employee.type_employee.id)
liquidate_employee_pension = payslip.get_parameterization_contributors().liquidate_employee_pension if len(payslip.get_parameterization_contributors()) > 0 else True
if obj_salary_rule and liquidate_employee_pension and version.contract_type != 'aprendizaje' and employee.subtipo_coti_id.not_contribute_pension == False:
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        porc = annual_parameters.value_porc_pension_employee/100
        if employee.tipo_coti_id.code != '51':
            total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            total_validation = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from,payslip.date_to)
            # Ley 1393
            if payslip.date_from.day > 15 or (inherit_contrato != 0):
                total_salarial = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from,
                                                                             payslip.date_to)
                auxtransporte = AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
                vac_no_salarial = categories.VNS + + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
                total_no_salarial = categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,
                                                                                   payslip.date_to) - auxtransporte - vac_no_salarial
                gran_total = total_salarial + total_no_salarial
                statute_value = (gran_total / 100) * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute
            # Fin Ley 1393
            dias_work = payslip.sum_days_contribution_base(payslip.date_from, payslip.date_to)
            dias_work_act = 0
            for wd in worked_days.dict.values():
                dias_work_act += wd.number_of_days if wd.work_entry_type_id.not_contribution_base == False else 0
            dias_validation = dias_work + dias_work_act
            dias_validation = dias_validation if dias_validation > 0 else 1
            dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
            top_twenty_five_smmlv = (annual_parameters.top_twenty_five_smmlv / 30) * dias_validation
            if version.modality_salary == 'integral':
                porc_integral_salary = annual_parameters.porc_integral_salary / 100
                total = total * porc_integral_salary
                total_validation = total_validation * porc_integral_salary
                total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
            else:
                total = ((annual_parameters.top_twenty_five_smmlv / 30) * dias_work_act) if total_validation >= top_twenty_five_smmlv else total
                # Validar que el aporte sea almenos por el smlv cuando la modalidad de salario sea basico
                salario_minimo = annual_parameters.smmlv_monthly
                if version.modality_salary == 'basico' and version.wage < salario_minimo and total > 0:
                    salario_minimo = salario_minimo / 30
                    salario_minimo = salario_minimo * dias_work
                    total = salario_minimo if total < salario_minimo else total
            result = (round((total)*porc) if round((total)*porc) % 100 == 0 else round((total)*porc) + 100 - round((total)*porc) % 100)*-1
        elif employee.tipo_coti_id.code == '51':
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_overtime.shift_hours > 0:
                    days = obj_overtime.shift_hours / 8
                    total = payslip.get_payroll_value_contributor_51(payslip.date_from.year,days)
                    result = (round((total)*porc) if round((total)*porc) % 100 == 0 else round((total)*porc) + 100 - round((total)*porc) % 100)*-1

#V17
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL002',employee.type_employee.id)
liquidate_employee_pension = payslip.get_parameterization_contributors().liquidate_employee_pension if len(payslip.get_parameterization_contributors()) > 0 else True
if obj_salary_rule and liquidate_employee_pension and version.contract_type != 'aprendizaje' and employee.subtipo_coti_id.not_contribute_pension == False:
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        porc = annual_parameters.value_porc_pension_employee/100
        if employee.tipo_coti_id.code != '51':
            total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            total_validation = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from,payslip.date_to)
            # Incluir indemnización de contrato indefinido a la base solo en liquidación de contrato
            indemnizacion_indefinido = 0.0
            if rules_computed.INDEMNIZACION:
                indemnizacion_indefinido = rules_computed.INDEMNIZACION or 0.0
            else:
                indemnizacion_indefinido = payslip.sum_mount_x_rule('INDEMNIZACION', payslip.date_from, payslip.date_to) or 0.0
            if inherit_contrato != 0:
                total += indemnizacion_indefinido
                total_validation += indemnizacion_indefinido
            # Ley 1393
            if total_validation > 0 and (payslip.date_from.day > 0 or (inherit_contrato != 0)):
                total_salarial = categories.DEV_SALARIAL #+ payslip.sum_mount('DEV_SALARIAL', payslip.date_from,payslip.date_to)
                auxtransporte = rules_computed.AUX000 #+ payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
                vac_no_salarial = categories.VNS #+ payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
                total_no_salarial = categories.DEV_NO_SALARIAL - auxtransporte - vac_no_salarial #+ payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,payslip.date_to)
                gran_total = total_salarial + total_no_salarial
                statute_value = (gran_total / 100) * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute
            # Fin Ley 1393
            dias_work = payslip.sum_days_contribution_base(payslip.date_from, payslip.date_to)
            dias_work_act = 0
            for wd in worked_days.dict.values():
                dias_work_act += wd.number_of_days if wd.work_entry_type_id.not_contribution_base == False else 0
            dias_validation = dias_work + dias_work_act
            dias_validation = dias_validation if dias_validation > 0 else 1
            dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
            top_twenty_five_smmlv = (annual_parameters.top_twenty_five_smmlv / 30) * dias_validation
            if version.modality_salary == 'integral':
                porc_integral_salary = annual_parameters.porc_integral_salary / 100
                total = total * porc_integral_salary
                total_validation = total_validation * porc_integral_salary
                total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
            else:
                total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
                # Validar que el aporte sea almenos por el smlv cuando la modalidad de salario sea basico
                salario_minimo = annual_parameters.smmlv_monthly
                if version.modality_salary == 'basico' and version.wage < salario_minimo and total > 0:
                    salario_minimo = salario_minimo / 30
                    salario_minimo = salario_minimo * dias_work
                    total = salario_minimo if total < salario_minimo else total
            result = round((total)*porc)*-1 if not annual_parameters.weight_contribution_calculations else (round((total)*porc) if round((total)*porc) % 100 == 0 else round((total)*porc) + 100 - round((total)*porc) % 100)*-1
        elif employee.tipo_coti_id.code == '51':
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_overtime.shift_hours > 0:
                    days = obj_overtime.shift_hours / 8
                    total = payslip.get_payroll_value_contributor_51(payslip.date_from.year,days)
                    result = round((total)*porc)*-1 if not annual_parameters.weight_contribution_calculations else (round((total)*porc) if round((total)*porc) % 100 == 0 else round((total)*porc) + 100 - round((total)*porc) % 100)*-1

#V19
# =====================================================================
# SSOCIAL002 — Pensión Empleado (UNIFICADA) — Odoo 19
# Único código para desplegar en Molpartes / Tkarga / AlianzaT / Servagro
# ---------------------------------------------------------------------
# Decisiones de unificación (alineadas a SSOCIAL001 salud):
#  - Entrada:            liquidate_employee_pension (NO contract_type)
#  - Exclusión:          subtipo_coti_id.not_contribute_pension
#  - Objeto contrato:    SIEMPRE version
#  - Ley 1393/1395:      total_validation > 0  (estilo Molpartes/Tkarga)
#  - Tope 25 SMMLV:      SIEMPRE prorrateado /30 * dias_validation
#  - Piso SMMLV:         SIEMPRE (rama no integral)
#  - Resta 1ª quincena:  SOLO si aplicar == 0 y inherit_contrato == 0
#  - Redondeo:           configurable por weight_contribution_calculations
#  - Cotizante 51:       rama por horas (Tkarga / Servagro / Molpartes)
#  - IBC mes anterior/vacaciones: rama Molpartes (gated z_enable_ibc_previous_month)
# =====================================================================

result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL002', employee.type_employee.id)
liquidate_employee_pension = (
    payslip.get_parameterization_contributors().liquidate_employee_pension
    if len(payslip.get_parameterization_contributors()) > 0
    else True
)

if obj_salary_rule and liquidate_employee_pension and (not employee.subtipo_coti_id.not_contribute_pension):
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)

    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        porc = annual_parameters.value_porc_pension_employee / 100

        # =============================================================
        # RAMA A — Cotizante 51 (cálculo por horas)
        # Cortocircuita el resto del flujo (sin Ley1393/tope/piso).
        # =============================================================
        if employee.tipo_coti_id.code == '51':
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime and obj_overtime.shift_hours > 0:
                days = obj_overtime.shift_hours / 8
                total = payslip.get_payroll_value_contributor_51(payslip.date_from.year, days)
                result = (
                    (round(total * porc) * -1)
                    if not annual_parameters.weight_contribution_calculations
                    else (
                        (round(total * porc) if round(total * porc) % 100 == 0
                         else round(total * porc) + 100 - round(total * porc) % 100) * -1
                    )
                )
                if aplicar == 0 and inherit_contrato == 0:
                    pension_primera_quincena = payslip.sum_mount_x_rule(
                        'SSOCIAL002', payslip.date_from.replace(day=1), payslip.date_to
                    )
                    result = result - pension_primera_quincena

        # =============================================================
        # RAMA B — Resto de cotizantes
        # =============================================================
        else:
            total = 0.0
            total_validation = 0.0

            # ---- B.1  IBC mes anterior + vacaciones disfrutadas (regla computada) [Molpartes] ----
            if (
                annual_parameters.z_enable_ibc_previous_month
                and (worked_days.VACDISFRUTADAS or 0)
                and (rules_computed.dict.get('VACDISFRUTADAS', 0) > 0)
            ):
                total = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                total_validation = total
                if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                    total_salarial    = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                    auxtransporte     = rules_computed.AUX000
                    vac_no_salarial   = payslip.sum_mount_before('VNS', payslip.date_from)
                    total_no_salarial = (
                        payslip.sum_mount_before('DEV_NO_SALARIAL', payslip.date_from)
                        - auxtransporte - vac_no_salarial
                    )
                    gran_total     = total_salarial + total_no_salarial
                    statute_value  = gran_total / 100 * annual_parameters.value_porc_statute_1395
                    total_statute  = total_no_salarial - statute_value
                    if total_statute > 0:
                        total += total_statute
                total = total / 30 * leaves.VACDISFRUTADAS

            # ---- B.2  IBC vacaciones (estructura 'vacaciones') o estándar [Molpartes] ----
            elif annual_parameters.z_enable_ibc_previous_month and (worked_days.VACDISFRUTADAS or 0):
                if payslip.struct_id.process == 'vacaciones':
                    total = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                    total_validation = total
                    if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                        total_salarial    = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                        auxtransporte     = rules_computed.AUX000
                        vac_no_salarial   = payslip.sum_mount_before('VNS', payslip.date_from)
                        total_no_salarial = (
                            payslip.sum_mount_before('DEV_NO_SALARIAL', payslip.date_from)
                            - auxtransporte - vac_no_salarial
                        )
                        gran_total     = total_salarial + total_no_salarial
                        statute_value  = gran_total / 100 * annual_parameters.value_porc_statute_1395
                        total_statute  = total_no_salarial - statute_value
                        if total_statute > 0:
                            total += total_statute
                    total = total / 30 * leaves.VACDISFRUTADAS
                else:
                    total = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                    total_validation = total
                    if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                        total_salarial    = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                        auxtransporte     = rules_computed.AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
                        vac_no_salarial   = (categories.VNS or 0) + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
                        total_no_salarial = (
                            (categories.DEV_NO_SALARIAL or 0)
                            + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
                            - auxtransporte - vac_no_salarial
                        )
                        gran_total     = total_salarial + total_no_salarial
                        statute_value  = gran_total / 100 * annual_parameters.value_porc_statute_1395
                        total_statute  = total_no_salarial - statute_value
                        if total_statute > 0:
                            total += total_statute

            # ---- B.3  IBC estándar (devengado del periodo) [Tkarga / Servagro / AlianzaT normalizado] ----
            else:
                total = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                total_validation = total
                if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                    total_salarial    = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                    auxtransporte     = rules_computed.AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
                    vac_no_salarial   = (categories.VNS or 0) + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
                    total_no_salarial = (
                        (categories.DEV_NO_SALARIAL or 0)
                        + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
                        - auxtransporte - vac_no_salarial
                    )
                    gran_total     = total_salarial + total_no_salarial
                    statute_value  = gran_total / 100 * annual_parameters.value_porc_statute_1395
                    total_statute  = total_no_salarial - statute_value
                    if total_statute > 0:
                        total += total_statute

            # ---- Cola común B: días, tope 25 SMMLV (prorrateado), integral, piso, redondeo, resta 1ª quincena ----
            if total_validation > 0:
                dias_work = payslip.sum_days_contribution_base(payslip.date_from, payslip.date_to)
                dias_work_act = 0
                for wd in worked_days.dict.values():
                    dias_work_act += wd.number_of_days if not wd.work_entry_type_id.not_contribution_base else 0
                dias_validation = dias_work + dias_work_act
                dias_validation = dias_validation if dias_validation > 0 else 1
                dias_work = dias_work_act if aplicar == 0 else dias_work + dias_work_act

                top_twenty_five_smmlv = annual_parameters.top_twenty_five_smmlv / 30 * dias_validation

                if version.modality_salary == 'integral':
                    porc_integral_salary  = annual_parameters.porc_integral_salary / 100
                    total                 = total * porc_integral_salary
                    total_validation      = total_validation * porc_integral_salary
                    total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
                else:
                    total = top_twenty_five_smmlv if total_validation >= top_twenty_five_smmlv else total
                    salario_minimo = annual_parameters.smmlv_monthly
                    if version.modality_salary == 'basico' and version.wage < salario_minimo and total > 0:
                        salario_minimo = salario_minimo / 30 * dias_work
                        total = salario_minimo if total < salario_minimo else total

                result = (
                    (round(total * porc) * -1)
                    if not annual_parameters.weight_contribution_calculations
                    else (
                        (round(total * porc) if round(total * porc) % 100 == 0
                         else round(total * porc) + 100 - round(total * porc) % 100) * -1
                    )
                )
                if aplicar == 0 and inherit_contrato == 0:
                    pension_primera_quincena = payslip.sum_mount_x_rule(
                        'SSOCIAL002', payslip.date_from.replace(day=1), payslip.date_to
                    )
                    result = result - pension_primera_quincena
# ---------------------------------------Fondo subsistencia--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL003',employee.type_employee.id)
liquidates_solidarity_fund = payslip.get_parameterization_contributors().liquidates_solidarity_fund if len(payslip.get_parameterization_contributors()) > 0 else True
if obj_salary_rule and liquidates_solidarity_fund and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        salario_minimo = annual_parameters.smmlv_monthly
        total = categories.DEV_SALARIAL if aplicar == 0 and inherit_contrato==0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        # Ley 1393
        if payslip.date_from.day > 15 or (inherit_contrato != 0):
            total_salarial = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from,
                                                                         payslip.date_to)
            auxtransporte = AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
            vac_no_salarial = categories.VNS + + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
            total_no_salarial = categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,
                                                                               payslip.date_to) - auxtransporte - vac_no_salarial
            gran_total = total_salarial + total_no_salarial
            statute_value = (gran_total / 100) * annual_parameters.value_porc_statute_1395
            total_statute = total_no_salarial - statute_value
            if total_statute > 0:
                total += total_statute
        # Fin Ley 1393
        dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        dias_work_act = worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
        dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
        top_twenty_five_smmlv = annual_parameters.top_twenty_five_smmlv#(annual_parameters.top_twenty_five_smmlv / 30) * dias_work
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary / 100
            total = total * porc_integral_salary
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        else:
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        if (total/salario_minimo) >= 4 and (total/salario_minimo) < 16:
            result =  payslip.roundup100(total * 0.005 * (-1))
        if  (total/salario_minimo) >= 16 and (total/salario_minimo) <= 17:
            result =  payslip.roundup100(total * 0.007 * (-1))
        if  (total/salario_minimo) > 17 and (total/salario_minimo) <= 18:
            result =  payslip.roundup100(total * 0.009 * (-1))
        if  (total/salario_minimo) > 18 and (total/salario_minimo) <= 19:
            result =  payslip.roundup100(total * 0.01 * (-1))
        if  (total/salario_minimo) > 19 and (total/salario_minimo) <= 20:
            result =  payslip.roundup100(total * 0.013 * (-1))
        if  (total/salario_minimo) > 20 and (total/salario_minimo) <= 25:
            result =  payslip.roundup100(total * 0.015* (-1))
        if  (total/salario_minimo) > 25:
            result =  payslip.roundup100(salario_minimo * 25 * 0.01* (-1))

        if result != 0:
            value_period = payslip.sum('SSOCIAL003', payslip.date_from, payslip.date_to)
            result = result - value_period
#V19
# =====================================================================
# SSOCIAL003 — Fondo de Subsistencia Pensional (UNIFICADA) — Odoo 19
# Único código para desplegar en Molpartes / Tkarga / AlianzaT / Servagro
# ---------------------------------------------------------------------
# Decisiones de unificación (espejo de SSOCIAL004 solidaridad):
#  - Entrada:            liquidates_solidarity_fund + contract_type != aprendizaje
#  - Objeto contrato:    SIEMPRE version
#  - Ley 1393/1395:      total_validation > 0  (estilo Molpartes/Tkarga)
#  - Tope 25 SMMLV:      prorrateado /30 * dias_work (WORK100)
#                        Solo se ve afectado en ingreso/retiro (< 30 días WORK100)
#  - Tarifa:             leída de grilla z_fds_lines_ids en annual_parameters
#                        campo z_porcentage_subsistence_fund por rango de SMMLV
#  - Resta cobros previos: SIEMPRE vía sum_mount_x_rule('SSOCIAL003', ...)
#  - Redondeo:           round(..., -2)
#  - IBC mes anterior/vacaciones: rama Molpartes (gated z_enable_ibc_previous_month)
# ---------------------------------------------------------------------
# Diferencia con SSOCIAL004:
#  - Código de regla:    SSOCIAL003
#  - Campo porcentaje:   z_porcentage_subsistence_fund  (en lugar de z_porcentage_solidarity_fund)
#  - Variable resta:     subsistencia_primera_quincena
# =====================================================================

result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL003', employee.type_employee.id)
liquidates_solidarity_fund = (
    payslip.get_parameterization_contributors().liquidates_solidarity_fund
    if len(payslip.get_parameterization_contributors()) > 0
    else True
)

if obj_salary_rule and liquidates_solidarity_fund and (version.contract_type != 'aprendizaje'):
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)

    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        salario_minimo = annual_parameters.smmlv_monthly
        total = 0.0
        total_validation = 0.0

        # =============================================================
        # BASE IBC — B.1  Mes anterior + vacaciones disfrutadas [Molpartes]
        # =============================================================
        if annual_parameters.z_enable_ibc_previous_month and (worked_days.VACDISFRUTADAS or 0):
            total = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            total_validation = total
            if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                total_salarial    = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                auxtransporte     = rules_computed.AUX000
                vac_no_salarial   = payslip.sum_mount_before('VNS', payslip.date_from)
                total_no_salarial = (
                    payslip.sum_mount_before('DEV_NO_SALARIAL', payslip.date_from)
                    - auxtransporte - vac_no_salarial
                )
                gran_total    = total_salarial + total_no_salarial
                statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute
            total = total / 30 * leaves.VACDISFRUTADAS

        # =============================================================
        # BASE IBC — B.2  Devengado del periodo [Tkarga / Molpartes estándar]
        # =============================================================
        else:
            total = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            total_validation = total
            if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                total_salarial    = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                auxtransporte     = rules_computed.AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
                vac_no_salarial   = (categories.VNS or 0) + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
                total_no_salarial = (
                    (categories.DEV_NO_SALARIAL or 0)
                    + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
                    - auxtransporte - vac_no_salarial
                )
                gran_total    = total_salarial + total_no_salarial
                statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute

        # =============================================================
        # DÍAS WORK100 — para prorrateo del tope
        # Solo WORK100; el tope se ve reducido únicamente en ingreso/retiro
        # =============================================================
        dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        dias_work_act = (worked_days.WORK100 or 0).number_of_days if (worked_days.WORK100 or 0) else 0
        dias_work = dias_work_act if aplicar == 0 else dias_work + dias_work_act

        # =============================================================
        # TOPE 25 SMMLV — prorrateado por días WORK100
        # =============================================================
        top_twenty_five_smmlv = annual_parameters.top_twenty_five_smmlv / 30 * dias_work

        # =============================================================
        # SALARIO INTEGRAL — aplica factor antes del tope
        # =============================================================
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary / 100
            total = total * porc_integral_salary

        total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total

        # =============================================================
        # TARIFA — leída de grilla z_fds_lines_ids
        # Compara total/salario_minimo contra z_initial_value/z_final_value
        # Aplica z_porcentage_subsistence_fund del rango correspondiente
        # =============================================================
        if total > 0 and salario_minimo > 0:
            ratio = total / salario_minimo
            porc_subsistencia = 0.0
            fds_lines = annual_parameters.z_fds_lines_ids
            for line in fds_lines:
                if line.z_initial_value <= ratio <= line.z_final_value:
                    porc_subsistencia = line.z_porcentage_subsistence_fund / 100
                    break

            if porc_subsistencia > 0:
                cobro_previo = payslip.sum_mount_x_rule(
                    'SSOCIAL003', payslip.date_from, payslip.date_to
                )
                result = round(total * porc_subsistencia * -1, -2) - cobro_previo
#---------------------------------------Fondo Solidadridad--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL004',employee.type_employee.id)
liquidates_solidarity_fund = payslip.get_parameterization_contributors().liquidates_solidarity_fund if len(payslip.get_parameterization_contributors()) > 0 else True
if obj_salary_rule and liquidates_solidarity_fund and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        salario_minimo = annual_parameters.smmlv_monthly
        total = categories.DEV_SALARIAL if aplicar == 0 and inherit_contrato==0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        # Ley 1393
        if payslip.date_from.day > 15 or (inherit_contrato != 0):
            total_salarial = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from,
                                                                         payslip.date_to)
            auxtransporte = AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
            vac_no_salarial = categories.VNS + + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
            total_no_salarial = categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,
                                                                               payslip.date_to) - auxtransporte - vac_no_salarial
            gran_total = total_salarial + total_no_salarial
            statute_value = (gran_total / 100) * annual_parameters.value_porc_statute_1395
            total_statute = total_no_salarial - statute_value
            if total_statute > 0:
                total += total_statute
        # Fin Ley 1393
        dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        dias_work_act = worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
        dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
        top_twenty_five_smmlv = annual_parameters.top_twenty_five_smmlv#(annual_parameters.top_twenty_five_smmlv / 30) * dias_work
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary / 100
            total = total * porc_integral_salary
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        else:
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        if (total/salario_minimo) >= 4:
            value_period = payslip.sum('SSOCIAL004', payslip.date_from, payslip.date_to)
            result =  (payslip.roundup100(total * 0.005 * (-1)) - value_period)
#V19
# =====================================================================
# SSOCIAL004 — Fondo de Solidaridad Pensional (UNIFICADA) — Odoo 19
# Único código para desplegar en Molpartes / Tkarga / AlianzaT / Servagro
# ---------------------------------------------------------------------
# Decisiones de unificación:
#  - Entrada:            liquidates_solidarity_fund + contract_type != aprendizaje
#  - Objeto contrato:    SIEMPRE version
#  - Ley 1393/1395:      total_validation > 0  (estilo Molpartes/Tkarga)
#  - Tope 25 SMMLV:      prorrateado /30 * dias_work (WORK100)
#                        Solo se ve afectado en ingreso/retiro (< 30 días WORK100)
#  - Tarifa:             leída de grilla z_fds_lines_ids en annual_parameters
#                        (z_porcentage_solidarity_fund por rango de SMMLV)
#  - Resta cobros previos: SIEMPRE vía sum_mount_x_rule('SSOCIAL004', ...)
#  - Redondeo:           round(..., -2)  [centenas, consistente con Molpartes/AlianzaT]
#  - IBC mes anterior/vacaciones: rama Molpartes (gated z_enable_ibc_previous_month)
# =====================================================================

result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL004', employee.type_employee.id)
liquidates_solidarity_fund = (
    payslip.get_parameterization_contributors().liquidates_solidarity_fund
    if len(payslip.get_parameterization_contributors()) > 0
    else True
)

if obj_salary_rule and liquidates_solidarity_fund and (version.contract_type != 'aprendizaje'):
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)

    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        salario_minimo = annual_parameters.smmlv_monthly
        total = 0.0
        total_validation = 0.0

        # =============================================================
        # BASE IBC — B.1  Mes anterior + vacaciones disfrutadas [Molpartes]
        # =============================================================
        if annual_parameters.z_enable_ibc_previous_month and (worked_days.VACDISFRUTADAS or 0):
            total = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            total_validation = total
            if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                total_salarial    = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                auxtransporte     = rules_computed.AUX000
                vac_no_salarial   = payslip.sum_mount_before('VNS', payslip.date_from)
                total_no_salarial = (
                    payslip.sum_mount_before('DEV_NO_SALARIAL', payslip.date_from)
                    - auxtransporte - vac_no_salarial
                )
                gran_total    = total_salarial + total_no_salarial
                statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute
            total = total / 30 * leaves.VACDISFRUTADAS

        # =============================================================
        # BASE IBC — B.2  Devengado del periodo [Tkarga / Molpartes estándar]
        # =============================================================
        else:
            total = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            total_validation = total
            if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                total_salarial    = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
                auxtransporte     = rules_computed.AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
                vac_no_salarial   = (categories.VNS or 0) + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
                total_no_salarial = (
                    (categories.DEV_NO_SALARIAL or 0)
                    + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
                    - auxtransporte - vac_no_salarial
                )
                gran_total    = total_salarial + total_no_salarial
                statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute

        # =============================================================
        # DÍAS WORK100 — para prorrateo del tope
        # Solo WORK100; el tope se ve reducido únicamente en ingreso/retiro
        # (cuando dias_work < 30). Vacaciones, licencias e incapacidades
        # no reducen el tope porque cuentan como WORK100 si aplica.
        # =============================================================
        dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        dias_work_act = (worked_days.WORK100 or 0).number_of_days if (worked_days.WORK100 or 0) else 0
        dias_work = dias_work_act if aplicar == 0 else dias_work + dias_work_act

        # =============================================================
        # TOPE 25 SMMLV — prorrateado por días WORK100
        # =============================================================
        top_twenty_five_smmlv = annual_parameters.top_twenty_five_smmlv / 30 * dias_work

        # =============================================================
        # SALARIO INTEGRAL — aplica factor antes del tope
        # =============================================================
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary / 100
            total = total * porc_integral_salary
        
        total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total

        # =============================================================
        # TARIFA — leída de grilla z_fds_lines_ids
        # Compara total/salario_minimo contra z_initial_value/z_final_value
        # Aplica z_porcentage_solidarity_fund del rango correspondiente
        # =============================================================
        if total > 0 and salario_minimo > 0:
            ratio = total / salario_minimo
            porc_solidaridad = 0.0
            fds_lines = annual_parameters.z_fds_lines_ids
            for line in fds_lines:
                if line.z_initial_value <= ratio <= line.z_final_value:
                    porc_solidaridad = line.z_porcentage_solidarity_fund / 100
                    break

            if porc_solidaridad > 0:
                cobro_previo = payslip.sum_mount_x_rule(
                    'SSOCIAL004', payslip.date_from, payslip.date_to
                )
                result = round(total * porc_solidaridad * -1, -2) - cobro_previo
# ---------------------------------------Fondo subsistencia // QUINCENAL SOLO TKARGA--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL003',employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        salario_minimo = annual_parameters.smmlv_monthly
        total_month = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        total = categories.DEV_SALARIAL if aplicar == 0 and inherit_contrato==0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        # Ley 1393
        if payslip.date_from.day > 15 or (inherit_contrato != 0):
            total_salarial = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from,
                                                                         payslip.date_to)
            auxtransporte = AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
            vac_no_salarial = categories.VNS + + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
            total_no_salarial = categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,
                                                                               payslip.date_to) - auxtransporte - vac_no_salarial
            gran_total = total_salarial + total_no_salarial
            statute_value = (gran_total / 100) * annual_parameters.value_porc_statute_1395
            total_statute = total_no_salarial - statute_value
            if total_statute > 0:
                total += total_statute
                total_month += total_statute
        # Fin Ley 1393
        dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        dias_work_act = worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
        dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
        top_twenty_five_smmlv = (annual_parameters.top_twenty_five_smmlv / 30) * dias_work
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary / 100
            total = total * porc_integral_salary
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        else:
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        if (total/salario_minimo) >= 2 and (total/salario_minimo) < 8:
            result =  (total * 0.005 * (-1))
        if  (total/salario_minimo) >= 8 and (total/salario_minimo) <= 8.5:
            result =  (total * 0.006 * (-1))
        if  (total/salario_minimo) > 8.5 and (total/salario_minimo) <= 9:
            result =  (total * 0.007 * (-1))
        if  (total/salario_minimo) > 9 and (total/salario_minimo) <= 9.5:
            result =  (total * 0.008 * (-1))
        if  (total/salario_minimo) > 9.5 and (total/salario_minimo) <= 10:
            result =  (total * 0.009 * (-1))
        if  (total/salario_minimo) > 10 and (total/salario_minimo) <= 12.5:
            result =  (total * 0.01* (-1))
        if  (total/salario_minimo) > 12.5:
            result =  (salario_minimo * 25 * 0.01* (-1))
        if payslip.date_from.day > 15 and not (total_month/salario_minimo) >= 4:
            result = 0

#V19
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL003', employee.type_employee.id)
liquidates_solidarity_fund = payslip.get_parameterization_contributors().liquidates_solidarity_fund if len(payslip.get_parameterization_contributors()) > 0 else True
if obj_salary_rule and liquidates_solidarity_fund and (version.contract_type != 'aprendizaje'):
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)
    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        salario_minimo = annual_parameters.smmlv_monthly
        if annual_parameters.z_enable_ibc_previous_month and (worked_days.VACDISFRUTADAS or 0):
            total = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            total_validation = total
            if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                total_salarial = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                auxtransporte = rules_computed.AUX000
                vac_no_salarial = payslip.sum_mount_before('VNS', payslip.date_from)
                total_no_salarial = payslip.sum_mount_before('DEV_NO_SALARIAL', payslip.date_from) - auxtransporte - vac_no_salarial
                gran_total = total_salarial + total_no_salarial
                statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute
            total = total / 30 * leaves.VACDISFRUTADAS
        else:
            total = categories.DEV_SALARIAL or 0 if aplicar == 0 else (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            total_validation = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                total_salarial = categories.DEV_SALARIAL or 0
                auxtransporte = rules_computed.AUX000
                vac_no_salarial = categories.VNS or 0
                total_no_salarial = (categories.DEV_NO_SALARIAL or 0) - auxtransporte - vac_no_salarial
                gran_total = total_salarial + total_no_salarial
                statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute
        dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        dias_work_act = (worked_days.WORK100 or 0).number_of_days if worked_days.WORK100 or 0 else 0
        dias_work = dias_work_act if aplicar == 0 else dias_work + dias_work_act
        top_twenty_five_smmlv = annual_parameters.top_twenty_five_smmlv / 30 * dias_work
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary / 100
            total = total * porc_integral_salary
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        else:
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        if total / salario_minimo >= 4 and total / salario_minimo < 16:
            result = round(total * 0.005 * -1, -2)
        if total / salario_minimo >= 16 and total / salario_minimo <= 17:
            result = round(total * 0.007 * -1, -2)
        if total / salario_minimo > 17 and total / salario_minimo <= 18:
            result = round(total * 0.009 * -1, -2)
        if total / salario_minimo > 18 and total / salario_minimo <= 19:
            result = round(total * 0.011 * -1, -2)
        if total / salario_minimo > 19 and total / salario_minimo <= 20:
            result = round(total * 0.013 * -1, -2)
        if total / salario_minimo > 20 and total / salario_minimo <= 25:
            result = round(total * 0.015 * -1, -2)
        if total / salario_minimo > 25:
            result = round(salario_minimo * 25 * 0.01 * -1, -2)
#---------------------------------------Fondo Solidadridad // QUINCENAL SOLO TKARGA--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL004',employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        salario_minimo = annual_parameters.smmlv_monthly
        total_month = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        total = categories.DEV_SALARIAL if aplicar == 0 and inherit_contrato==0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        # Ley 1393
        if payslip.date_from.day > 15 or (inherit_contrato != 0):
            total_salarial = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from,
                                                                         payslip.date_to)
            auxtransporte = AUX000 + payslip.sum_mount_x_rule('AUX000', payslip.date_from, payslip.date_to)
            vac_no_salarial = categories.VNS + + payslip.sum_mount('VNS', payslip.date_from, payslip.date_to)
            total_no_salarial = categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,
                                                                               payslip.date_to) - auxtransporte - vac_no_salarial
            gran_total = total_salarial + total_no_salarial
            statute_value = (gran_total / 100) * annual_parameters.value_porc_statute_1395
            total_statute = total_no_salarial - statute_value
            if total_statute > 0:
                total += total_statute
                total_month += total_statute
        # Fin Ley 1393
        dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        dias_work_act = worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
        dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
        top_twenty_five_smmlv = (annual_parameters.top_twenty_five_smmlv / 30) * dias_work
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary / 100
            total = total * porc_integral_salary
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        else:
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        if (total/salario_minimo) >= 2 and (total/salario_minimo) < 8:
            result =  (total * 0.005 * (-1))
        if  (total/salario_minimo) >= 8 and (total/salario_minimo) <= 8.5:
            result =  (total * 0.006 * (-1))
        if  (total/salario_minimo) > 8.5 and (total/salario_minimo) <= 9:
            result =  (total * 0.007 * (-1))
        if  (total/salario_minimo) > 9 and (total/salario_minimo) <= 9.5:
            result =  (total * 0.008 * (-1))
        if  (total/salario_minimo) > 9.5 and (total/salario_minimo) <= 10:
            result =  (total * 0.009 * (-1))
        if  (total/salario_minimo) > 10 and (total/salario_minimo) <= 12.5:
            result =  (total * 0.01* (-1))
        if  (total/salario_minimo) > 12.5:
            result =  (salario_minimo * 25 * 0.01* (-1))
        if payslip.date_from.day > 15 and not (total_month/salario_minimo) >= 4:
            result = 0

#V19
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SSOCIAL004', employee.type_employee.id)
liquidates_solidarity_fund = payslip.get_parameterization_contributors().liquidates_solidarity_fund if len(payslip.get_parameterization_contributors()) > 0 else True
if obj_salary_rule and liquidates_solidarity_fund and (version.contract_type != 'aprendizaje'):
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)
    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        salario_minimo = annual_parameters.smmlv_monthly
        if annual_parameters.z_enable_ibc_previous_month and (worked_days.VACDISFRUTADAS or 0):
            total = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            total_validation = total
            if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                total_salarial = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
                auxtransporte = rules_computed.AUX000
                vac_no_salarial = payslip.sum_mount_before('VNS', payslip.date_from)
                total_no_salarial = payslip.sum_mount_before('DEV_NO_SALARIAL', payslip.date_from) - auxtransporte - vac_no_salarial
                gran_total = total_salarial + total_no_salarial
                statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute
            total = total / 30 * leaves.VACDISFRUTADAS
        else:
            total = categories.DEV_SALARIAL or 0 if aplicar == 0 else (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            total_validation = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            if total_validation > 0 and (payslip.date_from.day > 0 or inherit_contrato != 0):
                total_salarial = categories.DEV_SALARIAL or 0
                auxtransporte = rules_computed.AUX000
                vac_no_salarial = categories.VNS or 0
                total_no_salarial = (categories.DEV_NO_SALARIAL or 0) - auxtransporte - vac_no_salarial
                gran_total = total_salarial + total_no_salarial
                statute_value = gran_total / 100 * annual_parameters.value_porc_statute_1395
                total_statute = total_no_salarial - statute_value
                if total_statute > 0:
                    total += total_statute
        dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
        dias_work_act = (worked_days.WORK100 or 0).number_of_days if worked_days.WORK100 or 0 else 0
        dias_work = dias_work_act if aplicar == 0 else dias_work + dias_work_act
        top_twenty_five_smmlv = annual_parameters.top_twenty_five_smmlv / 30 * dias_work
        if version.modality_salary == 'integral':
            porc_integral_salary = annual_parameters.porc_integral_salary / 100
            total = total * porc_integral_salary
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        else:
            total = top_twenty_five_smmlv if total >= top_twenty_five_smmlv else total
        if total / salario_minimo >= 4:
            result = round(total * 0.005 * -1, -2) - payslip.sum_mount_x_rule('SSOCIAL004', payslip.date_from, payslip.date_to)
#---------------------------------------Valor devengos/deducciones & Libranzas --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX001',employee.type_employee.id) 
if obj_salary_rule and worked_days.WORK100 != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)        
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll): # Cambiar por (aplicar >= day_initial_payrroll and day_end_payrroll <= aplicar)
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1

#--------------------------------------- Auxilio de rodamiento --------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX001',employee.type_employee.id)
if obj_salary_rule and worked_days.WORK100 != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias_work = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to)
                dias_work_act = worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
                dias_work = dias_work_act if (aplicar == 0) else dias_work + dias_work_act
                #dias = worked_days.WORK100.number_of_days
                result_qty = dias_work
                amount = obj_concept.amount/30
            else:
                 amount = obj_concept.amount
            result = amount if obj_salary_rule.dev_or_ded == 'devengo' else (amount)*-1

#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX001',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX001', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                amount = obj_concept.amount / 30 * (worked_days.WORK100 or 0).number_of_days
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX001', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100).number_of_days
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX001', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            dias = (worked_days.WORK100.number_of_days or 0)
            dias += (worked_days.VACDISFRUTADAS.number_of_days or 0) if (worked_days.VACDISFRUTADAS or 0) != 0.0 else 0
            if obj_salary_rule.modality_value == 'diario':
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                amount = obj_concept.amount / 30 * dias
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else amount * -1
#---------------------------------------Auxilio no salarial - TKARGA . INCLUYE VACACIONES // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX002', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 != 0.0 or leaves.VACDISFRUTADAS != 0.0):
    days_process = 0
    if worked_days.WORK100 != 0.0:
        days_process += worked_days.WORK100.number_of_days
    if leaves.VACDISFRUTADAS != 0.0:
        days_process += leaves.VACDISFRUTADAS
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (
        28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = days_process
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias) * -1
            else:
                amount = (obj_concept.amount / 30) * days_process
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else (amount) * -1

#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX002',employee.type_employee.id)
dias = payslip.sum_days_works('WORK100',payslip.date_from, payslip.date_to) + payslip.sum_days_works('COMPENSATORIO',payslip.date_from, payslip.date_to)
dias += (worked_days.WORK100.number_of_days or 0) if worked_days.WORK100 else 0
if (worked_days.COMPENSATORIO or 0) != 0.0:
    dias += (worked_days.COMPENSATORIO.number_of_days or 0)
if obj_salary_rule and dias != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                result = obj_concept.amount #* dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
                result_qty = dias
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX002', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                amount = obj_concept.amount / 30 * (worked_days.WORK100 or 0).number_of_days
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else amount * -1
#V19 Tkarga
result = 0.0 
try: 
    id_version_concepts 
except Exception: 
    id_version_concepts = 0 
obj_salary_rule = payslip.get_salary_rule('AUX002', employee.type_employee.id) 
if obj_salary_rule: 
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts) 
    day_initial_payrroll = payslip.date_from.day 
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day 
    if obj_concept: 
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar) 
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll): 
            dias_validos = 0.0 
            if (worked_days.WORK100 or 0) != 0.0: 
                dias_validos += (worked_days.WORK100.number_of_days or 0) 
            if leaves.VACDISFRUTADAS != 0.0: 
                dias_validos += leaves.VACDISFRUTADAS 
            if (worked_days.EGA or 0) != 0.0: 
                dias_validos += (worked_days.EGA.number_of_days or 0) 
            if (worked_days.EGH or 0) != 0.0: 
                dias_validos += (worked_days.EGH.number_of_days or 0) 
            if (worked_days.EP or 0) != 0.0: 
                dias_validos += (worked_days.EP.number_of_days or 0) 
            if (worked_days.AT or 0) != 0.0: 
                dias_validos += (worked_days.AT.number_of_days or 0) 
            if (worked_days.LICENCIA_REMUNERADA or 0) != 0.0: 
                dias_validos += (worked_days.LICENCIA_REMUNERADA.number_of_days or 0) 
            if (worked_days.LUTO or 0) != 0.0: 
                dias_validos += (worked_days.LUTO.number_of_days or 0) 
            if (worked_days.MAT or 0) != 0.0: 
                dias_validos += (worked_days.MAT.number_of_days or 0) 
            if dias_validos != 0.0: 
                amount = obj_concept.amount / 30 * dias_validos 
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else amount * -1
#---------------------------------------Embargo salarial 1/5 smmvl--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO002',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)        
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            salario_minimo = annual_parameters.smmlv_monthly/2 if aplicar == 0 else annual_parameters.smmlv_monthly
            total = categories.DEV_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            val = round((total - salario_minimo)/5)
            result = val*-1 if val > 0 else val
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0 
#---------------------------------------Embargo salarial %--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO007',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)        
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 15
            result = (round((total)*porc/100)*-1)
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0           
#---------------------------------------Embargotodo--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO008',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)        
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 15
            result = (round((total)*porc/100)*-1)  
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0      
#---------------------------------------Horas Extra Diurnas (125%)--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC001',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_ext_d' and overtime.overtime_ext_d > 0:
                    r_qty += overtime.overtime_ext_d
            result = round((version.wage /annual_parameters.hours_monthly)*1.25)  if r_qty > 0 else 0
            result_qty = r_qty

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC001',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_ext_d' and obj_overtime.overtime_ext_d > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*1.25)
                result_qty = obj_overtime.overtime_ext_d
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC001', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_ext_d' and obj_overtime.overtime_ext_d > 0:
                    result = round((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 1.25)
                    result_qty = obj_overtime.overtime_ext_d
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC001', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):    
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_ext_d' and obj_overtime.overtime_ext_d > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*1.25)
                result_qty = obj_overtime.overtime_ext_d
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC001', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_ext_d' and obj_overtime.overtime_ext_d > 0:
                result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 1.25
                result_qty = obj_overtime.overtime_ext_d
#---------------------------------------Horas extra diurnas dominical / festiva (200%)--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC002',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_eddf' and overtime.overtime_eddf > 0:
                    r_qty += overtime.overtime_eddf
            result = round((version.wage /annual_parameters.hours_monthly)*2)  if r_qty > 0 else 0
            result_qty = r_qty

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC002',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_eddf' and obj_overtime.overtime_eddf > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*2.05)
                result_qty = obj_overtime.overtime_eddf
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC002', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_eddf' and obj_overtime.overtime_eddf > 0:
                    result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 2.15
                    result_qty = obj_overtime.overtime_eddf
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC002', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):    
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_eddf' and obj_overtime.overtime_eddf > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*2.05)
                result_qty = obj_overtime.overtime_eddf
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC002', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_eddf' and obj_overtime.overtime_eddf > 0:
                result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 2.5
                result_qty = obj_overtime.overtime_eddf
#---------------------------------------Horas extra nocturna (175%)--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC003',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_ext_n' and overtime.overtime_ext_n > 0:
                    r_qty += overtime.overtime_ext_n
            result = round((version.wage /annual_parameters.hours_monthly)*1.75)  if r_qty > 0 else 0
            result_qty = r_qty

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC003',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_ext_n' and obj_overtime.overtime_ext_n > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*1.75)
                result_qty = obj_overtime.overtime_ext_n
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC003', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_ext_n' and obj_overtime.overtime_ext_n > 0:
                    result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 1.75
                    result_qty = obj_overtime.overtime_ext_n
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC003', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):    
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_ext_n' and obj_overtime.overtime_ext_n > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*1.75)
                result_qty = obj_overtime.overtime_ext_n
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC003', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_ext_n' and obj_overtime.overtime_ext_n > 0:
                result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 1.75
                result_qty = obj_overtime.overtime_ext_n
#---------------------------------------Horas recargo festivo (110%)--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC004',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_rndf' and overtime.overtime_rndf > 0:
                    r_qty += overtime.overtime_rndf
            result = round((version.wage /annual_parameters.hours_monthly)*1.1)  if r_qty > 0 else 0
            result_qty = r_qty

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC004',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rndf' and obj_overtime.overtime_rndf > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*1.15)
                result_qty = obj_overtime.overtime_rndf
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC004', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_rndf' and obj_overtime.overtime_rndf > 0:
                    result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 1.25
                    result_qty = obj_overtime.overtime_rndf
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC004', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):    
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rndf' and obj_overtime.overtime_rndf > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*1.15)
                result_qty = obj_overtime.overtime_rndf
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC004', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rndf' and obj_overtime.overtime_rndf > 0:
                result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 1.15
                result_qty = obj_overtime.overtime_rndf
#---------------------------------------Recargos dominicales (0.75%) // Molpartes, Sole, Tkarga--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC008',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato, aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_rdf' and overtime.overtime_rdf > 0:
                    r_qty += overtime.overtime_rdf
            result = round((version.wage / annual_parameters.hours_monthly) * 0.75)  if r_qty > 0 else 0
            result_qty = r_qty

#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC008', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_rdf' and obj_overtime.overtime_rdf > 0:
                    result = round((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / 220 * 1.9)
                    result_qty = obj_overtime.overtime_rdf
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC008', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rdf' and obj_overtime.overtime_rdf > 0:
                result = (((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*0.90)
                result_qty = obj_overtime.overtime_rdf
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC008', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rdf' and obj_overtime.overtime_rdf > 0:
                result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 0.8
                result_qty = obj_overtime.overtime_rdf
#---------------------------------------Horas Dominicales (175%)--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC007',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_dof' and overtime.overtime_dof > 0:
                    r_qty += overtime.overtime_dof
            result = round((version.wage /annual_parameters.hours_monthly)*1.75)  if r_qty > 0 else 0
            result_qty = r_qty
#---------------------------------------Horas Recargo Nocturno (35%)--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC005',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_rn' and overtime.overtime_rn > 0:
                    r_qty += overtime.overtime_rn
            result = round((version.wage /annual_parameters.hours_monthly)*0.35)  if r_qty > 0 else 0
            result_qty = r_qty

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC005',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rn' and obj_overtime.overtime_rn > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*0.35)
                result_qty = obj_overtime.overtime_rn
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC005', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_rn' and obj_overtime.overtime_rn > 0:
                    result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 0.35
                    result_qty = obj_overtime.overtime_rn
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC005', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):    
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rn' and obj_overtime.overtime_rn > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*0.35)
                result_qty = obj_overtime.overtime_rn
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC005', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rn' and obj_overtime.overtime_rn > 0:
                result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 0.35
                result_qty = obj_overtime.overtime_rn
#---------------------------------------Horas extra nocturna dominical / festiva (250%)--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC006',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_endf' and overtime.overtime_endf > 0:
                    r_qty += overtime.overtime_endf
            result = round((version.wage /annual_parameters.hours_monthly)*2.5) if r_qty > 0 else 0
            result_qty = r_qty

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC006',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_endf' and obj_overtime.overtime_endf > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*2.55)
                result_qty = obj_overtime.overtime_endf
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC006', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_endf' and obj_overtime.overtime_endf > 0:
                    result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 2.65
                    result_qty = obj_overtime.overtime_endf
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC006', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):    
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_endf' and obj_overtime.overtime_endf > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*2.55)
                result_qty = obj_overtime.overtime_endf
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC006', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_endf' and obj_overtime.overtime_endf > 0:
                result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 2.55
                result_qty = obj_overtime.overtime_endf
#---------------------------------------Horas dominicales--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC007',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
        if len(obj_overtime) > 0:
            r_qty = 0
            for overtime in obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_dof' and overtime.overtime_dof > 0:
                    r_qty += overtime.overtime_dof
            result = round((version.wage /annual_parameters.hours_monthly)*0.75)  if r_qty > 0 else 0
            result_qty = r_qty

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC007',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_dof' and obj_overtime.overtime_dof > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*0.80)
                result_qty = obj_overtime.overtime_dof
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC007', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_dof' and obj_overtime.overtime_dof > 0:
                    result = round((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 1.9)
                    result_qty = obj_overtime.overtime_dof
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC007', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato != 0):
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_dof' and obj_overtime.overtime_dof > 0:
                result = round(((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly) * 1.90)
                result_qty = obj_overtime.overtime_dof
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC007', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_dof' and obj_overtime.overtime_dof > 0:
                result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 1.8
                result_qty = obj_overtime.overtime_dof
#---------------------------------------Dias efectivamente laborados--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX005',employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        if obj_salary_rule.modality_value == 'diario_efectivo':
            obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
            obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,aplicar)
            if obj_overtime and obj_concept:
                if obj_overtime.days_actually_worked > 0:
                    result = obj_concept.amount#version.wage / 30
                    result_qty = obj_overtime.days_actually_worked
#---------------------------------------Incapacidad EPS // AlianzaT, Molpartes--------------------------------------------------------
#Odoo V8
result = 0.0

#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
if payslip.date_from.day > 15 or (inherit_contrato!=0):
    obj_salary_rule = payslip.get_salary_rule('AUX005',employee.type_employee.id)
    if obj_salary_rule:
        obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
        if obj_concept and obj_salary_rule.modality_value == 'diario_efectivo':
            obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,30)
            if obj_overtime:
                r_qty = 0
                for overtime in obj_overtime:
                    if overtime.days_actually_worked > 0:
                        r_qty += overtime.days_actually_worked
                result = obj_concept.amount
                result_qty = r_qty
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX005', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Incapacidad Compañía--------------------------------------------------------
#Odoo V8
result = 0.0

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD001',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and leaves.EGA_TOTAL <= 90:
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly / 30
            amount_ibc = version.wage
            if obj_leave_type.periods_calculations_ibl > 0 and payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from) > 0:
                amount_ibc = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            ibc_real = (amount_ibc/30) * obj_leave_type.recognizing_factor_eps_arl
            daily_value = ibc_real if ibc_real > salario_minimo else salario_minimo
            days = leaves.EGA_PARTNER
            if days > 0:
                result = daily_value
                result_qty = days
#V19 Molpartes, Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD001', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and (leaves.EGA_TOTAL <= 90 or leaves.EGA_MINUS90 != 0):
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            amount_ibc = version.wage
            if obj_leave_type.periods_calculations_ibl > 0 and payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from) > 0:
                amount_ibc = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = amount_ibc * obj_leave_type.recognizing_factor_eps_arl
            ibc_real = salario_minimo if amount_ibc * obj_leave_type.recognizing_factor_eps_arl < salario_minimo else amount_ibc * obj_leave_type.recognizing_factor_eps_arl
            days = leaves.EGA_PARTNER - leaves.EGA_PARTNER_PLUS90
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD001', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and leaves.EGA <= 90:
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = leaves.EGA_PARTNER
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days 
#---------------------------------------Incapacidad EPS 50%--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD007',employee.type_employee.id)
if obj_salary_rule:
    if worked_days.EGA != 0.0 and leaves.EGA_TOTAL > 90:
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type:
            days = worked_days.EGA.number_of_days
            if leaves.EGA_TOTAL > 180:
                if (leaves.EGA_TOTAL-worked_days.EGA.number_of_days) <= 180:
                    days = 180-(leaves.EGA_TOTAL-worked_days.EGA.number_of_days)
                else:
                    days = 0
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * 0.5)
            ibc_real = ibc_real if ibc_real >= salario_minimo else salario_minimo
            days = days if days >= 0 else 0
            result =  (ibc_real) /30
            result_qty = days

result = 0.0

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD007',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and leaves.EGA_TOTAL > 90:
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type:
            days = (worked_days.EGA.number_of_days or 0)
            if leaves.EGA_TOTAL > 180:
                if (leaves.EGA_TOTAL-(worked_days.EGA.number_of_days or 0)) <= 180:
                    days = 180-(leaves.EGA_TOTAL-(worked_days.EGA.number_of_days or 0))
                else:
                    days = 0
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * 0.5)
            ibc_real = ibc_real if ibc_real >= salario_minimo else salario_minimo
            days = days if days >= 0 else 0
            result =  (ibc_real) /30
            result_qty = days
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD007', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and (leaves.EGA > 90 and leaves.EGA <= 180):
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * 0.5
            ibc_real = salario_minimo if ibc_real < salario_minimo else ibc_real
            days = (worked_days.EGA or 0).number_of_days
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD007', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and (leaves.EGA > 90 and leaves.EGA <= 180):
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * 0.5)
            ibc_real = salario_minimo if ibc_real < salario_minimo else ibc_real
            days = (worked_days.EGA.number_of_days or 0) 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD007', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and (leaves.EGA > 90 and leaves.EGA <= 180 or leaves.EGA > 540):
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * 0.5
            days = (worked_days.EGA.number_of_days or 0)
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#---------------------------------------Incapacidad Accidente de Trabajo - ARL COMPAÑIA--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD006',employee.type_employee.id)
if obj_salary_rule:
    if worked_days.AT != 0.0:
        obj_leave_type = payslip.get_leave_type('AT')
        if obj_leave_type.company_input_id.id == obj_salary_rule.id:
            amount_ibc = version.wage
            if obj_leave_type.periods_calculations_ibl > 0 and payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from) > 0:
                amount_ibc = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (amount_ibc * obj_leave_type.recognizing_factor_company)
            ibc_real = salario_minimo if (amount_ibc * obj_leave_type.recognizing_factor_company) < salario_minimo else (amount_ibc * obj_leave_type.recognizing_factor_company)
            days = leaves.AT_COMPANY
            days = days if days >= 0 else 0
            result =  (ibc_real) /30
            result_qty = days


#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD006', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.AT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('AT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            # ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.AT.number_of_days or 0) - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = (ibc_real) / 30
            result_qty = days
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD006', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.AT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('AT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.AT or 0).number_of_days - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD006', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.AT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('AT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            #ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.AT.number_of_days or 0) - obj_leave_type.num_days_no_assume 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD006', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.AT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('AT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            ibc_real = salario_minimo if version.modality_salary != 'sostenimiento' and version.wage * obj_leave_type.recognizing_factor_eps_arl < salario_minimo else version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.AT.number_of_days or 0) - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#---------------------------------------Incapacidad Accidente de Trabajo - ARL EPS--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD009',employee.type_employee.id)
if obj_salary_rule:
    if worked_days.AT != 0.0:
        obj_leave_type = payslip.get_leave_type('AT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            amount_ibc = version.wage
            if obj_leave_type.periods_calculations_ibl > 0 and payslip.sum_mount_before('BASIC', payslip.date_from) > 0:
                amount_ibc = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (amount_ibc * obj_leave_type.recognizing_factor_eps_arl)
            ibc_real = salario_minimo if (amount_ibc * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (amount_ibc * obj_leave_type.recognizing_factor_eps_arl)
            days = leaves.AT_PARTNER
            days = days if days >= 0 else 0
            result =  (ibc_real) /30
            result_qty = days

#---------------------------------------Licencia remunerada--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA001',employee.type_employee.id)
if obj_salary_rule and worked_days.LICENCIA_REMUNERADA != 0.0:
        result =  round(worked_days.LICENCIA_REMUNERADA.number_of_days * (version.wage /30))  

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA001',employee.type_employee.id)
if obj_salary_rule and (worked_days.LICENCIA_REMUNERADA or 0) != 0.0:
        result =  round((worked_days.LICENCIA_REMUNERADA.number_of_days or 0) * (version.wage /30))
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA001', employee.type_employee.id)
if obj_salary_rule and (worked_days.LICENCIA_REMUNERADA or 0) != 0.0:
    result = round(worked_days.LICENCIA_REMUNERADA.number_of_days * (version.wage / 30))
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA001', employee.type_employee.id)
if obj_salary_rule and (worked_days.LICENCIA_REMUNERADA or 0) != 0.0:
        result =  round((worked_days.LICENCIA_REMUNERADA.number_of_days or 0) * (version.wage /30))
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA001', employee.type_employee.id)
if obj_salary_rule and (worked_days.LICENCIA_REMUNERADA or 0) != 0.0:
    result = round((worked_days.LICENCIA_REMUNERADA.number_of_days or 0) * (version.wage / 30))
#---------------------------------------Retención en la fuente--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE001',employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            amount_process = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            amount_process += categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,payslip.date_to)
            if amount_process >= annual_parameters.value_top_source_retention:
                localdict = {
                            'categories': categories,
                            'rules_computed': rules_computed,
                            'payslip': payslip,
                            'employee': employee,
                            'version': version,
                            'annual_parameters':annual_parameters
                        }
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to,version.retention_procedure, localdict)
                result = (obj_retention.result_calculation) * -1
        else:
            result = (version.fixed_value_retention_procedure) * -1

#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE001',employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            amount_process = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            amount_process += categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,payslip.date_to)
            amount_process += rules_computed.dict.get('AUX008', 0) + payslip.sum_mount_x_rule('AUX008', payslip.date_from, payslip.date_to)
            if amount_process >= annual_parameters.value_top_source_retention:
                localdict = {
                            'categories': categories,
                            'rules_computed': rules_computed,
                            'payslip': payslip,
                            'employee': employee,
                            'version': version,
                            'annual_parameters':annual_parameters
                        }
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to,version.retention_procedure, localdict)
                result = (obj_retention.result_calculation) * -1
        else:
            result = (version.fixed_value_retention_procedure) * -1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE001', employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)
    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            amount_process = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            amount_process += (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if amount_process >= annual_parameters.value_top_source_retention:
                localdict = {'categories': categories, 'rules_computed': rules_computed, 'payslip': payslip, 'employee': employee, 'version': version, 'annual_parameters': annual_parameters}
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to, version.retention_procedure, localdict)
                result = obj_retention.result_calculation * -1
        else:
            result = version.fixed_value_retention_procedure * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE001', employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            amount_process = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            amount_process += categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,payslip.date_to)
            if amount_process >= annual_parameters.value_top_source_retention:
                localdict = {
                            'categories': categories,
                            'rules_computed': rules_computed,
                            'payslip': payslip,
                            'employee': employee,
                            'version': version,
                            'annual_parameters':annual_parameters
                        }
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to,version.retention_procedure, localdict)
                result = (obj_retention.result_calculation) * -1
        else:
            result = (version.fixed_value_retention_procedure) * -1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE001', employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)
    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            if version.wage >= annual_parameters.value_top_source_retention:
                localdict = {'categories': categories, 'rules_computed': rules_computed, 'payslip': payslip, 'employee': employee, 'version': version, 'annual_parameters': annual_parameters}
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to, version.retention_procedure, localdict)
                result = obj_retention.result_calculation * -1
        else:
            result = version.fixed_value_retention_procedure * -1
#---------------------------------------Cuota Sindical--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CUOTA001',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)         
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll): 
            result = (((version.wage/100)*1)/2)*-1 # Corresponde al 1% del salario
        else:
            result = ((version.wage/100)*1)*-1 # Corresponde al 1% del salario

#---------------------------------------Ajuste Salario (Dev) // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_BASICO',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_BASICO', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Tkarga
result = 0.0 
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_BASICO', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0: 
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts) 
    day_initial_payrroll = payslip.date_from.day 
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day 
    if obj_concept: 
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar) 
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll): 
            if obj_salary_rule.modality_value == 'diario': 
                dias = (worked_days.WORK100 or 0).number_of_days or 0 
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1 
            else: 
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Garantizado // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BASIC004', employee.type_employee.id)
if obj_salary_rule and version.modality_salary != 'integral' and (version.modality_salary != 'sostenimiento') and (version.subcontract_type not in ('obra_parcial', 'obra_integral')):
    if (worked_days.WORK100 or 0) != 0.0:
        obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
        day_initial_payrroll = payslip.date_from.day
        day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
        if obj_concept:
            aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
            if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
                dias = worked_days.WORK100.number_of_days or 0
                base_mensual = obj_concept.amount
                result = round(dias * (base_mensual / 30))
                if obj_salary_rule.dev_or_ded == 'deduccion':
                    result = result * -1
#---------------------------------------Interrupción de Vacaciones // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('INTERRUPCION_VAC',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Bono Tarjeta Zafiro Plus // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX008', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                amount = obj_concept.amount / 30 * (worked_days.WORK100 or 0)
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else amount * -1
#---------------------------------------Recargo horas dominicales/festiva fijas 1.9 // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX011', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100).number_of_days
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Horas extras diurnas fijas 1.25 // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX012', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100).number_of_days
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Bono Coordinador // AlianzaT, Molpartes, Sole--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('BONI001',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BONI001', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BONI001', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Bonificación // AlianzaT, Molpartes, Sole--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('BONI002',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BONI002', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('BONI002', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Bono por cumplimiento de metas // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('BONI003',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Bono por resultados // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('BONI004',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Labor encargo // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('COMI001',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Dotación // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('DOTACION',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------IMPUESTO ASUMIDO // Tkarga--------------------------------------------------------
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('DOTACION', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Ajuste Salario // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_SALARIO', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Auxilio conectividad--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX003',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX003', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                amount = obj_concept.amount / 30 * (worked_days.WORK100 or 0).number_of_days
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX003', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                amount = (obj_concept.amount/30)*(worked_days.WORK100.number_of_days or 0)
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else (amount)*-1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX003', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Auxilio alimentación - Fijo - No prestacional // AlianzaT, Molpartes--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX004',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
if payslip.date_from.day > 0 or inherit_contrato != 0:
    obj_salary_rule = payslip.get_salary_rule('AUX004', employee.type_employee.id)
    if obj_salary_rule:
        obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
        if obj_concept and obj_salary_rule.modality_value == 'diario_efectivo':
            try:
                obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato, 30)
                if len(obj_overtime) > 0:
                    r_qty = 0
                    for overtime in obj_overtime:
                        if overtime.days_actually_worked > 0:
                            r_qty += overtime.days_actually_worked
                    result = obj_concept.amount * -1
                    result_qty = r_qty
            except:
                result = 0.0
#---------------------------------------AUXILIO DE ARRENDAMIENTO // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX0055',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Refrigerio // AlianzaT, Molpartes--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
if payslip.date_from.day > 15 or (inherit_contrato!=0):
    obj_salary_rule = payslip.get_salary_rule('AUX007',employee.type_employee.id)
    if obj_salary_rule:
        obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
        if obj_concept and obj_salary_rule.modality_value == 'diario_efectivo':
            obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato,30)
            if obj_overtime:
                r_qty = 0
                for overtime in obj_overtime:
                    if overtime.days_snack > 0:
                        r_qty += overtime.days_snack
                result = obj_concept.amount
                result_qty = r_qty
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX007', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------CCT - ART 13 AUXILIO EDUCATIVO PRÉSTAMO // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX055',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Ajuste Aux.Transporte (Dev) // AlianzaT, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_AUX.TRANS',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_AUX.TRANS', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Ajuste de cesantías (Dev) // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_CESANTIAS',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Ajuste Devolución Embargo (Dev) // AlianzaT, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_EMBARGO',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Tkarga
result = 0.0 
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_EMBARGO', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0: 
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts) 
    day_initial_payrroll = payslip.date_from.day 
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day 
    if obj_concept: 
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar) 
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll): 
            if obj_salary_rule.modality_value == 'diario': 
                dias = (worked_days.WORK100.number_of_days or 0) 
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1 
            else: 
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Ajuste Salud Dev // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_SALUD',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Ajuste Aux.Transporte (Dev) // Tkarga--------------------------------------------------------
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_AUX_NOSAL', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Auxilio de Movilización // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX006',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = payslip.sum_days_works('WORK100',payslip.date_from, payslip.date_to) + (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX006', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX006', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = payslip.sum_days_works('WORK100', payslip.date_from, payslip.date_to) + (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Incapacidad EGA--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD002',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and leaves.EGA_COMPANY <= 90 and leaves.EGA_TOTAL <= 90:
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type.company_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly/30
            amount_ibc = version.wage
            if obj_leave_type.periods_calculations_ibl > 0 and payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from) > 0:
                amount_ibc = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            ibc_real = (amount_ibc/30) * obj_leave_type.recognizing_factor_company
            daily_value = ibc_real if ibc_real > salario_minimo else salario_minimo            
            days = leaves.EGA_COMPANY
            if days > 0:
                result = daily_value
                result_qty = days
#V19 Molpartes, Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD002', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and leaves.EGA_COMPANY <= 90:
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type.company_input_id.id == obj_salary_rule.id:
            amount_ibc = version.wage
            if obj_leave_type.periods_calculations_ibl > 0 and payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from) > 0:
                amount_ibc = payslip.sum_mount_before('DEV_SALARIAL', payslip.date_from)
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = amount_ibc * obj_leave_type.recognizing_factor_company
            ibc_real = salario_minimo if amount_ibc * obj_leave_type.recognizing_factor_company < salario_minimo else amount_ibc * obj_leave_type.recognizing_factor_company
            days = leaves.EGA_COMPANY
            if days > 0:
                result = ibc_real / 30
                result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD002', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGA or 0) != 0.0 and leaves.EGA_COMPANY <= 90:
        obj_leave_type = payslip.get_leave_type('EGA')
        if obj_leave_type.company_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_company)
            ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_company) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_company)
            days = leaves.EGA_COMPANY
            if days > 0:
                result =  (ibc_real) /30
                result_qty = days
#---------------------------------------Incapacidad EGH - EPS 66.66%--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD003',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and leaves.EGH <= 90:
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            #ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.EGH.number_of_days or 0) - obj_leave_type.num_days_no_assume 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD003', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and leaves.EGH_PARTNER <= 90:
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            ibc_real = salario_minimo if version.wage * obj_leave_type.recognizing_factor_eps_arl < salario_minimo else version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = leaves.EGH_PARTNER
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD003', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and leaves.EGH_PARTNER <= 90:
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = leaves.EGH_PARTNER
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD003', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and leaves.EGH <= 90:
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            ibc_real = salario_minimo if version.modality_salary != 'sostenimiento' and version.wage * obj_leave_type.recognizing_factor_eps_arl < salario_minimo else version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.EGH.number_of_days or 0) - obj_leave_type.num_days_no_assume if (worked_days.EGH.number_of_days or 0) >= leaves.EGH else (worked_days.EGH.number_of_days or 0)
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#---------------------------------------Incapacidad EGH - Compañía--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD004',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and leaves.EGH <= 90:
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type.company_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_company)
            #ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_company) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_company)
            days = (worked_days.EGH.number_of_days or 0) if (worked_days.EGH.number_of_days or 0) <= obj_leave_type.num_days_no_assume else obj_leave_type.num_days_no_assume  
            if days > 0:
                result =  (ibc_real) /30
                result_qty = days
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD004', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and leaves.EGH_COMPANY <= 90:
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type.company_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_company
            ibc_real = salario_minimo if version.wage * obj_leave_type.recognizing_factor_company < salario_minimo else version.wage * obj_leave_type.recognizing_factor_company
            days = leaves.EGH_COMPANY
            if days > 0:
                result = ibc_real / 30
                result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD004', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and leaves.EGH_COMPANY <= 90:
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type.company_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_company)
            ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_company) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_company)
            days = leaves.EGH_COMPANY 
            if days > 0:
                result =  (ibc_real) /30
                result_qty = days
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD004', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and leaves.EGH <= 90:
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type.company_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_company
            ibc_real = salario_minimo if version.modality_salary != 'sostenimiento' and version.wage * obj_leave_type.recognizing_factor_company < salario_minimo else version.wage * obj_leave_type.recognizing_factor_company
            days = ((worked_days.EGH.number_of_days or 0) if (worked_days.EGH.number_of_days or 0) <= obj_leave_type.num_days_no_assume else obj_leave_type.num_days_no_assume) if (worked_days.EGH.number_of_days or 0) >= leaves.EGH else 0
            if days > 0:
                result = ibc_real / 30
                result_qty = days
#---------------------------------------Incapacidad EP - EPS--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD005',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EP or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('EP')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            #ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.EP.number_of_days or 0) - obj_leave_type.num_days_no_assume 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD005', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EP or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('EP')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            ibc_real = salario_minimo if version.wage * obj_leave_type.recognizing_factor_eps_arl < salario_minimo else version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.EP or 0).number_of_days - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD005', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EP or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('EP')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.EP.number_of_days or 0) - obj_leave_type.num_days_no_assume 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD005', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EP or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('EP')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            ibc_real = salario_minimo if version.modality_salary != 'sostenimiento' and version.wage * obj_leave_type.recognizing_factor_eps_arl < salario_minimo else version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.EP.number_of_days or 0) - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#---------------------------------------Incapacidad EGH - EPS 50%--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD008',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and (leaves.EGH > 90 and leaves.EGH <= 180):
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * 0.5)
            days = (worked_days.EGH.number_of_days or 0) 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD008', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and (leaves.EGH > 90 and leaves.EGH <= 180):
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * 0.5
            days = (worked_days.EGH or 0).number_of_days
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD008', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and (leaves.EGH > 90 and leaves.EGH <= 180):
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * 0.5)
            days = (worked_days.EGH.number_of_days or 0) 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INCAPACIDAD008', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.EGH or 0) != 0.0 and (leaves.EGH > 90 and leaves.EGH <= 180 or leaves.EGH > 540):
        obj_leave_type = payslip.get_leave_type('EGH')
        if obj_leave_type:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * 0.5
            days = (worked_days.EGH.number_of_days or 0)
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#---------------------------------------Licencia de Maternidad--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA002',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.MAT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('MAT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            #ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.MAT.number_of_days or 0) - obj_leave_type.num_days_no_assume 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA002', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.MAT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('MAT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            ibc_real = salario_minimo if version.wage * obj_leave_type.recognizing_factor_eps_arl < salario_minimo else version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.MAT.number_of_days or 0) - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA002', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.MAT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('MAT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.MAT.number_of_days or 0) - obj_leave_type.num_days_no_assume 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA002', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.MAT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('MAT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.MAT.number_of_days or 0) - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#---------------------------------------Licencia de Paternidad--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA003',employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.PAT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('PAT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            #ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.PAT.number_of_days or 0) - obj_leave_type.num_days_no_assume 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA003', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.PAT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('PAT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            ibc_real = salario_minimo if version.wage * obj_leave_type.recognizing_factor_eps_arl < salario_minimo else version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.PAT.number_of_days or 0) - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA003', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.PAT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('PAT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            ibc_real = salario_minimo if (version.wage * obj_leave_type.recognizing_factor_eps_arl) < salario_minimo else (version.wage * obj_leave_type.recognizing_factor_eps_arl)
            days = (worked_days.PAT.number_of_days or 0) - obj_leave_type.num_days_no_assume 
            days = days if days >= 0 else 0 
            result =  (ibc_real) /30
            result_qty = days
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA003', employee.type_employee.id)
if obj_salary_rule:
    if (worked_days.PAT or 0) != 0.0:
        obj_leave_type = payslip.get_leave_type('PAT')
        if obj_leave_type.eps_arl_input_id.id == obj_salary_rule.id:
            salario_minimo = annual_parameters.smmlv_monthly
            ibc_real = version.wage * obj_leave_type.recognizing_factor_eps_arl
            days = (worked_days.PAT.number_of_days or 0) - obj_leave_type.num_days_no_assume
            days = days if days >= 0 else 0
            result = ibc_real / 30
            result_qty = days
#---------------------------------------Ajuste Incapacidad (Dev) // AlianzaT, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_INCAPACIDAD',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_INCAPACIDAD', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Ajuste Incapacidad Meses Anteriores (Dev) // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_INCMESESANT',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Compensatorio--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('COMPENSATORIO',employee.type_employee.id)
if obj_salary_rule and (worked_days.COMPENSATORIO or 0) != 0.0:
        result =  round((worked_days.COMPENSATORIO.number_of_days or 0) * (version.wage /30))
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('COMPENSATORIO', employee.type_employee.id)
if obj_salary_rule and (worked_days.COMPENSATORIO or 0) != 0.0:
    result = round((worked_days.COMPENSATORIO.number_of_days or 0).number_of_days * (version.wage / 30))
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('COMPENSATORIO', employee.type_employee.id)
if obj_salary_rule and (worked_days.COMPENSATORIO or 0) != 0.0:
        result =  round((worked_days.COMPENSATORIO.number_of_days or 0) * (version.wage /30))
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('COMPENSATORIO', employee.type_employee.id)
if obj_salary_rule and (worked_days.COMPENSATORIO or 0) != 0.0:
    result = round((worked_days.COMPENSATORIO.number_of_days or 0) * (version.wage / 30))
#---------------------------------------Licencia de luto--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA005',employee.type_employee.id)
if obj_salary_rule and (worked_days.LUTO or 0) != 0.0:
        result =  round((worked_days.LUTO.number_of_days or 0) * (version.wage /30))
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA005', employee.type_employee.id)
if obj_salary_rule and (worked_days.LUTO or 0) != 0.0:
    result = round(worked_days.LUTO.number_of_days * (version.wage / 30))
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA005', employee.type_employee.id)
if obj_salary_rule and (worked_days.LUTO or 0) != 0.0:
        result =  round((worked_days.LUTO.number_of_days or 0) * (version.wage /30))  
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA005', employee.type_employee.id)
if obj_salary_rule and (worked_days.LUTO or 0) != 0.0:
    result = round((worked_days.LUTO.number_of_days or 0) * (version.wage / 30))
#---------------------------------------Licencia por cuidado de la niñez // AlianzaT, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA007', employee.type_employee.id)
if obj_salary_rule and worked_days.LICENCIA_CUIDADO_NIÑEZ != 0.0:
    year = payslip.date_from.year
    start_date = payslip.date_from.replace(month=1, day=1)
    end_date = payslip.date_from.replace(month=12, day=31)
    qty_lic = payslip.sum_days_works('LICENCIA_CUIDADO_NIÑEZ', start_date, end_date)
    if qty_lic <= 10:
        qty_lic_rest = 10 - qty_lic
        result_qty = qty_lic_rest if worked_days.LICENCIA_CUIDADO_NIÑEZ.number_of_days > qty_lic_rest else worked_days.LICENCIA_CUIDADO_NIÑEZ.number_of_days
        result = version.wage / 30
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LICENCIA007', employee.type_employee.id)
if obj_salary_rule and (worked_days.LICENCIA_CUIDADO_NIÑEZ or 0) != 0.0:
    year = payslip.date_from.year
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    qty_lic = payslip.sum_days_works('LICENCIA_CUIDADO_NIÑEZ', start_date, end_date)
    if qty_lic <= 10:
        qty_lic_rest = 10 - qty_lic
        result_qty = qty_lic_rest if (worked_days.LICENCIA_CUIDADO_NIÑEZ or 0).number_of_days > qty_lic_rest else (worked_days.LICENCIA_CUIDADO_NIÑEZ or 0).number_of_days
        result = version.wage / 30
#---------------------------------------Salario sin prestación de servicios // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SAL_SIN_PRES_SERV',employee.type_employee.id)
if obj_salary_rule and (worked_days.SAL_SIN_PRES_SERV or 0) != 0.0:
        result =  round((worked_days.SAL_SIN_PRES_SERV.number_of_days or 0) * (version.wage /30))
#---------------------------------------Ajuste Dominical (Dev) // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_DOMINICAL',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_DOMINICAL', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_DOMINICAL', employee.type_employee.id)
if obj_salary_rule and (worked_days.get('WORK100') or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.get('WORK100') or 0).number_of_days
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Recargo nocturno dominical/festivo (2.25%) // Molpartes, Sole--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC009', employee.type_employee.id)
if obj_salary_rule:
    aplicar = int(obj_salary_rule.aplicar_cobro)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if (aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or inherit_contrato != 0:
        if obj_salary_rule:
            obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
            obj_overtime = payslip.get_overtime(employee.id, payslip.date_from, payslip.date_to, inherit_contrato)
            if obj_overtime:
                if obj_type_overtime.type_overtime == 'overtime_rnf' and obj_overtime.overtime_rnf > 0:
                    result = (version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) / annual_parameters.hours_monthly * 2.25
                    result_qty = obj_overtime.overtime_rnf
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC009', employee.type_employee.id)
aplicar = int(obj_salary_rule.aplicar_cobro)
day_initial_payrroll = payslip.date_from.day
day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
if ((aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll)) or (inherit_contrato!=0):
    if obj_salary_rule:
        obj_type_overtime = payslip.get_type_overtime(obj_salary_rule.id)
        obj_overtime = payslip.get_overtime(employee.id,payslip.date_from, payslip.date_to, inherit_contrato)
        if obj_overtime:
            if obj_type_overtime.type_overtime == 'overtime_rnf' and obj_overtime.overtime_rnf > 0:
                result = (((version.wage if version.wage >= annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly) /annual_parameters.hours_monthly)*2.15)
                result_qty = obj_overtime.overtime_rnf                  
#---------------------------------------Variacion Transitoria // Molpartes, Sole--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC_VTS', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                amount = obj_concept.amount / 30 * (worked_days.WORK100 or 0).number_of_days
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('HEYREC_VTS', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                amount = (obj_concept.amount/30)*(worked_days.WORK100.number_of_days or 0)
                result = amount if obj_salary_rule.dev_or_ded == 'devengo' else (amount)*-1
#---------------------------------------Ajuste Horas Extra (Dev) // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_HORASEXTRA',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_HORASEXTRA', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_HORASEXTRA', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Auxilio de Movilización_VT // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VIATICOS_NO_PRESTACIONALES',employee.type_employee.id)
if obj_salary_rule and rules_computed.dict.get('VIATICOS_PRESTACIONALES', 0) > 0:
    result = rules_computed.dict.get('VIATICOS_TOTAL', 0) - rules_computed.dict.get('VIATICOS_PRESTACIONALES', 0)
#---------------------------------------Intereses de Cesantias - Parcial Integral // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INTCESANTIAS_PARCIAL_INTEGRAL', employee.type_employee.id)
if obj_salary_rule and version.subcontract_type == 'obra_integral':
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    accumulated = payslip.get_accumulated_cesantias(date_start, date_end) + values_base_cesantias
    result = (accumulated + (categories.get('BASIC') or 0)) * 0.01
#---------------------------------------Prima - Parcial Integral // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRIMA_PARCIAL_INTEGRAL', employee.type_employee.id)
if obj_salary_rule and version.subcontract_type == 'obra_integral':
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_prima
        date_end = payslip.date_liquidacion
    accumulated = payslip.get_accumulated_prima(date_start, date_end) + values_base_prima
    result = (accumulated + (categories.get('BASIC') or 0)) * 0.0833
#---------------------------------------Vacaciones - Parcial Integral // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACACIONES_PARCIAL_INTEGRAL', employee.type_employee.id)
if obj_salary_rule and version.subcontract_type == 'obra_integral':
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_vacaciones
        date_end = payslip.date_liquidacion
    accumulated = payslip.get_accumulated_vacation_money(date_end, date_start) + values_base_vacremuneradas
    result = (accumulated + (categories.get('BASIC') or 0)) * 0.0417
#---------------------------------------Viáticos Total // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VIATICOS_TOTAL',employee.type_employee.id)
if obj_salary_rule and rules_computed.dict.get('VIATICOS_TOTAL', 0) > 0:
    result = rules_computed.dict.get('VIATICOS_TOTAL', 0)*-1    
#---------------------------------------Total devengos--------------------------------------------------------
#V19 AlianzaT
if inherit_contrato != 0:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES
else:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL
#V19 Molpartes, Tkarga
result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.PRESTACIONES_SOCIALES or 0)
#V19 Sole
result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES
#---------------------------------------Cobro de herramienta // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('COBRO001', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#---------------------------------------Faltante inventario // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('DEDUCCION004', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#---------------------------------------Descuento adelanto de nómina // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('DEDUCCION005', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#---------------------------------------Descuento Gafas // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('DEDUCCION007', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#---------------------------------------Descuento auxilio de rodamiento // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('DESCUENTO001', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#---------------------------------------Descuento celular // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EQUIPOCEL001', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#---------------------------------------Cuota Seguros Bolivar // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SEGUROS001', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                #dias = (worked_days.WORK100.number_of_days or 0)
                dias = (payslip.date_to - payslip.date_from).days + 1
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Descuento EMI // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('DESCUENTO002', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Embargo monto fijo--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO001',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO001', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO001', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO001', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Embargo salarial 1/5 smmvl // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO002',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            salario_minimo = annual_parameters.smmlv_monthly/2 if aplicar == 0 else annual_parameters.smmlv_monthly
            total = categories.DEV_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            val = round((total - salario_minimo)/5)
            result = val*-1 if val > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO002', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            salario_minimo = annual_parameters.smmlv_monthly / 2 if aplicar == 0 else annual_parameters.smmlv_monthly
            total = categories.get('DEV_SALARIAL') or 0 if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            val = round((total - salario_minimo) / 5)
            result = val * -1 if val > 0 else val
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO002', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            salario_minimo = annual_parameters.smmlv_monthly / 2 if aplicar == 0 else annual_parameters.smmlv_monthly
            total = categories.DEV_SALARIAL or 0 if aplicar == 0 else (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            val = round((total - salario_minimo) / 5)
            result = val * -1 if val > 0 else val
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo salarial 50% // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO003',employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            #total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            total = categories.DEV_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            porc = 50
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO003', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.get('DEV_SALARIAL') or 0 if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = int(obj_concept.amount if obj_concept.amount != 0 else 0)
            result = round(total * porc / 100)
            result_qty = 1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO003', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL or 0 if aplicar == 0 else (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 50
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo todo 50% // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO004',employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            #total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL + categories.PRESTACIONES_SOCIALES if aplicar == 0 else categories.DEV_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEV_NO_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('PRESTACIONES_SOCIALES', payslip.date_from, payslip.date_to)
            porc = 50            
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO004', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.get('PRESTACIONES_SOCIALES') or 0
            porc = 50
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO004', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) if aplicar == 0 else (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.PRESTACIONES_SOCIALES or 0
            porc = 50
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo todo 30% // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO005',employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            #total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0 or inherit_contrato!=0:
                total += categories.PRESTACIONES_SOCIALES
            porc = 30
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO005', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.get('PRESTACIONES_SOCIALES') or 0
            porc = 30
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO005', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) if aplicar == 0 else (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.PRESTACIONES_SOCIALES or 0
            porc = 30
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo salarial 25% // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO006',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            porc = 25
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO006', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.get('DEV_SALARIAL') or 0 if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 25
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO006', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL or 0 if aplicar == 0 else (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 25
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo salarial 15% // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO007',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            porc = 15
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO007', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.get('DEV_SALARIAL') or 0 if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 15
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO007', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL or 0 if aplicar == 0 else (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 15
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo todo 15% // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO008',employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0 or inherit_contrato!=0:
                total += categories.PRESTACIONES_SOCIALES
            porc = 15
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO008', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total = categories.get('PRESTACIONES_SOCIALES') or 0
            porc = 15
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO008', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) if aplicar == 0 else (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.PRESTACIONES_SOCIALES or 0
            porc = 15
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo todo 20% // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO009',employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0 or inherit_contrato!=0:
                total += categories.PRESTACIONES_SOCIALES
            porc = 20
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO009', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.get('PRESTACIONES_SOCIALES') or 0
            porc = 20
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO009', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) if aplicar == 0 else (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.PRESTACIONES_SOCIALES or 0
            porc = 20
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo todo 25% // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO010',employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0 or inherit_contrato!=0:
                total += categories.PRESTACIONES_SOCIALES
            porc = 25
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO010', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.get('PRESTACIONES_SOCIALES') or 0
            porc = 25
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO010', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.DEDUCCIONES or 0) if aplicar == 0 else (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) + (categories.DEDUCCIONES or 0) + payslip.sum_mount('DEDUCCIONES', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.PRESTACIONES_SOCIALES or 0
            porc = 25
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo todo 40% // AlianzaT, Molpartes--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO011',employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0 or inherit_contrato!=0:
                total += categories.PRESTACIONES_SOCIALES
            porc = 40
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO011', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.get('PRESTACIONES_SOCIALES') or 0
            porc = 14.66
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo salarial 20% // AlianzaT, Molpartes--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO012',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            porc = 20
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO012', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.get('PRESTACIONES_SOCIALES') or 0
            porc = 5
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo salarial 30% // AlianzaT, Molpartes--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO013',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL + categories.SSOCIAL if aplicar == 0 else categories.DEV_SALARIAL + categories.SSOCIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('SSOCIAL', payslip.date_from, payslip.date_to)
            porc = 30
            result = (round((total)*porc/100)*-1) if round((total)*porc/100) > 0 else 0
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO013', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + (categories.get('DEV_NO_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if inherit_prima != 0:
                total += categories.get('PRESTACIONES_SOCIALES') or 0
            porc = 40
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo salarial 30% // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO014', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.get('DEV_SALARIAL') or 0 if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 30
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo salarial 20% // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMBARGO015', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.get('DEV_SALARIAL') or 0 if aplicar == 0 else (categories.get('DEV_SALARIAL') or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = 20
            result = round(total * porc / 100) * -1
            result_qty = obj_concept.amount if obj_concept.amount != 0 else 0
#---------------------------------------Embargo Todo 50% (Prima) // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('EMBARGO020',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Ajuste Devolución Libranza / Otros (Dev) // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_LIBRANZA',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_LIBRANZA', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_LIBRANZA', employee.type_employee.id)
if obj_salary_rule and (worked_days.get('WORK100') or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.get('WORK100') or 0).number_of_days
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Ajuste Devolución Descuento Pensión // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_PENSION',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Libranzas--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('LIBRANZA001',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = (obj_concept.amount * dias)*-1
            else:
                result = (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LIBRANZA001', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LIBRANZA001', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = (obj_concept.amount * dias)*-1
            else:
                result = (obj_concept.amount)*-1                     
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('LIBRANZA001', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount * -1
#---------------------------------------Aportes a Cooperativas // AlianzaT, Sole, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('CUOTA002',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CUOTA002', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CUOTA002', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.get('WORK100') or 0).number_of_days
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Descuentos Cooperativas // AlianzaT, Tkarga--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('CUOTA003',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CUOTA003', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Anticipos no legalizados // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('ANTI', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#---------------------------------------Préstamos empresa--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO001',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO001', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO001', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1                   
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO001', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Anticipo de Nomina // Molpartes, Sole, Tkarga--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO002', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO002', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1          
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO002', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Préstamo Servicios Empresariales // Molpartes, Tkarga--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO003', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO003', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Préstamo de Estudios // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO004', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Otros Préstamos // Molpartes, Sole--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO005', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO005', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1     
#---------------------------------------Préstamo Vehículos // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO006', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Préstamo Pico y Placa Solidario // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO007', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Préstamo Dotación // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO008', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Préstamo Computador // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO009', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Préstamo Celular // Molpartes--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO010', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Descuento cuota sindical // AlianzaT, Molpartes, Sole--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('CUOTA001',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll): 
            result = (((version.wage/100)*1)/2)*-1 # Corresponde al 1% del salario
        else:
            result = ((version.wage/100)*1)*-1 # Corresponde al 1% del salario
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CUOTA001', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CUOTA001', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Cuota Sindical // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('CUOTAS004',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Descuento AFC--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AFC',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AFC', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AFC', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AFC', employee.type_employee.id)
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Aporte Voluntario // Molpartes, Sole--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AVP', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL or 0 if aplicar == 0 else (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            porc = int(obj_concept.amount if obj_concept.amount != 0 else 0)
            result = round(total * porc / 100) * -1
            result_qty = 1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AVP', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1 
#---------------------------------------Ahorro // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AHORRO001',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = (obj_concept.amount * dias)*-1
            else:
                result = (obj_concept.amount)*-1
#---------------------------------------Póliza Fúnebre--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('POLIZA001',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('POLIZA001', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = worked_days.WORK100.number_of_days or 0 if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('POLIZA001', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1    
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('POLIZA001', employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar == '30' and inherit_contrato != 0 else int(obj_concept.aplicar)
        if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * dias * -1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else obj_concept.amount * -1
#---------------------------------------Póliza Vida Prima extra // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('POLIZA002',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Sueldo imponible // Sole--------------------------------------------------------
#V19 Sole
result = categories['BASIC'] + categories['ALW']
            
#---------------------------------------Total Deducciones--------------------------------------------------------
#V19 AlianzaT, Sole
result = categories.DEDUCCIONES
#V19 Molpartes, Tkarga
result = (categories.DEDUCCIONES or 0)
#---------------------------------------Neto a pagar--------------------------------------------------------
#V19 AlianzaT
if inherit_contrato != 0 or inherit_prima != 0:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
else:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.DEDUCCIONES
#V19 Molpartes, Tkarga
result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.PRESTACIONES_SOCIALES or 0) + (categories.DEDUCCIONES or 0)
#V19 Sole
result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
#---------------------------------------Asignación salarial // Sole--------------------------------------------------------
#V19 Sole
result = -inputs['ASSIG_SALARY'].amount
result_name = inputs['ASSIG_SALARY'].name
            
#---------------------------------------Deducción salarial // Sole--------------------------------------------------------
#V19 Sole
result = -inputs['ATTACH_SALARY'].amount
result_name = inputs['ATTACH_SALARY'].name
            
#---------------------------------------Pensión alimenticia // Sole--------------------------------------------------------
#V19 Sole
result = -inputs['CHILD_SUPPORT'].amount
result_name = inputs['CHILD_SUPPORT'].name
            
#---------------------------------------Deducción // Sole--------------------------------------------------------
#V19 Sole
result = -inputs['DEDUCTION'].amount
result_name = inputs['DEDUCTION'].name
            
#---------------------------------------Reembolso // Sole--------------------------------------------------------
#V19 Sole
result = inputs['REIMBURSEMENT'].amount
result_name = inputs['REIMBURSEMENT'].name
            
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------LIQUIDACION DE NÓMINA - EMP PUBLICOS --------------------------------------------------------
#--------------------------------------- Prima técnica  --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMPPUBLICO_PRIMATECNICA', employee.type_employee.id)
if obj_salary_rule and dias != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        dias = 0 if aplicar == 0 else payslip.sum_days_works('WORK100', payslip.date_from,payslip.date_to) + payslip.sum_days_works('COMPENSATORIO',payslip.date_from,payslip.date_to)
        dias += worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
        dias += worked_days.COMPENSATORIO.number_of_days if worked_days.COMPENSATORIO else 0
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            result = (((version.wage/30)*dias)*(obj_concept.amount/100)) # total
#--------------------------------------- Gastos de representación  --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMPPUBLICO_GASTOSREPRESENTACION', employee.type_employee.id)
if obj_salary_rule and dias != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        dias = 0 if aplicar == 0 else payslip.sum_days_works('WORK100', payslip.date_from,payslip.date_to) + payslip.sum_days_works('COMPENSATORIO',payslip.date_from,payslip.date_to)
        dias += worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
        dias += worked_days.COMPENSATORIO.number_of_days if worked_days.COMPENSATORIO else 0
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            result = (((version.wage/30)*dias)*(obj_concept.amount/100)) # total
#--------------------------------------- Subsidio de alimentación  --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMPPUBLICO_SUBALIMENTACION',employee.type_employee.id)
if obj_salary_rule and dias != 0.0:
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(
        obj_salary_rule.aplicar_cobro)
    dias = 0 if aplicar == 0 else payslip.sum_days_works('WORK100', payslip.date_from,payslip.date_to) + payslip.sum_days_works('COMPENSATORIO',payslip.date_from,payslip.date_to)
    dias += worked_days.WORK100.number_of_days if worked_days.WORK100 else 0
    if worked_days.COMPENSATORIO != 0.0:
        dias += worked_days.COMPENSATORIO.number_of_days
    auxtransporte = annual_parameters.z_food_subsidy_amount
    auxtransporte_tope = annual_parameters.z_food_subsidy_tope
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        total = categories.DEV_SALARIAL if aplicar == 0 else categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
        if dias != 0.0:
            if version.not_validate_top_auxtransportation == True:
                result = round(dias * auxtransporte / 30)
            else:
                if (version.wage <= auxtransporte_tope) and (total <= auxtransporte_tope):
                    result = round(dias * auxtransporte /30)
#--------------------------------------- Bonificación de servicios prestados --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('EMPPUBLICO_BONISERVICIOSPRESTADOS',employee.type_employee.id)
if obj_salary_rule and dias != 0.0:
    lst_date_years = payslip.years_in_company(payslip.date_to)
    bool_calculation = False
    for date in lst_date_years:
        bool_calculation = True if date >= payslip.date_from and date <= payslip.date_to else False
    if bool_calculation:
        obj_salary_rule_prima = payslip.get_salary_rule('EMPPUBLICO_PRIMATECNICA', employee.type_employee.id)
        obj_concept_prima = payslip.get_concepts(version.id, obj_salary_rule_prima.id, id_version_concepts)
        obj_salary_rule_gastos = payslip.get_salary_rule('EMPPUBLICO_GASTOSREPRESENTACION', employee.type_employee.id)
        obj_concept_gastos = payslip.get_concepts(version.id, obj_salary_rule_gastos.id, id_version_concepts)
        amount = version.wage
        if obj_concept_prima:
            amount += (version.wage * (obj_concept_prima.amount / 100))
        if obj_concept_gastos:
            amount += (version.wage * (obj_concept_gastos.amount / 100))
        if amount > annual_parameters.z_bonus_services_rendered:
            result = amount * 0.35
        else:
            result = amount * 0.5
#--------------------------------------------------- Cuota Seguros Bolivar ------------------------------------------------------------------
#V17
result = 0.0
obj_salary_rule = payslip.get_salary_rule('SEGUROS001',employee.type_employee.id)
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                #dias = worked_days.WORK100.number_of_days
                dias = (payslip.date_to - payslip.date_from).days + 1
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------LIQUIDACION DE VACACIONES--------------------------------------------------------
#---------------------------------------Vacaciones Liq Contrato Base-----------------------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACCONTRATO',employee.type_employee.id)
if obj_salary_rule and inherit_contrato != 0:
    date_start = payslip.date_vacaciones
    date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_vacation_money(date_end) + values_base_vacremuneradas
    result = accumulated

#---------------------------------------Vacaciones Disfrutadas-----------------------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACDISFRUTADAS',employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACDISFRUTADAS != 0.0:
        if (employee.dias360(version.date_start, payslip.date_from)) >= 360:
            accumulated = payslip.get_accumulated_vacation(payslip.date_from) / 360
        else:
            accumulated = payslip.get_accumulated_vacation(payslip.date_from) / (employee.dias360(version.date_start, payslip.date_from))
        amount = version.wage / 30      
        result =  accumulated + amount
        result_qty = leaves.VACDISFRUTADAS


#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACDISFRUTADAS',employee.type_employee.id)
if obj_salary_rule:
    if (leaves.VACDISFRUTADAS or 0) != 0.0:
        accumulated = payslip.get_accumulated_vacation(payslip.date_from) / 360
        amount = version.wage / 30      
        result =  accumulated + amount
        result_qty = leaves.VACDISFRUTADAS
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACDISFRUTADAS', employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACDISFRUTADAS != 0.0:
        if employee.dias360(version.date_start, payslip.date_from) >= 360:
            accumulated = payslip.get_accumulated_vacation(payslip.date_from) / 360
        else:
            accumulated = payslip.get_accumulated_vacation(payslip.date_from) / employee.dias360(version.date_start, payslip.date_from)
        amount = version.wage / 30
        result = accumulated + amount
        result_qty = leaves.VACDISFRUTADAS
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACDISFRUTADAS', employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACDISFRUTADAS != 0.0:
        accumulated = payslip.get_accumulated_vacation(payslip.date_from) / 360
        amount = version.wage / 30      
        result =  accumulated + amount
        result_qty = leaves.VACDISFRUTADAS
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACDISFRUTADAS', employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACDISFRUTADAS != 0.0:
        accumulated = payslip.get_accumulated_vacation(payslip.date_from) / 360
        result = version.get_vacation_base_amount(version.wage + accumulated * 30, annual_parameters) / 30
        result_qty = leaves.VACDISFRUTADAS
#---------------------------------------Vacaciones Disfrutadas - Días Habiles--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VAC001',employee.type_employee.id)
if obj_salary_rule:
    if leaves.BUSINESSVACDISFRUTADAS != 0.0:
        accumulated = payslip.get_accumulated_vacation(payslip.date_from) / 360
        amount = version.wage / 30      
        result =  accumulated + amount
        result_qty = leaves.BUSINESSVACDISFRUTADAS

#---------------------------------------Vacaciones Disfrutadas - Días Festivos--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VAC002',employee.type_employee.id)
if obj_salary_rule:
    if leaves.HOLIDAYSVACDISFRUTADAS != 0.0:
        if ((payslip.date_to - version.date_start).days) >= 360:
            accumulated = payslip.get_accumulated_vacation(payslip.date_from) / 360
        else:
            accumulated = payslip.get_accumulated_vacation(payslip.date_from) / ((payslip.date_to - version.date_start).days)
        amount = version.wage / 30      
        result =  accumulated + amount
        result_qty = leaves.HOLIDAYSVACDISFRUTADAS

#---------------------------------------Vacaciones Remuneradas--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACREMUNERADAS',employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACREMUNERADAS != 0.0:
        accumulated = payslip.get_accumulated_vacation_money(payslip.date_from) / 360
        amount = version.wage / 30      
        result =  accumulated + amount
        result_qty = leaves.VACREMUNERADAS
#---------------------------------------Auxilio vacaciones pacto colectivo--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUXLIOVAC001',employee.type_employee.id)
if obj_salary_rule and employee.ed_qualification >= 4.5:
    obj_assistance_vacation = payslip.get_assistance_vacation(antiquity_employee)
    result = (version.wage / 30) * obj_assistance_vacation.vacation_relief 

#---------------------------------------Auxilio vacaciones convención--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUXLIOVAC002',employee.type_employee.id)
if obj_salary_rule:
    if employee.branch_id.name == 'Cartagena' and employee.labor_union_information:        
        obj_assistance_vacation = payslip.get_assistance_vacation(antiquity_employee)
        result = (version.wage / 30) * obj_assistance_vacation.convention_vacation

#-----------------------------------------------Prima de Vacaciones-------------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRIMAVAC',employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACDISFRUTADAS > 0:
        result = (VACDISFRUTADAS/leaves.VACDISFRUTADAS)*leaves.BUSINESSVACDISFRUTADAS

#----------------------------------------Bonificación Especial de Recreación----------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUX_ESPECIAL_RECREACION',employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACDISFRUTADAS > 0:
        days_process = 2 if leaves.BUSINESSVACDISFRUTADAS >= 15 else (leaves.BUSINESSVACDISFRUTADAS * 2) / 15
        #result = (VACDISFRUTADAS/leaves.VACDISFRUTADAS)*days_process
        result = (contrage.wage/30)*days_process

# ---------------------------------------Vacaciones - Parcial Integral SERVAGRO --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACACIONES_PARCIAL_INTEGRAL', employee.type_employee.id)
if obj_salary_rule and version.subcontract_type == 'obra_integral':
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_vacaciones
        date_end = payslip.date_liquidacion
    # Obtener acumulados
    accumulated = payslip.get_accumulated_vacation_money(date_end,date_start) + values_base_vacremuneradas
    result = (accumulated + categories.BASIC) * 0.0417
#---------------------------------------Vacaciones--------------------------------------------------------
#V19 AlianzaT, Molpartes, Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACCONTRATO',employee.type_employee.id)
if obj_salary_rule and inherit_contrato != 0:
    date_start = payslip.date_vacaciones
    date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_vacation_money(date_end) + values_base_vacremuneradas
    result = accumulated
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACCONTRATO', employee.type_employee.id)
if obj_salary_rule and inherit_contrato != 0:
    date_start = payslip.date_vacaciones
    date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_vacation_money(date_end) + values_base_vacremuneradas
    result = accumulated
#---------------------------------------Vacaciones Remuneradas--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACREMUNERADAS',employee.type_employee.id)
if obj_salary_rule:
    if (leaves.VACREMUNERADAS or 0) != 0.0:
        accumulated = payslip.get_accumulated_vacation_money(payslip.date_from) / 360
        amount = version.wage / 30      
        result =  accumulated + amount
        result_qty = leaves.VACREMUNERADAS
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACREMUNERADAS', employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACREMUNERADAS != 0.0:
        accumulated = payslip.get_accumulated_vacation_money(payslip.date_from) / 360
        amount = version.wage / 30
        result = accumulated + amount
        result_qty = leaves.VACREMUNERADAS
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACREMUNERADAS', employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACREMUNERADAS != 0.0:
        accumulated = payslip.get_accumulated_vacation_money(payslip.date_from) / 360
        amount = version.wage / 30      
        result =  accumulated + amount
        result_qty = leaves.VACREMUNERADAS
#V19 Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('VACREMUNERADAS', employee.type_employee.id)
if obj_salary_rule:
    if leaves.VACREMUNERADAS != 0.0:
        accumulated = payslip.get_accumulated_vacation_money(payslip.date_from) / 360
        result = version.get_vacation_base_amount(version.wage + accumulated * 30, annual_parameters) / 30
        result_qty = leaves.VACREMUNERADAS
#---------------------------------------Auxilio vacaciones pacto colectivo // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUXLIOVAC001',employee.type_employee.id)
if obj_salary_rule and employee.ed_qualification >= 4.5 and inherit_contrato == 0:
    obj_assistance_vacation = payslip.get_assistance_vacation(antiquity_employee)
    result = (version.wage / 30) * obj_assistance_vacation.vacation_relief
#---------------------------------------Auxilio vacaciones convención CCT // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AUXLIOVAC002',employee.type_employee.id)
if obj_salary_rule and inherit_contrato == 0:
    if employee.branch_id.name == 'Cartagena' and employee.labor_union_information:        
        obj_assistance_vacation = payslip.get_assistance_vacation(antiquity_employee)
        result = (version.wage / 30) * obj_assistance_vacation.convention_vacation
#---------------------------------------Neto a pagar--------------------------------------------------------
#V19 AlianzaT
result = 0
if inherit_contrato == 0:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
#V19 Molpartes
result = 0
if inherit_contrato == 0:
    result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.PRESTACIONES_SOCIALES or 0) + (categories.DEDUCCIONES or 0)
#V19 Sole, Tkarga
result = 0
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------LIQUIDACION DE CESANTIAS--------------------------------------------------------
#---------------------------------------Cesantias Base--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CESANTIAS',employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_cesantias(date_start,date_end) + values_base_cesantias
    result = accumulated

#---------------------------------------Cesantias - Parcial Integral SERVAGRO --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CESANTIAS_PARCIAL_INTEGRAL',employee.type_employee.id)
if obj_salary_rule and version.subcontract_type == 'obra_integral':
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_cesantias(date_start,date_end) + values_base_cesantias
    result = (accumulated + categories.BASIC) * 0.0833

#---------------------------------------Intereses de Cesantias Base--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INTCESANTIAS',employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_cesantias(date_start,date_end) + values_base_cesantias
    result = accumulated

#---------------------------------------Intereses de Cesantias - Parcial Integral SERVAGRO --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INTCESANTIAS_PARCIAL_INTEGRAL',employee.type_employee.id)
if obj_salary_rule and version.subcontract_type == 'obra_integral':
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_cesantias(date_start,date_end) + values_base_cesantias
    result = (accumulated + categories.BASIC) * 0.01
#---------------------------------------Cesantías--------------------------------------------------------
#V19 AlianzaT, Molpartes, Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CESANTIAS',employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_cesantias(date_start,date_end) + values_base_cesantias
    result = accumulated
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('CESANTIAS', employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_cesantias(date_start,date_end) + values_base_cesantias
    result = accumulated
#---------------------------------------Total devengos (Cesantías) // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
si heredar_contrato != 0: resultado = categorias.DEV_SALARIAL + categorias.DEV_NO_SALARIAL + categorias.PRESTACIONES_SOCIALES else: resultado = categorias.PRESTACIONES_SOCIALES
#V19 Molpartes
               si heredar_contrato != 0: resultado = categorias.DEV_SALARIAL + categorias.DEV_NO_SALARIAL + categorias.PRESTACIONES_SOCIALES else: resultado = categorias.PRESTACIONES_SOCIALES
#V19 Tkarga
                   si heredar_contrato != 0: resultado = categorias.DEV_SALARIAL + categorias.DEV_NO_SALARIAL + categorias.PRESTACIONES_SOCIALES else: resultado = categorias.PRESTACIONES_SOCIALES
#---------------------------------------Neto a pagar--------------------------------------------------------
#V19 AlianzaT, Sole
result = 0
if inherit_contrato == 0:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
#V19 Molpartes, Tkarga
result = 0
if inherit_contrato == 0:
    result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.PRESTACIONES_SOCIALES or 0) + (categories.DEDUCCIONES or 0)
#---------------------------------------Intereses a las Cesantías--------------------------------------------------------
#V19 AlianzaT, Molpartes, Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INTCESANTIAS',employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_cesantias(date_start,date_end) + values_base_cesantias
    result = accumulated
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('INTCESANTIAS', employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_cesantias
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_cesantias(date_start,date_end) + values_base_cesantias
    result = accumulated
#---------------------------------------Devengos totales (IntCesantías) // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT
si heredar_contrato != 0: resultado = categorias.DEV_SALARIAL + categorias.DEV_NO_SALARIAL + categorias.PRESTACIONES_SOCIALES else: resultado = categorias.PRESTACIONES_SOCIALES
#V19 Molpartes
                   	si heredar_contrato != 0: resultado = categorias.DEV_SALARIAL + categorias.DEV_NO_SALARIAL + categorias.PRESTACIONES_SOCIALES else: resultado = categorias.PRESTACIONES_SOCIALES
#V19 Tkarga
               	si heredar_contrato != 0: resultado = categorias.DEV_SALARIAL + categorias.DEV_NO_SALARIAL + categorias.PRESTACIONES_SOCIALES else: resultado = categorias.PRESTACIONES_SOCIALES
#---------------------------------------Neto a pagar--------------------------------------------------------
#V19 AlianzaT, Sole
result = 0
if inherit_contrato == 0:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
#V19 Molpartes, Tkarga
result = 0
if inherit_contrato == 0:
    result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.PRESTACIONES_SOCIALES or 0) + (categories.DEDUCCIONES or 0)
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------LIQUIDACION DE PRIMA--------------------------------------------------------
#---------------------------------------Prima Base--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRIMA',employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_prima
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_prima(date_start,date_end) + values_base_prima
    result = accumulated

#---------------------------------------Prima - Parcial Integral SERVAGRO --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRIMA_PARCIAL_INTEGRAL',employee.type_employee.id)
if obj_salary_rule and version.subcontract_type == 'obra_integral':
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_prima
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_prima(date_start,date_end) + values_base_prima
    result = (accumulated + categories.BASIC) * 0.0833
#---------------------------------------Retención en la fuente PRIMA --------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE_PRIMA001',employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje':
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            amount_process = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            amount_process += categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,payslip.date_to)
            if amount_process >= annual_parameters.value_top_source_retention:
                localdict = {
                            'categories': categories,
                            'rules_computed': rules_computed,
                            'payslip': payslip,
                            'employee': employee,
                            'version': version,
                            'annual_parameters':annual_parameters
                        }
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to,'103', localdict)
                result = (obj_retention.result_calculation) * -1
        else:
            result = (version.fixed_value_retention_procedure) * -1
#---------------------------------------Ajuste PRIMA (Dev) // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AJ_DEV_PRIMA',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Prima--------------------------------------------------------
#V19 AlianzaT, Molpartes, Tkarga
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRIMA',employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_prima
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_prima(date_start,date_end) + values_base_prima
    result = accumulated
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('PRIMA', employee.type_employee.id)
if obj_salary_rule:
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_prima
        date_end = payslip.date_liquidacion
    #Obtener acumulados
    accumulated = payslip.get_accumulated_prima(date_start,date_end) + values_base_prima
    result = accumulated
#---------------------------------------Retención en la fuente por salario - PRIMA // Molpartes, Sole--------------------------------------------------------
#V19 Molpartes
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE_PRIMA001', employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje' and (inherit_contrato == 0):
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)
    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            amount_process = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            amount_process += (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if amount_process >= annual_parameters.value_top_source_retention:
                localdict = {'categories': categories, 'rules_computed': rules_computed, 'payslip': payslip, 'employee': employee, 'version': version, 'annual_parameters': annual_parameters}
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to, '103', localdict)
                result = obj_retention.result_calculation * -1
        else:
            result = version.fixed_value_retention_procedure * -1
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE_PRIMA001', employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje' and inherit_contrato==0:
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
    if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            amount_process = categories.DEV_SALARIAL + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            amount_process += categories.DEV_NO_SALARIAL + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from,payslip.date_to)
            if amount_process >= annual_parameters.value_top_source_retention:
                localdict = {
                            'categories': categories,
                            'rules_computed': rules_computed,
                            'payslip': payslip,
                            'employee': employee,
                            'version': version,
                            'annual_parameters':annual_parameters
                        }
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to,'103', localdict)
                result = (obj_retention.result_calculation) * -1
        else:
            result = (version.fixed_value_retention_procedure) * -1
#---------------------------------------Total Deducciones(Prima) // AlianzaT, Molpartes, Tkarga--------------------------------------------------------
#V19 AlianzaT, Tkarga
resultado = categorias.DEDUCCIONES
#V19 Molpartes
                    	resultado = categorias.DEDUCCIONES
#---------------------------------------Neto a pagar--------------------------------------------------------
#V19 AlianzaT, Sole
result = 0
if inherit_contrato == 0:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
#V19 Molpartes, Tkarga
result = 0
if inherit_contrato == 0:
    result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.PRESTACIONES_SOCIALES or 0) + (categories.DEDUCCIONES or 0)
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------LIQUIDACION DE CONTRATO--------------------------------------------------------
#---------------------------------------Indemnización contrato diferente a termino fijo--------------------------------------------------------
result = 0.0
if payslip.have_compensation and version.contract_type != 'fijo' and version.modality_salary != 'integral':
    dias = payslip.days_between(version.date_start, payslip.date_liquidacion)
    antiguedad = dias / 360.0
    vr_mas_ano = 0.0
    vr_ano = 0.0

    salario =  version.wage
    date_to = version.date_to if version.date_to else version.date_end

    if date_to:
        dias_indemnizados = payslip.days_between(payslip.date_liquidacion, date_to)
        dias_indemnizados = dias_indemnizados - 1
    else:
        dias_indemnizados = 0

    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_from
        date_end = payslip.date_liquidacion
    # Obtener acumulados
    accumulated = payslip.get_accumulated_compensation(date_start, date_end, values_base_compensation)
    total = salario + accumulated
    if dias_indemnizados == 0:
        if round(total / annual_parameters.smmlv_monthly) < 10.0:
            vr_ano = total
            if antiguedad > 1:   
                vr_mas_ano = (((dias - 360.0) * 20.0)/360.0) * (total /30.0)
        else:
            vr_ano = round((total /30.0)*20.0)
            if antiguedad > 1:   
                vr_mas_ano = (((dias - 360.0) * 15.0)/360.0) * (total /30.0)
    else:
        vr_ano = dias_indemnizados * (total /30.0)
    
    result = round(vr_ano + vr_mas_ano)

#---------------------------------------Indemnización contrato termino fijo--------------------------------------------------------
result = 0.0
if payslip.have_compensation and version.contract_type == 'fijo' and version.modality_salary != 'integral':
    date_to = version.date_to if version.date_to else version.date_end
    dias = payslip.days_between(payslip.date_liquidacion, date_to)     
    salario_dia =  version.wage/30
    result = salario_dia
    result_qty = dias

#---------------------------------------Indemnización salario integral--------------------------------------------------------
result = 0.0
if payslip.have_compensation and version.modality_salary == 'integral':
    dias = payslip.days_between(version.date_start, payslip.date_liquidacion)
    antiguedad = dias / 360.0
    vr_mas_ano = 0.0
    vr_ano = 0.0
    salario=version.wage
    vr_ano = round(salario/30.0)*20.0 
    if antiguedad > 1:   
        vr_mas_ano = (((dias - 360.0) * 15.0)/360.0) * (salario/30.0)
    
    result = round(vr_ano + vr_mas_ano)



#V19
result = 0.0
obj_salary_rule = payslip.get_salary_rule('RETFTE_PRIMA001', employee.type_employee.id)
if obj_salary_rule and version.contract_type != 'aprendizaje' and (inherit_contrato == 0):
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28, 29) else payslip.date_to.day
    aplicar = 0 if obj_salary_rule.aplicar_cobro == '30' and inherit_contrato != 0 else int(obj_salary_rule.aplicar_cobro)
    if aplicar == 0 or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
        if version.retention_procedure != 'fixed':
            amount_process = (categories.DEV_SALARIAL or 0) + payslip.sum_mount('DEV_SALARIAL', payslip.date_from, payslip.date_to)
            amount_process += (categories.DEV_NO_SALARIAL or 0) + payslip.sum_mount('DEV_NO_SALARIAL', payslip.date_from, payslip.date_to)
            if amount_process >= annual_parameters.value_top_source_retention:
                localdict = {'categories': categories, 'rules_computed': rules_computed, 'payslip': payslip, 'employee': employee, 'version': version, 'annual_parameters': annual_parameters}
                obj_retention = payslip.get_deduction_retention(employee.id, payslip.date_to, '103', localdict)
                result = obj_retention.result_calculation * -1
        else:
            result = version.fixed_value_retention_procedure * -1
#---------------------------------------Descuento UPC--------------------------------------------------------
result = 0.0
obj_salary_rule = payslip.get_salary_rule('DESCUENTO_UPC',employee.type_employee.id)
aplicar = 0 if obj_salary_rule.aplicar_cobro=='30' and inherit_contrato!=0 else int(obj_salary_rule.aplicar_cobro)
if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
    for dependent_upc in employee.dependents_information:
        if dependent_upc.z_upc_payment:
            for upc_config in annual_parameters.z_upc_lines_ids:
                age = employee.get_age_for_date(dependent_upc.date_birthday)
                lst_validation = [
                    ('age<1', age < 1),
                    ('age>1 and age<=4', age > 1 and age <= 4),
                    ('age>=5 and age<=14', age >= 5 and age <= 14),
                    ('age>=15 and age<=18', age >= 15 and age <= 18),
                    ('age>=19 and age<=44', age >= 19 and age <= 44),
                    ('age>=45 and age<=49', age >= 45 and age <= 49),
                    ('age>=50 and age<=54', age >= 50 and age <= 54),
                    ('age>=55 and age<=59', age >= 55 and age <= 59),
                    ('age>=60 and age<=64', age >= 60 and age <= 64),
                    ('age>=65 and age<=69', age >= 65 and age <= 69),
                    ('age>=70 and age<=74', age >= 70 and age <= 74),
                    ('age>=75', age >= 75)
                ]
                for validation in lst_validation:
                    if validation[1] == True and upc_config.z_age_group_upc == validation[0]:
                        if upc_config.z_gender_upc == dependent_upc.genero:
                            if dependent_upc.z_upc_geographic_area == 'ZN':
                                result += upc_config.z_normal_zone_upc
                            elif dependent_upc.z_upc_geographic_area == 'ZE':
                                result += upc_config.z_special_zone_upc
                            elif dependent_upc.z_upc_geographic_area == 'CD':
                                result += upc_config.z_cities_upc
                            elif dependent_upc.z_upc_geographic_area == 'IS':
                                result += upc_config.z_islands_upc
                            else:
                                result += 0
    if result > 0 and aplicar == 0:
        result = (result/2)*-1
    else:
        result = result*-1

#---------------------------------------Indemnización Contrato Indefinido--------------------------------------------------------
#V19 AlianzaT
result = 0.0
if payslip.have_compensation and version.contract_type != 'fijo' :
    dias = payslip.days_between(version.date_start, payslip.date_liquidacion)
    antiguedad = dias / 360.0
    vr_mas_ano = 0.0
    vr_ano = 0.0

    salario =  version.wage
    date_to = version.date_to if version.date_to else version.date_end

    if date_to:
        dias_indemnizados = payslip.days_between(payslip.date_liquidacion, date_to)
        dias_indemnizados = dias_indemnizados - 1
    else:
        dias_indemnizados = 0

    if dias_indemnizados == 0:
        if round(salario / annual_parameters.smmlv_monthly) < 10.0:     
            vr_ano = salario
            if antiguedad > 1:   
                vr_mas_ano = (((dias - 360.0) * 20.0)/360.0) * (salario /30.0)
        else:
            vr_ano = round((salario /30.0)*20.0) 
            if antiguedad > 1:   
                vr_mas_ano = (((dias - 360.0) * 15.0)/360.0) * (salario /30.0)
    else:
        vr_ano = dias_indemnizados * (salario /30.0)
    
    result = round(vr_ano + vr_mas_ano)
#V19 Molpartes
result = 0.0
if payslip.have_compensation and version.contract_type != 'fijo':
    dias = payslip.days_between(version.date_start, payslip.date_liquidacion)
    antiguedad = dias / 360.0
    vr_mas_ano = 0.0
    vr_ano = 0.0
    salario = version.wage
    date_to = version.date_to if version.date_to else version.date_end
    if date_to:
        dias_indemnizados = payslip.days_between(payslip.date_liquidacion, date_to)
        dias_indemnizados = dias_indemnizados - 1
    else:
        dias_indemnizados = 0
    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_from
        date_end = payslip.date_liquidacion
    accumulated = payslip.get_accumulated_compensation(date_start, date_end, values_base_compensation)
    total = salario + accumulated
    if dias_indemnizados == 0:
        if round(total / annual_parameters.smmlv_monthly) < 10.0:
            vr_ano = total
            if antiguedad > 1:
                vr_mas_ano = (dias - 360.0) * 20.0 / 360.0 * (total / 30.0)
        else:
            vr_ano = round(total / 30.0 * 20.0)
            if antiguedad > 1:
                vr_mas_ano = (dias - 360.0) * 15.0 / 360.0 * (total / 30.0)
    else:
        vr_ano = dias_indemnizados * (total / 30.0)
    result = round(vr_ano + vr_mas_ano)
#V19 Sole
result = 0.0
if payslip.have_compensation and version.contract_type != 'fijo' :
    dias = payslip.days_between(version.date_start, payslip.date_liquidacion)
    antiguedad = dias / 360.0
    vr_mas_ano = 0.0
    vr_ano = 0.0

    salario =  version.wage
    date_to = version.date_to if version.date_to else version.date_end

    if date_to:
        dias_indemnizados = payslip.days_between(payslip.date_liquidacion, date_to)
        dias_indemnizados = dias_indemnizados - 1
    else:
        dias_indemnizados = 0

    date_start = payslip.date_from
    date_end = payslip.date_to
    if inherit_contrato != 0:
        date_start = payslip.date_from
        date_end = payslip.date_liquidacion
    # Obtener acumulados
    accumulated = payslip.get_accumulated_compensation(date_start, date_end, values_base_compensation)
    total = salario + accumulated
    if dias_indemnizados == 0:
        if round(total / annual_parameters.smmlv_monthly) < 10.0:
            vr_ano = total
            if antiguedad > 1:   
                vr_mas_ano = (((dias - 360.0) * 20.0)/360.0) * (total /30.0)
        else:
            vr_ano = round((total /30.0)*20.0)
            if antiguedad > 1:   
                vr_mas_ano = (((dias - 360.0) * 15.0)/360.0) * (total /30.0)
    else:
        vr_ano = dias_indemnizados * (total /30.0)
    
    result = round(vr_ano + vr_mas_ano)
#V19 Tkarga
result = 0.0
if payslip.have_compensation and version.contract_type != 'fijo' and (version.modality_salary != 'integral'):
    dias = payslip.days_between(version.date_start, payslip.date_liquidacion)
    antiguedad = dias / 360.0
    vr_mas_ano = 0.0
    vr_ano = 0.0
    salario = version.wage
    date_to = version.date_to if version.date_to else version.date_end
    if date_to:
        dias_indemnizados = payslip.days_between(payslip.date_liquidacion, date_to)
        dias_indemnizados = dias_indemnizados - 1
    else:
        dias_indemnizados = 0
    if dias_indemnizados == 0:
        if round(salario / annual_parameters.smmlv_monthly) < 10.0:
            vr_ano = salario
            if antiguedad > 1:
                vr_mas_ano = (dias - 360.0) * 20.0 / 360.0 * (salario / 30.0)
        else:
            vr_ano = round(salario / 30.0 * 20.0)
            if antiguedad > 1:
                vr_mas_ano = (dias - 360.0) * 15.0 / 360.0 * (salario / 30.0)
    else:
        vr_ano = dias_indemnizados * (salario / 30.0)
    result = round(vr_ano + vr_mas_ano)
#---------------------------------------Indemnización Contrato Término Fijo--------------------------------------------------------
#V19 AlianzaT, Sole
result = 0.0
if payslip.have_compensation and version.contract_type == 'fijo' and version.modality_salary != 'integral':
    date_to = version.date_to if version.date_to else version.date_end
    dias = payslip.days_between(payslip.date_liquidacion, date_to) - 1    
    salario_dia =  version.wage/30
    result = salario_dia
    result_qty = dias
#V19 Molpartes, Tkarga
result = 0.0
if payslip.have_compensation and version.contract_type == 'fijo' and (version.modality_salary != 'integral'):
    date_to = version.date_to if version.date_to else version.date_end
    dias = payslip.days_between(payslip.date_liquidacion, date_to) - 1
    salario_dia = version.wage / 30
    result = salario_dia
    result_qty = dias
#---------------------------------------Indemnización Salario Integral // Molpartes, Tkarga--------------------------------------------------------
#V19 Molpartes, Tkarga
result = 0.0
if payslip.have_compensation and version.modality_salary == 'integral':
    dias = payslip.days_between(version.date_start, payslip.date_liquidacion)
    antiguedad = dias / 360.0
    vr_mas_ano = 0.0
    vr_ano = 0.0
    salario = version.wage
    vr_ano = round(salario / 30.0) * 20.0
    if antiguedad > 1:
        vr_mas_ano = (dias - 360.0) * 15.0 / 360.0 * (salario / 30.0)
    result = round(vr_ano + vr_mas_ano)
#---------------------------------------Neto a pagar // Molpartes, Sole, Tkarga--------------------------------------------------------
#V19 Molpartes, Tkarga
result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.PRESTACIONES_SOCIALES or 0) + (categories.DEDUCCIONES or 0)
#V19 Sole
result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------TOTALES--------------------------------------------------------
#---------------------------------------Total devengos--------------------------------------------------------
if inherit_contrato != 0:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES
else:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL

#---------------------------------------Total deducciones--------------------------------------------------------
result = categories.DEDUCCIONES

#---------------------------------------Neto a pagar--------------------------------------------------------
if inherit_contrato != 0:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
else:
    result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.DEDUCCIONES

#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------LIQUIDACION OTRO // AlianzaT, Molpartes, Sole, Tkarga--------------------------------------------------------
#---------------------------------------Ajuste salario Independiente // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_SALARIO_INDEPEN', employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Acta de transacción // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX008',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Bono por mera liberalidad // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX009',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Fondo de Salud Art 9 // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX010',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Auxilio de Maternidad // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX011',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Bonificación por pensión de vejez // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX012',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Bono Navideño // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX013',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Viaticos // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX010',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------PACTO - AUXILIO FUNEBRE // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX015',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Art Auxilio Escolar para estudiantes de Preescolar, Primaria y Secundaria // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX016',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Art 13 Auxilio para la Educación - Bono Académico // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX017',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Art Credito para Educación // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX018',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------PACTO - CLAUSULA 7 - AUXILIO DE MATERNIDAD // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX019',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Auxilio Navideño // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX020',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------CCT - Bono Mesa de Negociación // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('AUX021',employee.type_employee.id) 
if obj_salary_rule and (worked_days.WORK100 or 0) != 0.0:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0)
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Préstamo Independiente // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('PRESTAMO001',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Indemnización Salario Integral // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
if payslip.have_compensation and version.modality_salary == 'integral':
    dias = payslip.days_between(version.date_start, payslip.date_liquidacion)
    antiguedad = dias / 360.0
    vr_mas_ano = 0.0
    vr_ano = 0.0
    salario=version.wage
    vr_ano = round(salario/30.0)*20.0 
    if antiguedad > 1:   
        vr_mas_ano = (((dias - 360.0) * 15.0)/360.0) * (salario/30.0)
    
    result = round(vr_ano + vr_mas_ano)
#---------------------------------------Devengos totales (NI) // Molpartes--------------------------------------------------------
#V19 Molpartes
                  resultado = categorias.DEV_SALARIAL + categorias.DEV_NO_SALARIAL + categorias.PRESTACIONES_SOCIALES
#---------------------------------------Ajuste Salud Independiente // Sole--------------------------------------------------------
#V19 Sole
result = 0.0
obj_salary_rule = payslip.get_salary_rule('AJ_SALUD', employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id, obj_salary_rule.id, id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1    
#---------------------------------------Retención en la fuente por salario - vf - // AlianzaT--------------------------------------------------------
#V19 AlianzaT
result = 0.0
try:
    id_version_concepts
except Exception:
    id_version_concepts = 0
obj_salary_rule = payslip.get_salary_rule('RETFTE_FIJO',employee.type_employee.id) 
if obj_salary_rule:
    obj_concept = payslip.get_concepts(version.id,obj_salary_rule.id,id_version_concepts)
    day_initial_payrroll = payslip.date_from.day
    day_end_payrroll = 30 if payslip.date_to.month == 2 and payslip.date_to.day in (28,29) else payslip.date_to.day
    if obj_concept:
        aplicar = 0 if obj_concept.aplicar=='30' and inherit_contrato!=0 else int(obj_concept.aplicar)
        if (aplicar == 0) or (aplicar >= day_initial_payrroll and aplicar <= day_end_payrroll):
            if obj_salary_rule.modality_value == 'diario':
                dias = (worked_days.WORK100.number_of_days or 0) if (worked_days.WORK100 or 0) != 0.0 else 0
                result = obj_concept.amount * dias if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount * dias)*-1
            else:
                result = obj_concept.amount if obj_salary_rule.dev_or_ded == 'devengo' else (obj_concept.amount)*-1
#---------------------------------------Deducciones Totales(NI) // Molpartes--------------------------------------------------------
#V19 Molpartes
               resultado = categorias.DEDUCCIONES
#---------------------------------------Neto a Pagar--------------------------------------------------------
#V19 AlianzaT, Sole
result = categories.DEV_SALARIAL + categories.DEV_NO_SALARIAL + categories.PRESTACIONES_SOCIALES + categories.DEDUCCIONES
#V19 Molpartes
result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.DEDUCCIONES or 0)
#V19 Tkarga
result = (categories.DEV_SALARIAL or 0) + (categories.DEV_NO_SALARIAL or 0) + (categories.PRESTACIONES_SOCIALES or 0) + (categories.DEDUCCIONES or 0)










--------------------------------XML nómina electrónica--------------------------------

# NominaIndividual - 1
# Código atributos
nsmap={None:"dian:gov:co:facturaelectronica:NominaIndividual","xs":"http://www.w3.org/2001/XMLSchema-instance","ds":"http://www.w3.org/2000/09/xmldsig#","ext":"urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2","xades":"http://uri.etsi.org/01903/v1.3.2#","xades141":"http://uri.etsi.org/01903/v1.4.1#","xsi":"http://www.w3.org/2001/XMLSchema-instance"},SchemaLocation=""

# Periodo - 3
# Código atributos
FechaIngreso=str(o.version_id.date_start),FechaLiquidacionInicio =o.get_dates_process(),FechaLiquidacionFin=o.get_dates_process(1),TiempoLaborado=str(abs(o.get_time_working())),FechaGen=o.get_date_now()
# Código validación
validation = False if o.version_id.retirement_date else True

# Periodo - 3
# Código atributos
FechaIngreso=str(o.version_id.date_start),FechaLiquidacionInicio =o.get_dates_process(),FechaLiquidacionFin=o.get_dates_process(1),TiempoLaborado=str(abs(o.get_time_working())),FechaGen=o.get_date_now(),FechaRetiro=str(o.version_id.retirement_date) if o.version_id.retirement_date else ""
# Código validación
validation = True if o.version_id.retirement_date else False

# NumeroSecuenciaXML - 4
# Código atributos
CodigoTrabajador=o.employee_id.identification_id,Prefijo=o.electronic_payroll_id.prefix,Consecutivo=str(o.item),Numero=o.electronic_payroll_id.prefix+str(o.item)

# LugarGeneracionXML - 5
# Código atributos
Pais=o.employee_id.partner_encab_id.country_id.code,DepartamentoEstado=o.employee_id.partner_encab_id.x_city.code[0:2],MunicipioCiudad=o.employee_id.partner_encab_id.x_city.code,Idioma="es"

# InformacionGeneral - 6
# Código atributos
Version="V1.0: Documento Soporte de Pago de Nómina Electrónica",Ambiente="1",TipoXML="102",FechaGen=o.get_date_now(),HoraGen=o.get_time_now(),PeriodoNomina="5",TipoMoneda="COP",TRM="0.00"

# Empleador - 7
# Código atributos
RazonSocial=o.employee_id.company_id.name,NIT=str(o.employee_id.company_id.partner_id.vat),DV=str(o.employee_id.company_id.partner_id.x_digit_verification),Pais=o.employee_id.company_id.partner_id.country_id.code,DepartamentoEstado=o.employee_id.company_id.partner_id.x_city.code[0:2],MunicipioCiudad=o.employee_id.company_id.partner_id.x_city.code,Direccion=o.employee_id.company_id.partner_id.street

# Trabajador - 8
# Código atributos
TipoTrabajador=o.employee_id.tipo_coti_id.code,SubTipoTrabajador="00",AltoRiesgoPension="false",TipoDocumento=o.employee_id.partner_encab_id.l10n_latam_identification_type_id.z_code_dian,NumeroDocumento=o.employee_id.partner_encab_id.vat,PrimerApellido=o.employee_id.partner_encab_id.x_first_lastname,SegundoApellido=o.employee_id.partner_encab_id.x_second_lastname if o.employee_id.partner_encab_id.x_second_lastname else " ",PrimerNombre=o.employee_id.partner_encab_id.x_first_name,OtrosNombres=o.employee_id.partner_encab_id.x_second_name if o.employee_id.partner_encab_id.x_second_name else " ",LugarTrabajoPais=o.employee_id.partner_encab_id.country_id.code,LugarTrabajoDepartamentoEstado=o.employee_id.partner_encab_id.city_id.z_code_dian[0:2],LugarTrabajoMunicipioCiudad=o.employee_id.partner_encab_id.city_id.z_code_dian,LugarTrabajoDireccion=o.employee_id.partner_encab_id.street if  o.employee_id.partner_encab_id.street else "",SalarioIntegral="true" if o.version_id.modality_salary=="integral" else "false",TipoContrato=o.get_type_version(),Sueldo=str(o.version_id.wage)

# Pago - 9
# Código atributos
Forma="1",Metodo="47",Banco=o.get_bank_information(r_bank=1),TipoCuenta=o.get_bank_information(r_type=1),NumeroCuenta=o.get_bank_information(r_account=1)

# Basico - 13
# Código atributos
DiasTrabajados= str(int(o.get_quantity_salary_rules_exclude_prima(['BASICTURNOS'])/8)) if int(o.get_quantity_salary_rules_exclude_prima(['BASICTURNOS'])) > 0 else str(o.get_days_lines_exclude_prima(['WORK100'])),SueldoTrabajado=str(o.get_value_salary_rules(['BASIC','BASIC002','BASIC003','BASICTURNOS']) if o.get_value_salary_rules(['BASIC','BASIC002','BASIC003','BASICTURNOS']) > 0 else 0.0)

# Transporte - 14
# Código atributos
AuxilioTransporte=str(o.get_value_salary_rules(['AUX000','AUX000TURNOS','AJ_DEV_AUX_TRANS','AJ_DED_AUX_TRANS','AUX001'])),ViaticoManuAlojNS=str(o.get_value_salary_rules(['AJ_DED_AUX_MOVILIZ','AUX002']))
# Código validación
validation = o.get_value_salary_rules(['AUX000','AUX000TURNOS','AJ_DEV_AUX_TRANS','AJ_DED_AUX_TRANS','AUX001','AJ_DED_AUX_MOVILIZ','AUX002']) > 0

# HED - 16
# Código atributos
Cantidad = str(round(o.get_quantity_salary_rules([o.get_type_overtime(1).salary_rule.code]), 2)),Porcentaje=str(o.get_type_overtime(1).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(1).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(1).salary_rule.code]) > 0

# HEN - 18
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(2).salary_rule.code])),Porcentaje=str(o.get_type_overtime(2).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(2).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(2).salary_rule.code]) > 0

# HRN - 20
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(3).salary_rule.code])),Porcentaje=str(o.get_type_overtime(3).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(3).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(3).salary_rule.code]) > 0

# HEDDF - 22
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(4).salary_rule.code])),Porcentaje=str(o.get_type_overtime(4).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(4).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(4).salary_rule.code]) > 0

# HRDDF - 24
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(5).salary_rule.code])),Porcentaje=str(o.get_type_overtime(5).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(5).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(5).salary_rule.code]) > 0

# HENDF - 26
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(6).salary_rule.code])),Porcentaje=str(o.get_type_overtime(6).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(6).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(6).salary_rule.code]) > 0

# HRNDF - 28
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(7).salary_rule.code])),Porcentaje=str(o.get_type_overtime(7).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(7).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(7).salary_rule.code]) > 0

# VacacionesComunes - 30
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['VACDISFRUTADAS']))),Pago=str(o.get_value_salary_rules(['VACDISFRUTADAS']))
# Código validación
validation = o.get_value_salary_rules(['VACDISFRUTADAS']) > 0

# VacacionesCompensadas - 31
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['VACREMUNERADAS','VACCONTRATO','VACACIONES_PARCIAL_INTEGRAL']))) if int(o.get_quantity_salary_rules(['VACREMUNERADAS','VACCONTRATO','VACACIONES_PARCIAL_INTEGRAL'])) <= 99 else "99",Pago=str(o.get_value_salary_rules(['VACREMUNERADAS','VACCONTRATO','VACACIONES_PARCIAL_INTEGRAL']))
# Código validación
validation = o.get_value_salary_rules(['VACREMUNERADAS','VACCONTRATO','VACACIONES_PARCIAL_INTEGRAL']) > 0

# Primas - 32
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['PRIMA','PRIMA_PARCIAL_INTEGRAL']))),Pago=str(o.get_value_salary_rules(['PRIMA','AJ_DEV_PRIMA','PRIMA_PARCIAL_INTEGRAL','AJ_DED_PRIMA', 'AJ_DED_AUX_NOSAL', 'AJ_DEDUC_PRIMA']))
# Código validación
validation = o.get_value_salary_rules(['PRIMA','AJ_DEV_PRIMA','PRIMA_PARCIAL_INTEGRAL','AJ_DED_PRIMA', 'AJ_DED_AUX_NOSAL', 'AJ_DEDUC_PRIMA'])> 0

# Cesantias - 33
# Código atributos
Pago=str(o.get_value_salary_rules(['CESANTIAS','CESANTIAS_PARCIAL_INTEGRAL'])),Porcentaje="12.00",PagoIntereses=str(o.get_value_salary_rules(['INTCESANTIAS','INTCESANTIAS_PARCIAL_INTEGRAL']))
# Código validación
validation = o.get_value_salary_rules(['CESANTIAS','CESANTIAS_PARCIAL_INTEGRAL','INTCESANTIAS','INTCESANTIAS_PARCIAL_INTEGRAL']) > 0

# Incapacidad - 35
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['INCAPACIDAD001','INCAPACIDAD002','INCAPACIDAD003','INCAPACIDAD004','INCAPACIDAD007','INCAPACIDAD008']))),Tipo="1",Pago=str(o.get_value_salary_rules(['INCAPACIDAD001','INCAPACIDAD002','INCAPACIDAD003','INCAPACIDAD004','INCAPACIDAD007','INCAPACIDAD008']))
# Código validación
validation = o.get_value_salary_rules(['INCAPACIDAD001','INCAPACIDAD002','INCAPACIDAD003','INCAPACIDAD004','INCAPACIDAD007','INCAPACIDAD008']) > 0

# Incapacidad - 36
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['INCAPACIDAD005']))),Tipo="2",Pago=str(o.get_value_salary_rules(['INCAPACIDAD005']))
# Código validación
validation = o.get_value_salary_rules(['INCAPACIDAD005'])> 0

# Incapacidad - 37
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['INCAPACIDAD006']))),Tipo="3",Pago=str(o.get_value_salary_rules(['INCAPACIDAD006']))
# Código validación
validation = o.get_value_salary_rules(['INCAPACIDAD006']) > 0

# LicenciaMP - 39
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['LICENCIA002','LICENCIA003']))),Pago=str(o.get_value_salary_rules(['LICENCIA002','LICENCIA003',LICENCIA006]))
# Código validación
validation = o.get_value_salary_rules(['LICENCIA002','LICENCIA003','LICENCIA006']) > 0

# LicenciaR - 40
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['LICENCIA001','LICENCIA004','LICENCIA005','COMPENSATORIO']))),Pago=str(o.get_value_salary_rules(['LICENCIA001','LICENCIA004','LICENCIA005','LICENCIA007','COMPENSATORIO']))
# Código validación
validation = o.get_value_salary_rules(['LICENCIA001','LICENCIA004','LICENCIA005','LICENCIA007','COMPENSATORIO']) > 0

# LicenciaNR - 41
# Código atributos
Cantidad=str(int(o.get_days_lines_exclude_prima(['LICENCIA_NO_REMUNERADA','SANCION','SUSP_CONTRATO','INAS_INJU'])))
# Código validación
validation = o.get_days_lines_exclude_prima(['LICENCIA_NO_REMUNERADA','SANCION','SUSP_CONTRATO','INAS_INJU']) > 0

# Bonificacion - 43
# Código atributos
BonificacionS=str(o.get_value_salary_rules(['BONI001','BONI002','BONI003','AJ_DED_BONIFICACION'])),BonificacionNS="0"
# Código validación
validation = o.get_value_salary_rules(['BONI001','BONI002','BONI003','AJ_DED_BONIFICACION']) > 0

# Auxilio - 45
# Código atributos
AuxilioS="0",AuxilioNS=str(o.get_value_salary_rules(['AUX003','AUX004','AUX005','AUX007','AUXLIOVAC001','AUXLIOVAC002','AUX008','AUX009','AJ_DEV_AUX_NOSAL','AUX050','AUX006']))
# Código validación
validation = o.get_value_salary_rules(['AUX003','AUX004','AUX005','AUX007','AUXLIOVAC001','AUXLIOVAC002','AUX008','AUX009','AJ_DEV_AUX_NOSAL','AUX050','AUX006']) > 0

# OtroConcepto - 49
# Código atributos
DescripcionConcepto="OTROS DEVENGOS",ConceptoS=str(int(round(o.get_value_salary_rules(['AJ_DEV_BASICO','AJ_DEV_INCAPACIDAD','AJ_DEV_DOMINICAL','AJ_DEV_HORASEXTRA','VIATICOS_PRESTACIONALES', 'VIATICOS_NO_PRESTACIONALES', 'VIATICOS_TOTAL','IMPUESTO_ASUM'', 'SANCION001', 'SANCION002', 'SANCION003','DESCUENTOHORAS','AJ_DEV_DESC','AJUST_RETE_DEV', 'AJ_DED_INCAPACIDAD'])))),ConceptoNS="0"
# Código validación
validation = o.get_value_salary_rules(['AJ_DEV_BASICO','AJ_DEV_INCAPACIDAD','AJ_DEV_DOMINICAL','AJ_DEV_HORASEXTRA','VIATICOS_PRESTACIONALES', 'VIATICOS_NO_PRESTACIONALES', 'VIATICOS_TOTAL','IMPUESTO_ASUM', 'SANCION001', 'SANCION002', 'SANCION003','DESCUENTOHORAS','AJ_DEV_DESC','AJUST_RETE_DEV', 'AJ_DED_INCAPACIDAD']) > 0

# OtroConcepto - 49
# Código atributos
DescripcionConcepto="CONSOLIDADO INTCESANTIAS",ConceptoS=str(int(round(o.get_consolidated_provisions('intcesantias')))),ConceptoNS="0"
# Código validación
validation = o.get_consolidated_provisions('intcesantias') > 0

# OtroConcepto - 49
# Código atributos
DescripcionConcepto="CONSOLIDADO PRIMA",ConceptoS=str(int(round(o.get_consolidated_provisions('prima')))),ConceptoNS="0"
# Código validación
validation = o.get_consolidated_provisions('prima') > 0

# OtroConcepto - 49
# Código atributos
DescripcionConcepto="CONSOLIDADO VACACIONES",ConceptoS=str(int(round(o.get_consolidated_provisions('vacaciones')))),ConceptoNS="0"
# Código validación
validation = o.get_consolidated_provisions('vacaciones') > 0

# OtroConcepto - 49
# Código atributos
DescripcionConcepto="CONSOLIDADO CESANTIAS",ConceptoS=str(int(round(o.get_consolidated_provisions('cesantias')))),ConceptoNS="0"
# Código validación
validation = o.get_consolidated_provisions('cesantias') > 0

# Salud - 63
# Código atributos
Porcentaje=str(o.get_annual_parameters().value_porc_health_employee),Deduccion=str(o.get_value_salary_rules(['SSOCIAL001']) if o.get_value_salary_rules(['SSOCIAL001']) > 0 else 0.0)

# FondoPension - 64
# Código atributos
Porcentaje=str(o.get_annual_parameters().value_porc_pension_employee),Deduccion=str(o.get_value_salary_rules(['SSOCIAL002']) if o.get_value_salary_rules(['SSOCIAL002'])  > 0 else 0.0)

# FondoSP - 65
# Código atributos
Porcentaje=str(1 if o.get_porc_fsp() == 0 and o.get_value_salary_rules(['SSOCIAL003','SSOCIAL004']) > 0 else o.get_porc_fsp()),DeduccionSP=str(o.get_value_salary_rules(['SSOCIAL003','SSOCIAL004'])),PorcentajeSub="0.00",DeduccionSub="0.00"
# Código validación
validation = o.get_value_salary_rules(['SSOCIAL003','SSOCIAL004']) > 0

# Sindicato - 67
# Código atributos
Porcentaje="1.00",Deduccion=str(o.get_value_salary_rules(['CUOTA001','CUOTAS004']))
# Código validación
validation = o.get_value_salary_rules(['CUOTA001','CUOTAS004']) > 0

# Libranza - 71
# Código atributos
Descripcion="Libranza "+o.employee_id.name,Deduccion=str(o.get_value_salary_rules(['LIBRANZA001','AJ_DEV_LIBRANZA']))
# Código validación
validation = o.get_value_salary_rules(['LIBRANZA001','AJ_DEV_LIBRANZA']) > 0

---------------------------XML nómina electrónica de ajuste--------------------------

# NominaIndividualDeAjuste - 1
# Código atributos
nsmap={None:"dian:gov:co:facturaelectronica:NominaIndividualDeAjuste","xs":"http://www.w3.org/2001/XMLSchema-instance","ds":"http://www.w3.org/2000/09/xmldsig#","ext":"urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2","xades":"http://uri.etsi.org/01903/v1.3.2#","xades141":"http://uri.etsi.org/01903/v1.4.1#","xsi":"http://www.w3.org/2001/XMLSchema-instance"},SchemaLocation=""

# ReemplazandoPredecesor - 5
# Código atributos
NumeroPred=str(o.electronic_adjust_payroll_detail_id.sequence),CUNEPred=str(o.electronic_adjust_payroll_detail_id.cune),FechaGenPred=str(o.electronic_adjust_payroll_id.electronic_payroll_id.create_date.date())

# Periodo - 6
# Código atributos
FechaIngreso=str(o.version_id.date_start),FechaLiquidacionInicio =o.get_dates_process(),FechaLiquidacionFin=o.get_dates_process(1),TiempoLaborado=str(abs(o.get_time_working())),FechaGen=o.get_date_now(),FechaRetiro=str(o.version_id.retirement_date) if o.version_id.retirement_date else ""
# Código validación
validation = True if o.version_id.retirement_date else False

# Periodo - 7
# Código atributos
FechaIngreso=str(o.version_id.date_start),FechaLiquidacionInicio =o.get_dates_process(),FechaLiquidacionFin=o.get_dates_process(1),TiempoLaborado=str(abs(o.get_time_working())),FechaGen=o.get_date_now()
# Código validación
validation = False if o.version_id.retirement_date else True

# NumeroSecuenciaXML - 8
# Código atributos
CodigoTrabajador=o.employee_id.identification_id,Prefijo=o.electronic_adjust_payroll_id.prefix_adjust,Consecutivo=str(o.item),Numero=o.electronic_adjust_payroll_id.prefix_adjust+str(o.item)

# LugarGeneracionXML - 9
# Código atributos
Pais=o.employee_id.partner_encab_id.country_id.code,DepartamentoEstado=o.employee_id.partner_encab_id.x_city.code[0:2],MunicipioCiudad=o.employee_id.partner_encab_id.x_city.code,Idioma="es"

# InformacionGeneral - 10
# Código atributos
Version="V1.0: Nota de Ajuste de Documento Soporte de Pago de Nómina Electrónica",Ambiente="1",TipoXML="103",FechaGen=o.get_date_now(),HoraGen=o.get_time_now(),PeriodoNomina="5",TipoMoneda="COP"

# Empleador - 11
# Código atributos
RazonSocial=o.employee_id.company_id.name,NIT=str(o.employee_id.company_id.partner_id.vat),DV=str(o.employee_id.company_id.partner_id.x_digit_verification),Pais=o.employee_id.company_id.partner_id.country_id.code,DepartamentoEstado=o.employee_id.company_id.partner_id.x_city.code[0:2],MunicipioCiudad=o.employee_id.company_id.partner_id.x_city.code,Direccion=o.employee_id.company_id.partner_id.street

# Trabajador - 12
# Código atributos
TipoTrabajador=o.employee_id.tipo_coti_id.code,SubTipoTrabajador="00",AltoRiesgoPension="false",TipoDocumento=o.employee_id.partner_encab_id.l10n_latam_identification_type_id.z_code_dian,NumeroDocumento=o.employee_id.partner_encab_id.vat,PrimerApellido=o.employee_id.partner_encab_id.x_first_lastname,SegundoApellido=o.employee_id.partner_encab_id.x_second_lastname if o.employee_id.partner_encab_id.x_second_lastname else " ",PrimerNombre=o.employee_id.partner_encab_id.x_first_name,OtrosNombres=o.employee_id.partner_encab_id.x_second_name if o.employee_id.partner_encab_id.x_second_name else " ",LugarTrabajoPais=o.employee_id.partner_encab_id.country_id.code,LugarTrabajoDepartamentoEstado=o.employee_id.partner_encab_id.x_city.code[0:2],LugarTrabajoMunicipioCiudad=o.employee_id.partner_encab_id.x_city.code,LugarTrabajoDireccion=o.employee_id.partner_encab_id.street if  o.employee_id.partner_encab_id.street else "",SalarioIntegral="true" if o.version_id.modality_salary=="integral" else "false",TipoContrato=o.get_type_version(),Sueldo=str(o.version_id.wage)

# Pago - 13
# Código atributos
Forma="1",Metodo="47",Banco=o.get_bank_information(r_bank=1),TipoCuenta=o.get_bank_information(r_type=1),NumeroCuenta=o.get_bank_information(r_account=1)

# Basico - 17
# Código atributos
DiasTrabajados= str(int(o.get_quantity_salary_rules_exclude_prima(['BASICTURNOS'])/8)) if int(o.get_quantity_salary_rules_exclude_prima(['BASICTURNOS'])) > 0 else str(o.get_days_lines_exclude_prima(['WORK100'])),SueldoTrabajado=str(o.get_value_salary_rules(['BASIC','BASIC002','BASIC003','BASICTURNOS']) if o.get_value_salary_rules(['BASIC','BASIC002','BASIC003','BASICTURNOS']) > 0 else 0.0)

# Transporte - 18
# Código atributos
AuxilioTransporte=str(o.get_value_salary_rules(['AUX000','AUX000TURNOS','AJ_DEV_AUX_TRANS','AJ_DED_AUX_TRANS','AUX001'])),ViaticoManuAlojNS=str(o.get_value_salary_rules(['AUX006','AJ_DED_AUX_MOVILIZ','AUX002']))
# Código validación
validation = o.get_value_salary_rules(['AUX000','AUX000TURNOS','AJ_DEV_AUX_TRANS','AJ_DED_AUX_TRANS','AUX001','AUX006','AJ_DED_AUX_MOVILIZ','AUX002']) > 0

# HED - 20
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(1).salary_rule.code])),Porcentaje=str(o.get_type_overtime(1).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(1).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(1).salary_rule.code]) > 0

# HEN - 22
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(2).salary_rule.code])),Porcentaje=str(o.get_type_overtime(2).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(2).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(2).salary_rule.code]) > 0

# HRN - 24
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(3).salary_rule.code])),Porcentaje=str(o.get_type_overtime(3).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(3).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(3).salary_rule.code]) > 0

# HEDDF - 26
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(4).salary_rule.code])),Porcentaje=str(o.get_type_overtime(4).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(4).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(4).salary_rule.code]) > 0

# HRDDF - 28
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(5).salary_rule.code])),Porcentaje=str(o.get_type_overtime(5).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(5).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(5).salary_rule.code]) > 0

# HENDF - 30
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(6).salary_rule.code])),Porcentaje=str(o.get_type_overtime(6).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(6).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(6).salary_rule.code]) > 0

# HRNDF - 32
# Código atributos
Cantidad=str(o.get_quantity_salary_rules([o.get_type_overtime(7).salary_rule.code])),Porcentaje=str(o.get_type_overtime(7).percentage),Pago=str(o.get_value_salary_rules([o.get_type_overtime(7).salary_rule.code]))
# Código validación
validation = o.get_value_salary_rules([o.get_type_overtime(7).salary_rule.code]) > 0

# VacacionesComunes - 34
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['VACDISFRUTADAS']))),Pago=str(o.get_value_salary_rules(['VACDISFRUTADAS']))
# Código validación
validation = o.get_value_salary_rules(['VACDISFRUTADAS']) > 0

# VacacionesCompensadas - 35
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['VACREMUNERADAS','VACCONTRATO','VACACIONES_PARCIAL_INTEGRAL']))) if int(o.get_quantity_salary_rules(['VACREMUNERADAS','VACCONTRATO','VACACIONES_PARCIAL_INTEGRAL'])) <= 99 else "99",Pago=str(o.get_value_salary_rules(['VACREMUNERADAS','VACCONTRATO','VACACIONES_PARCIAL_INTEGRAL']))
# Código validación
validation = o.get_value_salary_rules(['VACREMUNERADAS','VACCONTRATO','VACACIONES_PARCIAL_INTEGRAL']) > 0

# Primas - 36
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['PRIMA','PRIMA_PARCIAL_INTEGRAL']))),Pago=str(o.get_value_salary_rules(['PRIMA','AJ_DEV_PRIMA','PRIMA_PARCIAL_INTEGRAL']))
# Código validación
validation = o.get_value_salary_rules(['PRIMA','AJ_DEV_PRIMA','PRIMA_PARCIAL_INTEGRAL'])> 0

# Cesantias - 37
# Código atributos
Pago=str(o.get_value_salary_rules(['CESANTIAS','CESANTIAS_PARCIAL_INTEGRAL'])),Porcentaje="12.00",PagoIntereses=str(o.get_value_salary_rules(['INTCESANTIAS','INTCESANTIAS_PARCIAL_INTEGRAL']))
# Código validación
validation = o.get_value_salary_rules(['CESANTIAS','CESANTIAS_PARCIAL_INTEGRAL','INTCESANTIAS','INTCESANTIAS_PARCIAL_INTEGRAL']) > 0

# Incapacidad - 39
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['INCAPACIDAD001','INCAPACIDAD002','INCAPACIDAD003','INCAPACIDAD004','INCAPACIDAD007','INCAPACIDAD008']))),Tipo="1",Pago=str(o.get_value_salary_rules(['INCAPACIDAD001','INCAPACIDAD002','INCAPACIDAD003','INCAPACIDAD004','INCAPACIDAD007','INCAPACIDAD008']))
# Código validación
validation = o.get_value_salary_rules(['INCAPACIDAD001','INCAPACIDAD002','INCAPACIDAD003','INCAPACIDAD004','INCAPACIDAD007','INCAPACIDAD008']) > 0

# Incapacidad - 40
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['INCAPACIDAD005']))),Tipo="2",Pago=str(o.get_value_salary_rules(['INCAPACIDAD005']))
# Código validación
validation = o.get_value_salary_rules(['INCAPACIDAD005'])> 0

# Incapacidad - 41
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['INCAPACIDAD006']))),Tipo="3",Pago=str(o.get_value_salary_rules(['INCAPACIDAD006']))
# Código validación
validation = o.get_value_salary_rules(['INCAPACIDAD006']) > 0

# LicenciaMP - 43
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['LICENCIA002','LICENCIA003']))),Pago=str(o.get_value_salary_rules(['LICENCIA002','LICENCIA003']))
# Código validación
validation = o.get_value_salary_rules(['LICENCIA002','LICENCIA003']) > 0

# LicenciaR - 44
# Código atributos
Cantidad=str(int(o.get_quantity_salary_rules(['LICENCIA001','LICENCIA004','LICENCIA005','COMPENSATORIO']))),Pago=str(o.get_value_salary_rules(['LICENCIA001','LICENCIA004','LICENCIA005','LICENCIA007','COMPENSATORIO']))
# Código validación
validation = o.get_value_salary_rules(['LICENCIA001','LICENCIA004','LICENCIA005','LICENCIA007','COMPENSATORIO']) > 0

# LicenciaNR - 45
# Código atributos
Cantidad=str(int(o.get_days_lines_exclude_prima(['LICENCIA_NO_REMUNERADA','SANCION','SUSP_CONTRATO','INAS_INJU'])))
# Código validación
validation = o.get_days_lines_exclude_prima(['LICENCIA_NO_REMUNERADA','SANCION','SUSP_CONTRATO','INAS_INJU']) > 0

# Bonificacion - 47
# Código atributos
BonificacionS=str(o.get_value_salary_rules(['BONI001','BONI002','BONI003','AJ_DED_BONIFICACION'])),BonificacionNS=str(o.get_value_salary_rules(['AUX013']))
# Código validación
validation = o.get_value_salary_rules(['BONI001','BONI002','BONI003','AJ_DED_BONIFICACION','AUX013']) > 0

# Auxilio - 49
# Código atributos
AuxilioS="0",AuxilioNS=str(o.get_value_salary_rules(['AUX003','AUX005','AUX007','AUXLIOVAC001','AUXLIOVAC002','AUX008','AUX009','AJ_DEV_AUX_NOSAL']))
# Código validación
validation = o.get_value_salary_rules(['AUX003','AUX005','AUX007','AUXLIOVAC001','AUXLIOVAC002','AUX008','AUX009','AJ_DEV_AUX_NOSAL']) > 0

# OtroConcepto - 53
# Código atributos
DescripcionConcepto="CONSOLIDADO INTCESANTIAS",ConceptoS=str(o.get_consolidated_provisions('intcesantias')),ConceptoNS="0"
# Código validación
validation = o.get_consolidated_provisions('intcesantias') > 0

# OtroConcepto - 53
# Código atributos
DescripcionConcepto="OTROS DEVENGOS",ConceptoS=str(o.get_value_salary_rules(['AJ_DEV_BASICO','AJ_DEV_INCAPACIDAD','AJ_DEV_DOMINICAL','AJ_DEV_HORASEXTRA','VIATICOS_PRESTACIONALES', 'VIATICOS_NO_PRESTACIONALES', 'VIATICOS_TOTAL','IMPUESTO_ASUM'])),ConceptoNS="0"
# Código validación
validation = o.get_value_salary_rules(['AJ_DEV_BASICO','AJ_DEV_INCAPACIDAD','AJ_DEV_DOMINICAL','AJ_DEV_HORASEXTRA','VIATICOS_PRESTACIONALES', 'VIATICOS_NO_PRESTACIONALES', 'VIATICOS_TOTAL','IMPUESTO_ASUM']) > 0

# OtroConcepto - 53
# Código atributos
DescripcionConcepto="CONSOLIDADO CESANTIAS",ConceptoS=str(o.get_consolidated_provisions('cesantias')),ConceptoNS="0"
# Código validación
validation = o.get_consolidated_provisions('cesantias') > 0

# OtroConcepto - 53
# Código atributos
DescripcionConcepto="CONSOLIDADO VACACIONES",ConceptoS=str(o.get_consolidated_provisions('vacaciones')),ConceptoNS="0"
# Código validación
validation = o.get_consolidated_provisions('vacaciones') > 0

# OtroConcepto - 53
# Código atributos
DescripcionConcepto="CONSOLIDADO PRIMA",ConceptoS=str(o.get_consolidated_provisions('prima')),ConceptoNS="0"
# Código validación
validation = o.get_consolidated_provisions('prima') > 0

# Salud - 68
# Código atributos
Porcentaje=str(o.get_annual_parameters().value_porc_health_employee),Deduccion=str(o.get_value_salary_rules(['SSOCIAL001']) if o.get_value_salary_rules(['SSOCIAL001']) > 0 else 0.0)

# FondoPension - 69
# Código atributos
Porcentaje=str(o.get_annual_parameters().value_porc_pension_employee),Deduccion=str(o.get_value_salary_rules(['SSOCIAL002']) if o.get_value_salary_rules(['SSOCIAL002'])  > 0 else 0.0)

# FondoSP - 70
# Código atributos
Porcentaje=str(o.get_porc_fsp()),DeduccionSP=str(o.get_value_salary_rules(['SSOCIAL003','SSOCIAL004'])),PorcentajeSub="0.00",DeduccionSub="0.00"
# Código validación
validation = o.get_value_salary_rules(['SSOCIAL003','SSOCIAL004']) > 0

# Sindicato - 72
# Código atributos
Porcentaje="1.00",Deduccion=str(o.get_value_salary_rules(['CUOTA001','CUOTAS004']))
# Código validación
validation = o.get_value_salary_rules(['CUOTA001','CUOTAS004']) > 0

# Libranza - 76
# Código atributos
Descripcion="Libranza "+o.employee_id.name,Deduccion=str(o.get_value_salary_rules(['LIBRANZA001','AJ_DEV_LIBRANZA']))
# Código validación
validation = o.get_value_salary_rules(['LIBRANZA001','AJ_DEV_LIBRANZA']) > 0
