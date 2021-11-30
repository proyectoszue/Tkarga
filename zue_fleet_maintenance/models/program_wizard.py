from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class program_wizard(models.TransientModel):
    _name = 'program.wizard'
    _description = 'Planeación preventiva de los vehículos'

   
    programming_range =  fields.Selection([('week', 'A una semana'), ('monthly', 'A un mes'), ('three_months', 'A tres meses'),('year','A un año'),('non_scheduled', 'No programada'),('instant', 'Instante')], 'Rango a programar', default='week', required=True)
    service_type_id = fields.Many2one('mntc.services.type', string='Servicio')
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Marca de vehículo')
    vehiculo_linea_id = fields.Many2one('vehiculos.lineas', string='Linea de vehículo')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehículo')
    movil_nro = fields.Char('Movil', readonly=True)
    branch_id    = fields.Many2one('zue.res.branch', 'Sucursal', required=True)
    garage_id = fields.Many2one('mntc.garage', string='Taller')
    days_last_revision = fields.Char(string='Última revisión (en días)')
    observation = fields.Text(string='Observación')
    start_programmed_date = fields.Datetime(string='Fecha inicio programada',required=True,default=datetime.utcnow())
    location_id = fields.Many2one('mntc.location', string='Ubicación')
    routines_id = fields.Many2one('mntc.routines', string='Rutinas')
    workorder_state  = fields.Char('Estado Orden de trabajo', readonly=True)
    workorder_id = fields.Many2one('mntc.workorder', string='Orden de trabajo')
    vehicle_state = fields.Char(string='Estado del vehículo')
    end_date_execution_wo  = fields.Datetime(string='Fecha fin ejecución OT')
    odometer_vehicle = fields.Integer('Odómetro')
    odometer_last_execute = fields.Integer('Odómetro última ejecución')
    trigger_type = fields.Selection([('frecuency', "Frecuencia"), ('odometer', "Odómetro")], string="Tipo de disparador")
    trigger_qty = fields.Float(string='Cantidad')
    daily_average = fields.Integer('Promedio diario')

    def load_list(self,programming_range,garage_id,service_type_id,fleet_id):
        if fleet_id:
            vehicle_pool = self.env['fleet.vehicle'].search([('id','=',fleet_id.id),('branch_id','=',garage_id.branch_id.id)]) 
        else:
            if service_type_id:
                vehicle_pool = self.env['fleet.vehicle'].search([('branch_id','=',garage_id.branch_id.id),('model_id','!=',False),('service_type_id','=',service_type_id.id),('vehiculo_linea','!=',False)]) 
            else:
                vehicle_pool = self.env['fleet.vehicle'].search([('branch_id','=',garage_id.branch_id.id),('model_id','!=',False),('service_type_id','!=',False),('vehiculo_linea','!=',False)]) 
        
        date_now = datetime.now()
        domain = {}

        if programming_range == 'week':
            date = date_now + timedelta(days=7)
            number_days = 7
        elif programming_range == 'monthly':
            date = date_now + timedelta(days=30)
            number_days = 30
        elif programming_range == 'three_months':
            date = date_now + timedelta(days=90)
            number_days = 90
        elif programming_range == 'year':
            date = date_now + timedelta(days=365) 
            number_days = 365  
        elif programming_range == 'instant':
            date = date_now + timedelta(days=365) 
            number_days =  1

        date_now = datetime.date(date_now)
        date = datetime.date(date)

        if vehicle_pool:
            for vehicle in vehicle_pool:
                odometer_counter = 0    
                domain =[   ('brand_id', '=',vehicle.model_id.brand_id.id),
                            ('service_type_id', '=',vehicle.service_type_id.id),
                            ('vehiculo_linea_id', '=',vehicle.vehiculo_linea.id)] 
                catalog_pool = self.env['mntc.catalog'].search(domain)  
                daily_average=vehicle.daily_average
                if catalog_pool:
                    for routine in catalog_pool.routines_ids:
                        aux = False
                        odometer_counter = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', vehicle.id)],order='value desc',limit=1)
                        if routine.trigger_qty:
                            tmp_odometer_diff = 0
                            workorder_routines_obj = self.env['mntc.workorder.routines'].search([('routine_id', '=', routine.id), ('vehicle_id', '=', vehicle.id)], order='odometer desc', limit=1)
                            if workorder_routines_obj:
                                if odometer_counter.value == False or odometer_counter.date == False:
                                    raise ValidationError(_("Error! No hay registros del odómetro en el vehículo, agregue un odómetro inicial \n vehicle: %s \n movil: %s  \n "  % (vehicle.name, vehicle.movil_nro)))
                                
                                if routine.trigger_type=='odometer':
                                    tmp_odometer_diff = odometer_counter.value - workorder_routines_obj.odometer
                                    if tmp_odometer_diff <= routine.trigger_qty:
                                        if daily_average:
                                            odometer_last_execute = workorder_routines_obj.odometer
                                            if odometer_last_execute > odometer_counter.value:
                                                odometer_last_execute = odometer_counter.value
                                            if daily_average:
                                                days_next_revision = round(((odometer_last_execute + routine.trigger_qty) - odometer_counter.value) / daily_average)
                                    else:
                                        days_next_revision = 1
                                        odometer_last_execute = workorder_routines_obj.odometer

                                    tmp_last_odometer = 0
                                    if daily_average:
                                        if workorder_routines_obj.workorder_id.end_date:
                                            end_date_execution_wo = workorder_routines_obj.workorder_id.end_date
                                        elif workorder_routines_obj.workorder_id.end_programmed_date :
                                            end_date_execution_wo = workorder_routines_obj.workorder_id.end_programmed_date
                                        else:
                                            end_date_execution_wo= workorder_routines_obj.create_date

                                        end_date_execution_wo = datetime.date(end_date_execution_wo)
                                        days_last_revision = date_now - end_date_execution_wo
                                        days_last_revision = abs(days_last_revision.days)

                                        if not days_last_revision:
                                            days_last_revision= 1

                                        start_programmed_date=datetime.utcnow()
                                        created_wo = False

                                        start_programmed_date = datetime.date(start_programmed_date)
                                        while date > start_programmed_date:
                                            if aux:
                                                if daily_average > routine.trigger_qty:
                                                    start_programmed_date = aux + timedelta(1)
                                                else:
                                                    start_programmed_date = aux + timedelta(routine.trigger_qty/daily_average)
                                                end_date_execution_wo = aux
                                                odometer_last_execute = odometer_last_execute + routine.trigger_qty

                                                #start_programmed_date = datetime.date(start_programmed_date)

                                                days_last_revision = start_programmed_date - date_now
                                                days_last_revision = days_last_revision.days
                                            else:
                                                start_programmed_date = start_programmed_date + timedelta(days=days_next_revision)
                                                workorder_id = workorder_routines_obj.workorder_id.id
                                                workorder_state =workorder_routines_obj.workorder_id.state

                                            if start_programmed_date > date:
                                                break
                                            #odometer_range_min = odometer_last_execute - (routine.trigger_qty * 0.5)
                                            #odometer_range_max = odometer_last_execute + (routine.trigger_qty * 0.5)

                                            if not created_wo:
                                                workorder_routines_last_execute = self.env['mntc.workorder.routines'].search([('routine_id', '=', routine.id), ('vehicle_id', '=', vehicle.id)],order='odometer desc', limit=1)
                                            else:
                                                if tmp_last_odometer < vehicle.odometer:
                                                    start_programmed_date = datetime.date(datetime.utcnow()) + timedelta(days=1)
                                                workorder_routines_last_execute = created_wo

                                            if days_last_revision <= 1:
                                                programming_range = 'instant'
                                            elif  days_last_revision >= 1 and days_last_revision <= 7:
                                                programming_range  = 'week'
                                            elif days_last_revision >= 7 and days_last_revision <= 30:
                                                programming_range = 'monthly'
                                            elif  days_last_revision >= 30 and days_last_revision <= 90:
                                                programming_range = 'three_months'
                                            elif  days_last_revision >= 365:
                                                programming_range = 'year'

                                            if workorder_routines_last_execute:
                                                if created_wo:
                                                    workorder_id = False
                                                    workorder_state = 'Programmed'
                                                    days_last_revision = 'Programada'
                                                else:
                                                    workorder_id = workorder_routines_last_execute.workorder_id.id
                                                    workorder_state = workorder_routines_last_execute.workorder_id.state
                                                    days_last_revision = 'Programada'
                                            else :
                                                workorder_id = False
                                                workorder_state = False
                                                days_last_revision = 'No ejecutada'

                                            vals={
                                                'vehicle_id': vehicle.id,
                                                'movil_nro': vehicle.movil_nro,
                                                'vehicle_state': vehicle.disponibilidad,
                                                'garage_id': garage_id.id,
                                                'programming_range': programming_range,
                                                'service_type_id': vehicle.service_type_id.id,
                                                'brand_id': vehicle.model_id.brand_id.id,
                                                'branch_id': vehicle.branch_id.id,
                                                'vehiculo_linea_id': vehicle.vehiculo_linea.id,
                                                'routines_id': routine.id,
                                                'workorder_id': workorder_id,
                                                'start_programmed_date': start_programmed_date ,
                                                'days_last_revision':days_last_revision,
                                                'odometer_vehicle': odometer_counter.value,
                                                'odometer_last_execute': odometer_last_execute,
                                                'trigger_qty': routine.trigger_qty,
                                                'trigger_type': routine.trigger_type,
                                                'end_date_execution_wo': end_date_execution_wo,
                                                'daily_average': daily_average,
                                                'workorder_state': workorder_state,

                                            }
                                            aux=start_programmed_date

                                            created_wo = self.create(vals)
                                            tmp_last_odometer = odometer_last_execute + routine.trigger_qty
                                    else:
                                            vals={
                                                        'vehicle_id': vehicle.id,
                                                        'movil_nro': vehicle.movil_nro,
                                                        'vehicle_state': vehicle.disponibilidad,
                                                        'programming_range': 'non_scheduled',
                                                        'garage_id': garage_id.id,
                                                        'service_type_id': vehicle.service_type_id.id,
                                                        'brand_id': vehicle.model_id.brand_id.id,
                                                        'branch_id': vehicle.branch_id.id,
                                                        'vehiculo_linea_id': vehicle.vehiculo_linea.id,
                                                        'routines_id': routine.id,
                                                        'odometer_vehicle': odometer_counter.value,
                                                        'trigger_qty': routine.trigger_qty,
                                                        'trigger_type': routine.trigger_type,
                                                        'daily_average': daily_average,
                                                        'days_last_revision':'Error el campo Daily average del vehiculo por favor actualizar los odómetros'
                                                    }
                                            self.create(vals)
                                else:     
                                    if workorder_routines_obj.workorder_id.end_date:
                                        end_date_execution_wo = workorder_routines_obj.workorder_id.end_date  
                                    elif workorder_routines_obj.workorder_id.end_programmed_date :
                                        end_date_execution_wo = workorder_routines_obj.workorder_id.end_programmed_date
                                    else:
                                        end_date_execution_wo= workorder_routines_obj.create_date
                                    
                                    end_date_execution_wo = datetime.date(end_date_execution_wo)
                                    days_last_revision = date_now - end_date_execution_wo
                                    days_last_revision = abs(days_last_revision.days) 

                                    start_programmed_date=datetime.utcnow()

                                    if not days_last_revision:
                                        days_last_revision= 1
                                    if days_last_revision < number_days:
                                        odometer_last_execute =workorder_routines_obj.odometer
                                        if odometer_last_execute > odometer_counter.value:
                                            odometer_last_execute = odometer_counter.value
                                        start_programmed_date=datetime.utcnow() 
                                        
                                        start_programmed_date = datetime.date(start_programmed_date)
                                        while date > start_programmed_date:
                                            if aux:
                                                start_programmed_date =aux + timedelta(routine.trigger_qty)
                                                end_date_execution_wo = aux
                                                odometer_last_execute = odometer_last_execute + routine.trigger_qty * daily_average
                                                
                                                #start_programmed_date = datetime.date(start_programmed_date)
                                                days_last_revision = start_programmed_date - date_now
                                                days_last_revision = days_last_revision.days

                                            else :
                                                workorder_id= workorder_routines_obj.workorder_id.id
                                                workorder_state=workorder_routines_obj.workorder_id.state
                                                if  end_date_execution_wo: 
                                                    start_programmed_date = end_date_execution_wo + timedelta(routine.trigger_qty)
                                                else :
                                                    start_programmed_date = workorder_routines_obj.create_date + timedelta(routine.trigger_qty)

                                            if start_programmed_date > date:
                                                break
                                            
                                            if days_last_revision <= 1:
                                                programming_range = 'instant'
                                            elif  days_last_revision >= 1 and days_last_revision <= 7:
                                                programming_range  = 'week' 
                                            elif days_last_revision >= 7 and days_last_revision <= 30:
                                                programming_range = 'monthly'
                                            elif  days_last_revision >= 30 and days_last_revision <= 90:
                                                programming_range = 'three_months'
                                            elif  days_last_revision >= 365:
                                                programming_range = 'year'
                                            odometer_range_min= odometer_last_execute -  (odometer_last_execute * 0.5)
                                            odometer_range_max= odometer_last_execute +  (odometer_last_execute * 0.5)
                                            workorder_routines_last_execute = self.env['mntc.workorder.routines'].search(['&',('routine_id','=',routine.id),('vehicle_id','=',vehicle.id)], limit=1)

                                            if workorder_routines_last_execute:
                                                workorder_id= workorder_routines_last_execute.workorder_id.id
                                                workorder_state=workorder_routines_last_execute.workorder_id.state
                                            
                                                days_last_revision = 'Programada'
                                            else :
                                                workorder_id = False 
                                                workorder_state = False 
                                                days_last_revision = 'No ejecutada'

                                            vals={                       
                                                'vehicle_id': vehicle.id,
                                                'movil_nro': vehicle.movil_nro,
                                                'vehicle_state': vehicle.disponibilidad,
                                                'garage_id': garage_id.id,
                                                'programming_range': programming_range,
                                                'service_type_id': vehicle.service_type_id.id,
                                                'brand_id': vehicle.model_id.brand_id.id,
                                                'branch_id': vehicle.branch_id.id,
                                                'vehiculo_linea_id': vehicle.vehiculo_linea.id,
                                                'routines_id': routine.id,
                                                'workorder_id':workorder_id,
                                                'start_programmed_date':start_programmed_date,
                                                'days_last_revision':days_last_revision,
                                                'odometer_vehicle': odometer_counter.value,
                                                'odometer_last_execute': odometer_last_execute ,
                                                'trigger_qty': routine.trigger_qty,
                                                'trigger_type': routine.trigger_type,
                                                'end_date_execution_wo': end_date_execution_wo,
                                                'daily_average': daily_average,
                                                'workorder_state': workorder_state,
                                                
                                            }
                                            aux=start_programmed_date
                                            self.create(vals)
                            else:
                                if routine.trigger_qty:
                                    if not odometer_counter.value or not odometer_counter.date:
                                        continue
                                        # raise ValidationError(
                                        #     _("Error! No hay registros del odómetro en el vehículo, agregue un odómetro inicial \n vehicle: %s \n movil: %s  \n " % (
                                        #     vehicle.name, vehicle.movil_nro)))

                                    if routine.trigger_type == 'odometer':
                                        tmp_odometer_diff = odometer_counter.value - 0

                                        if daily_average:
                                            odometer_last_execute = odometer_counter.value
                                            if odometer_last_execute > odometer_counter.value:
                                                odometer_last_execute = odometer_counter.value
                                            if daily_average:
                                                days_next_revision = round(((odometer_last_execute + routine.trigger_qty) - odometer_counter.value) / daily_average)

                                            if days_next_revision < 0:
                                                days_next_revision = 1

                                            end_date_execution_wo = None
                                            days_last_revision = None

                                            if not days_last_revision:
                                                days_last_revision = 1
                                            if days_last_revision < number_days:
                                                start_programmed_date = datetime.utcnow()

                                                created_wo = False

                                                start_programmed_date = datetime.date(start_programmed_date)
                                                while date > start_programmed_date:
                                                    if aux:
                                                        if daily_average > routine.trigger_qty:
                                                            start_programmed_date = aux + timedelta(1)
                                                        else:
                                                            start_programmed_date = aux + timedelta(routine.trigger_qty / daily_average)

                                                        end_date_execution_wo = aux
                                                        odometer_last_execute = odometer_last_execute + routine.trigger_qty

                                                        # start_programmed_date = datetime.date(start_programmed_date)

                                                        days_last_revision = start_programmed_date - date_now
                                                        days_last_revision = days_last_revision.days
                                                    else:
                                                        if created_wo:
                                                            start_programmed_date = start_programmed_date + timedelta(days=days_next_revision)
                                                        else:
                                                            start_programmed_date = start_programmed_date + timedelta(days=1)
                                                        workorder_id = None
                                                        workorder_state = None

                                                    if start_programmed_date > date:
                                                        break
                                                    # odometer_range_min = odometer_last_execute - (routine.trigger_qty * 0.5)
                                                    # odometer_range_max = odometer_last_execute + (routine.trigger_qty * 0.5)

                                                    if not created_wo:
                                                        workorder_routines_last_execute = self.env['mntc.workorder.routines'].search([('routine_id', '=', routine.id), ('vehicle_id', '=', vehicle.id)], order='odometer desc', limit=1)
                                                    else:
                                                        workorder_routines_last_execute = created_wo

                                                    if days_last_revision <= 1:
                                                        programming_range = 'instant'
                                                    elif days_last_revision >= 1 and days_last_revision <= 7:
                                                        programming_range = 'week'
                                                    elif days_last_revision >= 7 and days_last_revision <= 30:
                                                        programming_range = 'monthly'
                                                    elif days_last_revision >= 30 and days_last_revision <= 90:
                                                        programming_range = 'three_months'
                                                    elif days_last_revision >= 365:
                                                        programming_range = 'year'

                                                    if workorder_routines_last_execute:
                                                        if created_wo:
                                                            workorder_id = False
                                                            workorder_state = 'Programmed'
                                                            days_last_revision = 'Programada'
                                                        else:
                                                            workorder_id = workorder_routines_last_execute.workorder_id.id
                                                            workorder_state = workorder_routines_last_execute.workorder_id.state
                                                            days_last_revision = 'Programada'
                                                    else:
                                                        workorder_id = False
                                                        workorder_state = False
                                                        days_last_revision = 'No ejecutada'

                                                    vals = {
                                                        'vehicle_id': vehicle.id,
                                                        'movil_nro': vehicle.movil_nro,
                                                        'vehicle_state': vehicle.disponibilidad,
                                                        'garage_id': garage_id.id,
                                                        'programming_range': programming_range,
                                                        'service_type_id': vehicle.service_type_id.id,
                                                        'brand_id': vehicle.model_id.brand_id.id,
                                                        'branch_id': vehicle.branch_id.id,
                                                        'vehiculo_linea_id': vehicle.vehiculo_linea.id,
                                                        'routines_id': routine.id,
                                                        'workorder_id': workorder_id,
                                                        'start_programmed_date': start_programmed_date,
                                                        'days_last_revision': days_last_revision,
                                                        'odometer_vehicle': odometer_counter.value,
                                                        'odometer_last_execute': odometer_last_execute,
                                                        'trigger_qty': routine.trigger_qty,
                                                        'trigger_type': routine.trigger_type,
                                                        'end_date_execution_wo': end_date_execution_wo,
                                                        'daily_average': daily_average,
                                                        'workorder_state': workorder_state,

                                                    }
                                                    aux = start_programmed_date
                                                    created_wo = self.create(vals)
                                        else:
                                            vals = {
                                                'vehicle_id': vehicle.id,
                                                'movil_nro': vehicle.movil_nro,
                                                'vehicle_state': vehicle.disponibilidad,
                                                'programming_range': 'non_scheduled',
                                                'garage_id': garage_id.id,
                                                'service_type_id': vehicle.service_type_id.id,
                                                'brand_id': vehicle.model_id.brand_id.id,
                                                'branch_id': vehicle.branch_id.id,
                                                'vehiculo_linea_id': vehicle.vehiculo_linea.id,
                                                'routines_id': routine.id,
                                                'odometer_vehicle': odometer_counter.value,
                                                'trigger_qty': routine.trigger_qty,
                                                'trigger_type': routine.trigger_type,
                                                'daily_average': daily_average,
                                                'days_last_revision': 'Error el campo Daily average del vehiculo por favor actualizar los odómetros'
                                            }
                                            self.create(vals)
                                    else:
                                        vals={
                                                    'vehicle_id': vehicle.id,
                                                    'movil_nro': vehicle.movil_nro,
                                                    'vehicle_state': vehicle.disponibilidad,
                                                    'programming_range': 'non_scheduled',
                                                    'garage_id': garage_id.id,
                                                    'service_type_id': vehicle.service_type_id.id,
                                                    'brand_id': vehicle.model_id.brand_id.id,
                                                    'branch_id': vehicle.branch_id.id,
                                                    'vehiculo_linea_id': vehicle.vehiculo_linea.id,
                                                    'routines_id': routine.id,
                                                    'odometer_vehicle': odometer_counter.value,
                                                    'trigger_qty': routine.trigger_qty,
                                                    'trigger_type': routine.trigger_type,
                                                    'daily_average': daily_average,
                                                    'days_last_revision':'No se han realizado mantenimientos de este tipo'
                                                }
                                        self.create(vals)
       

    def program_catalog(self):
        workorder_lst = []  
        for record in self:
            if not record.start_programmed_date:
                raise ValidationError(_("Error! No ha especificado una fecha de inicio programada."))

            technician_id = 0
            workorder_obj=self.env['mntc.workorder']

            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if not employee:
                raise ValidationError(_("Error! El usuario no se ha configurado como empleado."))

            obj_technician_id = self.env['mntc.technician'].search([('employee_id', '=', employee.id)],limit=1)

            if not obj_technician_id:
                raise ValidationError(_("Error! El empleado no se ha configurado como técnico."))
            else:
                technician_id =  obj_technician_id.id
            date =  datetime.utcnow() 
            observation = ''
            
            if employee:
                observation = 'programmer : '+ employee.name 
            
            workorder_routines_obj = self.env['mntc.workorder.routines']
            routine_ids=[]  
            routine_ids.append(record.routines_id.id)
            #odometer_counter = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.vehicle_id.id), ('source', '!=', 'gps')], order='date desc', limit=1)

            type_mntc = ''
            if record.trigger_type == 'frecuency':
                type_mntc = 'type_mntc_3'
            elif record.trigger_type == 'odometer':
                type_mntc = 'type_mntc_1'

            vals = {
                    'vehicle_id': record.vehicle_id.id,
                    'movil_nro': record.vehicle_id.movil_nro,
                    'state': 'planeacion',
                    'type_mntc': type_mntc,
                    'priority' : 'priority_3',
                    'in_charge': 'planning',
                    'observation' : observation,
                    'garage_id': record.garage_id.id,
                    'approved_date': date,
                    'location_id' : record.location_id.id,
                    'start_programmed_date':  record.start_programmed_date,
                    'approved_tech_id':technician_id,
                    'work_routine_ids':[(6,0,routine_ids)]
                    }
            workorder_id=workorder_obj.create(vals)

            # workorder_id.generate_tasks()
            # workorder_id.generate_program()

            workorder_id.mntc_work_routine_ids()
            workorder_id.start_programmed_date_change() 
            workorder_id.mntc_workorder_programmed()
            workorder_id.write({'end_programmed_date': workorder_id.start_programmed_date + timedelta(hours=workorder_id.estimated_time)})

            workorder_lst.append(workorder_id.id)

            # if odometer_counter:
            #     odometer_date = odometer_counter.date
            #     odometer_value = odometer_counter.value
            # else:
            #     odometer_date = record.start_programmed_date
            #     odometer_value = 0            

            # days = datetime.combine(odometer_date,datetime.min.time()) - record.start_programmed_date
            # days= abs(float(days.total_seconds()/86400))
            # odometer= days *  record.vehicle_id.daily_average
            # odometer_record=odometer_value + odometer
            # if  record.odometer_last_execute:
            #     odometer_record=record.odometer_last_execute

            # vals2 = {
            #             'workorder_id': workorder_id.id,
            #             'routine_id': record.routines_id.id,
            #             'vehicle_id': record.vehicle_id.id,
            #             'odometer' : odometer_record 
            #             }   
            # workorder_routines_obj.create(vals2)
        
                
        view_tree = self.env['ir.ui.view'].search([('name','=','mntc.workorder.tree.view')]).id
        view_form = self.env['ir.ui.view'].search([('name','=','mntc.workorder.form.view')]).id
        view_graph = self.env['ir.ui.view'].search([('name','=','mntc.workorder.graph')]).id
        window = {
                    'name': 'Órden de trabajo',
                    'view_mode': 'tree,form,graph',
                    'views': [[view_tree, 'tree'], [view_form, 'form'], [view_graph, 'graph']],
                    'res_model': 'mntc.workorder',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                     }

        if workorder_lst:
            workorder_str=','.join(map(str, workorder_lst))
            window['domain'] = "[('id','in',["+workorder_str+"])]"

        return window

    

