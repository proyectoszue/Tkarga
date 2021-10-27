from odoo import models, fields, api, _ 
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class mntc_io(models.Model):
    _name = 'mntc.io'
    _rec_name = 'number'
    _description = 'Entrada/Salida'

    odometer                = fields.Integer('Odometer')
    number                  = fields.Char('Number', copy=False, index=True)
    scheduled_incoming_date = fields.Datetime('Scheduled incoming date')
    scheduled_outgoing_date = fields.Datetime('Scheduled outgoing date')
    incoming_date           = fields.Datetime('Incoming date')
    outgoing_date           = fields.Datetime('Outgoing date')
    garage_id               = fields.Many2one('mntc.garage', 'Taller',required=True)
    vehicle_id              = fields.Many2one('fleet.vehicle', 'Vehicle',required=True)
    movil_nro               = fields.Char(string='Movil', required=True)
    location_type           = fields.Selection([('location_1', 'Taller'), ('location_2', 'Otro taller'),('location_3', 'En camino')],'Location', default='location_3',required=True, domain="[('garage_id','=',garage_id)]")
    estimated_time = fields.Float(string='Estimated time',compute='_hours_get_estimated_time', store=True)
    real_time = fields.Float(string='Real time',compute='_hours_get_real_time', store=True) 
    counter_request = fields.Integer(compute='compute_counter_request', string='No. of Request')
    counter_workorder = fields.Integer(compute='compute_counter_workorder', string='No. of Workorders')
    mntc_request_ids = fields.One2many('mntc.request', 'mntc_io_id', string='Request ids')
    state = fields.Selection([('programmed', 'Programmed'), ('in', 'In'), ('out', 'Out'), ('canceled', 'Canceled')], 'State', default='in')
    workorder_ids = fields.Many2many('mntc.workorder','mntc_io_x_mntc_workorder', 'io_id','workorder_id', 'workorder_id')
    requester_id  = fields.Many2one('hr.employee', 'Requester')
    work_phone = fields.Char('Work phone')
    company_id = fields.Many2one('res.company', compute='get_company', string='Company')
    service_type_id = fields.Many2one('mntc.services.type',related="vehicle_id.service_type_id",string='Service',store=True)
    branch_id = fields.Many2one(related='garage_id.branch_id', store=True)
    vehiculo_marca = fields.Many2one(related='vehicle_id.vehiculo_marca', store=True)
    
    def unlink(self):
        disponibilidad_pool = self.env['vehiculo.trazabilidad.disponibilidad'].search([('io_id','=',self.id)])
        #vehicle_id = self.env['fleet.vehicle'].search([('id', '=',self.vehicle_id.id)])

        self.vehicle_id.disponibilidad = 'operacion'
        self.vehicle_id.state_id = 1

        disponibilidad_pool.unlink()        
        
        return super(mntc_io, self).unlink()

    @api.model
    def create(self, vals):
        date = None
        create_disp = 0
        if vals['state'] == 'in':
            if not vals['incoming_date']:
                date = datetime.now()-timedelta(hours=6)
                vals['incoming_date'] = date

            vehicle_id = self.env['fleet.vehicle'].search([('id', '=',vals['vehicle_id'])])
            count_in = 0
            in_pool = self.env['mntc.io'].search([('vehicle_id','=', vehicle_id.id)])
            for io_in in in_pool:
                if io_in.state == 'in':
                    count_in += 1
                if io_in.state == 'programmed':      

                    io_scheduled_incoming_date = io_in.scheduled_incoming_date                     
                    datetime_io_scheduled_incoming_date = io_scheduled_incoming_date
                    date_io_scheduled_incoming_date = datetime_io_scheduled_incoming_date.date()

                    str_incoming_date = vals['incoming_date']
                    datetime_incoming_date = str_incoming_date
                    date_incoming_date = datetime_incoming_date.date()

                    if date_io_scheduled_incoming_date == date_incoming_date:
                        raise ValidationError(_('Already input created \ Vehicle already have a programmed input, You must use that input.'))

            if count_in >=1:
                raise ValidationError(_("In maintenance \ Vehicle already is in maintenance, You can't make another input to this vehicle."))

            vehicle_id.disponibilidad = 'mantenimiento'
            vehicle_id.state_id = 2

            garage_object = self.env['mntc.garage'].search([('id', '=', vals['garage_id'])])
            sequence_code='mntc_EM-'+garage_object.code
            seq = self.env['ir.sequence'].next_by_code(sequence_code) or '-'
            
            vals['number'] = seq

            create_disp = 1
        else:
            garage_object = self.env['mntc.garage'].search([('id', '=', vals['garage_id'])])
            sequence_code='mntc_EM-'+garage_object.code
            seq = self.env['ir.sequence'].next_by_code(sequence_code) or '-'
            
            vals['number'] = seq

        ret = super(mntc_io, self).create(vals)

        if create_disp == 1:
            disponibilidad_pool = self.env['vehiculo.trazabilidad.disponibilidad']
            disponibilidad_vals = {
                'vehiculo': vehicle_id.id,
                'disponibilidad': 'mantenimiento',
                'razon': 'Entrada {}'.format(vals['number']),
                'io_id': ret.id
            }
            disponibilidad_pool.create(disponibilidad_vals)

        odometro_val = 0
        if ret.state == 'in':
            if type(vals['incoming_date']) == datetime:
                date = vals['incoming_date']
            else:
                date = datetime.strptime(vals['incoming_date'], '%Y-%m-%d %H:%M:%S') 

            ret.vehicle_id.get_odometer(date)
            odometro_val = int(float(ret.vehicle_id.last_odometer_ws))
            ret.write({'odometer': odometro_val})

            for workorder in ret.workorder_ids:
                workorder.write({'odometer': odometro_val})

        return ret

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} - Móvil {}".format(record.number,record.movil_nro)))
        return result

    def get_company(self):
        self.company_id = self.env.user.company_id
        return True

    # def write(self, vals):
    #     for record in self:
    #         user_in_plan = self.env.user.has_group('big_fleet_maintenance.big_fleet_maintenance_plan_group')
    #         user_in_receive = self.env.user.has_group('big_fleet_maintenance.big_fleet_maintenance_receive_vehicles_group')
    #         if user_in_plan:
    #             if record.state != 'programmed' and not user_in_receive:
    #                 raise  ValidationError(_("You are not authorized to update this record in this state."))
    #     return super(mntc_io, self).write(vals)

    def return_action_to_open(self):
        res = {
            'name': 'Solicitud',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mntc.request',
            'target': 'current',
            'domain': "[('mntc_io_id','in',[" + str(self._ids[0]) + "])]"
        }
        return res
    
    def return_action_to_open_workorder(self):
        res = {
            'name': 'Órden de Trabajo',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mntc.workorder',
            'target': 'current',
            'domain': "[('io_ids','in',[" + str(self._ids[0]) + "])]"
        }
        return res

    def compute_counter_request(self):
        for request in self:
            count = self.env['mntc.request'].search_count([('mntc_io_id', '=', request.id)])
            request.counter_request = count

    def compute_counter_workorder(self):
        for workorder in self:
            self._cr.execute("SELECT COUNT(*) FROM mntc_io_x_mntc_workorder WHERE io_id = %s" % workorder.ids[0])
            count = self._cr.fetchone()[0]

            workorder.counter_workorder = count
    
    def mntc_io_canceled(self):
        self.state = 'canceled'

    @api.onchange('movil_nro')
    def mntc_movil_nro_onchange(self):
        if self.movil_nro:
            vehicle_id = self.env['fleet.vehicle'].search([('movil_nro', '=', self.movil_nro)])
            if vehicle_id:
                self.vehicle_id = vehicle_id
            else :
                self.movil_nro = False
                self.vehicle_id = False
                raise ValidationError(_('Error! El móvil no tiene asociado un vehículo'))

    @api.onchange('vehicle_id')
    def mntc_vehicle_id_onchange(self):

        if self.vehicle_id:
            self.movil_nro = self.vehicle_id.movil_nro

    @api.onchange('incoming_date')
    def mntc_incoming_date_onchange(self):
        if self.incoming_date:
            if self.incoming_date > datetime.now():
                self.incoming_date = None
                raise ValidationError(_('Error! La fecha de entrada no puede ser mayor a la fecha actual'))

    @api.onchange('requester_id')
    def mntc_requester_id_onchange(self):
        if self.requester_id and self.requester_id.work_phone:            
            self.work_phone = self.requester_id.work_phone
        else:
            if self.requester_id.mobile_phone:
                self.work_phone = self.requester_id.mobile_phone
            else:
                self.work_phone = ''
    
    @api.depends('outgoing_date', 'incoming_date')
    def _hours_get_real_time(self):
        for mntc_io in self:
            if mntc_io.incoming_date and mntc_io.outgoing_date:
                result = mntc_io.outgoing_date - mntc_io.incoming_date
                seconds = result.total_seconds()
                final = seconds/3600
                mntc_io.real_time = final
            else:
                mntc_io.real_time = 0

    
    @api.depends('scheduled_incoming_date', 'scheduled_outgoing_date')
    def _hours_get_estimated_time(self):
        for mntc_io in self:
            if mntc_io.scheduled_incoming_date and mntc_io.scheduled_outgoing_date:
                result = mntc_io.scheduled_outgoing_date - mntc_io.scheduled_incoming_date
                seconds = result.total_seconds()
                final = seconds/3600
                mntc_io.estimated_time = final
            else:
                mntc_io.estimated_time = 0

    
    
    def new_request(self):
        request_pool = self.env['mntc.request']
       
        vals = {}
        vals = {
            'vehicle_id':self.vehicle_id.id,
            'movil_nro': self.movil_nro,
            'garage_id': self.garage_id.id,
            'state': 'draft',
            'mntc_io_id': self.id,
            'request_date': self.incoming_date,
            'requester_id': self.requester_id.id
        }
        request_pool.create(vals)

    def output(self):
        count = 0
        workorder_ended = 0
        
        for workorder in self.workorder_ids:
            count += 1
            #if workorder.state in ['programmed','stopped','ended', 'canceled', 'waiting_parts']:
            if workorder.state in ['stopped','ended', 'canceled','programmed']: 
                workorder_ended += 1      

        if count == workorder_ended:
            self.outgoing_date = datetime.utcnow()
            self.state = 'out'        
        else:
            raise ValidationError(_("Error!. Se debe finalizar, detener o cancelar las órdenes de trabajo asociadas a esta entrada."))

        if not self.vehicle_id.disponibilidad in 'operacion':
            self.vehicle_id.disponibilidad = 'operacion'
            self.vehicle_id.state_id = 1
            disponibilidad_pool = self.env['vehiculo.trazabilidad.disponibilidad']
            disponibilidad_vals = {
                'vehiculo': self.vehicle_id.id,
                'disponibilidad': 'operacion',
                'razon': 'Salida {}'.format(self.number)
            }
            disponibilidad_pool.create(disponibilidad_vals)
        
        self.vehicle_id.get_odometer()
        self.write({'odometer': int(float(self.vehicle_id.last_odometer_ws))})
        
    
    def vehicle_income(self):
        error, tmp_entrada = '', ''
        count_in = 0

        in_pool = self.env['mntc.io'].search([('vehicle_id','=',self.vehicle_id.id)])
        for io_in in in_pool:
            if io_in.state == 'in':
                tmp_entrada += "'" + str(io_in.number) + "'"
                count_in += 1
                
        if count_in >= 1:
            error += "Error!. Ya existe una entrada en ingreso para el vehículo.\n" + tmp_entrada 
            raise ValidationError(_(error))

            # return {
            #         'name': 'Deseas continuar?',
            #         'type': 'ir.actions.act_window',
            #         'res_model': 'confirm.wizard',
            #         'view_mode': 'form',
            #         'target': 'new',
            #         'context': {'default_yes_no': yes_no,
            #                     'default_io_id': self.id}
            #         }


        # if count_in >=1:
        #     raise ValidationError(_("En mantenimiento \ El vehículo se encuentra en mantenimiento, No es posible hacer otro ingreso."))

        if count_in == 0:
            self.state = 'in'
        
            self.incoming_date = datetime.utcnow()
            self.vehicle_id.disponibilidad = 'mantenimiento'
            self.vehicle_id.state_id = 2

            disponibilidad_pool = self.env['vehiculo.trazabilidad.disponibilidad']
            disponibilidad_vals = {
                'vehiculo': self.vehicle_id.id,
                'disponibilidad': 'mantenimiento',
                'razon': 'Entrada {}'.format(self.number)
            }
            disponibilidad_pool.create(disponibilidad_vals)

            if type(self.incoming_date) == datetime:
                    date = self.incoming_date
            else:
                date = datetime.strptime(self.incoming_date, '%d/%m/%y %H:%M:%S')

            self.vehicle_id.get_odometer(date)
            self.write({'odometer': int(float(self.vehicle_id.last_odometer_ws))})

            for wo in self.workorder_ids:
                wo.write({'odometer': int(float(self.vehicle_id.last_odometer_ws))})

    def check_odometer(self):
        self.vehicle_id.get_odometer()
        self.write({'odometer': int(float(self.vehicle_id.last_odometer_ws))})

        return True
        # ws_odometer=garage_object.ws_check_odometer(self.vehicle_id.placa_nro)
        # self.odometer  = ws_odometer
       
    @api.model
    def _get_default_id(self):return self.env.ref('zue_fleet_maintenance.mntc_documents_types_input_output')