class program_range_wizard(models.TransientModel):
    """
    This window auto-schedules the maintenance of the fleet module, 
    filters the vehicles by garage, catalog, line and brand, 
    programs the service orders in approved with their 
    tasks and schedules already assigned.
    """
    _name = 'program.range.wizard'
    _description = 'Wizard planeación preventiva'

    programming_range =  fields.Selection([('week', 'A una semana'), ('monthly', 'A un mes'), ('three_months', 'A tres meses'),('year','A un año')], 'Rango a programar', default='week', required=True)
    garage_id = fields.Many2one('mntc.garage', string='Taller', required=True)
    service_type_id = fields.Many2one('mntc.services.type', string='Servicio')
    fleet_id = fields.Many2one('fleet.vehicle', 'Vehículo')

    def open_program_wizard(self):
        program_wizard_pool = self.env['program.wizard'] 
        for program in program_wizard_pool.search([('create_uid','=',self.env.uid)]):
            program[0].unlink()

        program_wizard_pool.load_list(self.programming_range,self.garage_id,self.service_type_id,self.fleet_id)

        view_tree_id = self.env['ir.ui.view'].search([('name','=','program.wizard.tree')])
        view_form_id = self.env['ir.ui.view'].search([('name','=','program.wizard.form')])
       
        res = { 
                'name': 'Asistente rango de programación',
                'view_mode': 'tree',
                'views': [[view_tree_id.id, 'tree'],[view_form_id.id, 'form']],
                'res_model': 'program.wizard',      
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('create_uid','=',self.env.uid)],
        }
        return res