class mntc_request(models.Model):
    _name = 'mntc.request'
    _rec_name = 'number'
    _description = 'Solicitudes'


    name = fields.Char(string="Name")
    number        = fields.Char(string="Number Request", readonly=True, copy=False, index=True)
    request_date  = fields.Datetime('Request Date',readonly=True,default=lambda *a: datetime.utcnow())
    vehicle_id    = fields.Many2one('fleet.vehicle','Vehicle',required=True)
    requester_id  = fields.Many2one('hr.employee', 'Requester',required=True)
    classification1 = fields.Many2one('mntc.workorder.classification', 'Clasificación')
    classification= fields.Selection( [('classification_1', 'vehicle stranded in the field'), ('classification_2', 'Corrective work not scheduled'),
                                        ('classification_4', 'Scheduled preventive work')], 'Classification', default='classification_4',required=True)
    priority_id = fields.Selection( [('priority_1', 'Emergency'), ('priority_2', 'Urgent'),('priority_3', 'Programmed')],'Priority')
    type_mntc = fields.Selection([('type_mntc_2', 'Correctivo'),('type_mntc_4', 'Mejorativo')], 'Type of maintenance', default='type_mntc_2')#, ('type_mntc_3', 'Predictive')('type_mntc_1', 'Preventive'), 
    #branch_id = fields.Many2one('zue.res.branch', 'Sucursal',readonly=True)
    delivery_date = fields.Datetime('Delivery Date', readonly=True)
    field_work = fields.Boolean(string='Field work')
    minor_work = fields.Boolean(string='Minor work')
    symptom_ids = fields.Many2one('mntc.symptoms', string="Symptom",domain="[('system_ids','in',[system_id])]")
    detection_method = fields.Many2one('mntc.detection.methods', string="Detection Methods")
    approved_tech_id = fields.Many2one('mntc.technician', 'Approved by', readonly=True)
    approved_date = fields.Datetime('Approved Date' , readonly=True)
    state = fields.Selection( [('draft', 'Draft'), ('approved', 'Approved'), ('ended', 'Ended'),('canceled', 'Canceled')], 'State', default='draft')
    description = fields.Text('Description')
    counter_request = fields.Integer(compute='compute_counter_request', string='of Workorders')
    movil_nro = fields.Char(related='vehicle_id.movil_nro', string='Movil')
    garage_id = fields.Many2one('mntc.garage', 'Garage',required=True)
    scheduled_delivery_date = fields.Datetime('Scheduled Delivery Date', readonly=True)
    mntc_io_id = fields.Many2one('mntc.io', string='Input/Output')
    system_id = fields.Many2one('mntc.vehicle.system', string='System id')
    service_type_id = fields.Many2one('mntc.services.type',related="vehicle_id.service_type_id",string='Service',readonly=True)
    branch_id = fields.Many2one(related='garage_id.branch_id')
    cancel_osbservation = fields.Text('Observación')
    #programmed_date  = fields.Datetime('Fecha programada')  
     
    @api.model
    def create(self, vals):      
        garage_object = self.env['mntc.garage'].search([('id', '=', vals['garage_id'])])
        sequence_code = 'mntc_SO-' + garage_object.code
        sequence_object = self.env['ir.sequence'].search([('code', '=', sequence_code)])

        last_write_date = sequence_object.write_date
        date = last_write_date
        last_year = date.year
        last_month = date.month
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().month

        if last_year == current_year:
            if int(last_month) < int(current_month):
                sequence_object.write({'number_next': 1})
            elif int(last_year) < int(current_year):
                sequence_object.write({'number_next': 1})

        seq = self.env['ir.sequence'].next_by_code(sequence_code) or '/'
        vals['number'] = seq
        
        obj_request = super(mntc_request, self).create(vals)
        
        return obj_request
        
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} | {}".format(record.number, record.name)))
        return result

    @api.onchange('mntc_io_id')
    def mntc_io_id_onchange(self):
        if not self.mntc_io_id:
            self.vehicle_id = False
            self.movil_nro = False
            self.garage_id = False
            self.requester_id = False   
        else:
            self.vehicle_id = self.mntc_io_id.vehicle_id
            self.movil_nro = self.mntc_io_id.movil_nro
            self.garage_id = self.mntc_io_id.garage_id
            self.requester_id = self.mntc_io_id.requester_id

    @api.onchange('system_id')
    def system_id_onchange(self):
        self.symptom_ids = False

    @api.onchange('priority_id')
    def mntc_priority_onchange(self):
        self.minor_work = False
        self.field_work = False

    def return_action_to_open(self):
        res = {
            'name': 'Órden de Trabajo',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mntc.workorder',
            'target': 'current',
            'domain': "[('request_id','in',[" + str(self._ids[0]) + "])]"
        }
        return res

    def compute_counter_request(self):
        count = self.env['mntc.workorder'].search_count([('request_id', '=', self.id)])
        self.counter_request = count

    @api.onchange('garage_id')
    def mntc_garage_onchange(self):
        if self.garage_id:
            self.branch_id = self.garage_id.branch_id

    @api.onchange('movil_nro')
    def mntc_movil_nro_onchange(self):
        if  self.movil_nro:
            vehicle_id = self.env['fleet.vehicle'].search([('movil_nro', '=', self.movil_nro)])
            if vehicle_id:
                self.vehicle_id = vehicle_id
            else:
                self.vehicle_id = False
                raise ValidationError(_("Error in movil \ ¡The vehicle does not have an associated fleet number"))

    @api.onchange('vehicle_id')
    def mntc_vehicle_id_onchange(self):
        if self.vehicle_id:
            self.movil_nro = self.vehicle_id.movil_nro
        
        obj_solicitud = self.env['mntc.request'].search(['&', ('vehicle_id', '=', self.vehicle_id.id), ('state', '=', 'draft')], limit=1)
        if obj_solicitud:
            yes_no = "La solicitud '" + obj_solicitud.name + " 'asociada al mismo vehículo se encuentra abierta."

            return {
            'warning': {
                'title': 'Advertencia!',
                'message': yes_no,
            }}

    def mntc_aproved(self):
        if not self.detection_method or not self.system_id or not self.symptom_ids:
            raise ValidationError(_("Error! Debe especificar los campos del prediagnóstico"))

        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id
        if not employee_id:
            raise ValidationError(_("Error en la configuración \\ Requiere ser un empleado para aprobar la operación"))

        technician_id =  self.env['mntc.technician'].search([('employee_id', '=', employee_id)], limit=1).id
        if not technician_id:
            raise ValidationError(_("Error en la configuración \\ Requiere ser un técnico para aprobar la operación"))


        approved_date = datetime.utcnow()

        if not self.name:
            raise ValidationError(_("Name is missing \ The field name is required"))
    
        
        if self.priority_id == 'priority_1' or self.priority_id == 'priority_2':
            if not self.mntc_io_id:
                raise ValidationError(_("Error! Debe especificar la entrada/salida para la prioridad seleccionada"))

            workorder_state = 'in_progress'
            tmp_in_charge = 'coordinating'
        else:
            workorder_state = 'planeacion'
            tmp_in_charge = 'planning'
            
        self.env['mntc.workorder'].create({
                    'request_id': self.id,
                    'state': workorder_state,
                    'origin_state': workorder_state,
                    'garage_id': self.garage_id.id,
                    'priority': self.priority_id,
                    'number': None,
                    'vehicle_id': self.vehicle_id.id,
                    'priority': self.priority_id,
                    'type_mntc': self.type_mntc,
                    'movil_nro': self.movil_nro,
                    'approved_date': datetime.utcnow(),
                    'approved_tech_id': technician_id,
                    'in_charge': tmp_in_charge,
                    'io_ids': self.mntc_io_id.ids,
                    'created_by': self.env.user.id
                })  
    
        # order_pool.create(vals)
        if employee_id:
            if technician_id:
                return self.write({"approved_tech_id": technician_id, "approved_date": approved_date,"state": "approved"})
            else:
                raise ValidationError(_("Error in configured \ Requires being a technician to approve the operation"))
        else:
            raise ValidationError(_("Error in configured \ You must be  registered as an employee"))
    
    def mntc_canceled(self): 
        workorders_related = self.env['mntc.workorder'].search([('request_id', '=', self.id)])
        for workorder in workorders_related:
            if not workorder.state in ['canceled']:
                raise ValidationError(_("Work Orders \ There are work orders not canceled")) 

        if not self.cancel_osbservation:
            raise ValidationError(_("Error! Debe especificar una observación para cancelar la solicitud.")) 

        
        # if self.description or self.state in ['approved','inprogress']:
        self.write({"state": "canceled"}) 
        return True
        # else:
        #     raise ValidationError(_("Error in configured \ Requires description to canceled"))
    

class mntc_workorder_classification(models.Model):
    _name = 'mntc.workorder.classification'
    _description = 'Clasificación de orden de trabajo'
    
    name = fields.Char('Nombre')