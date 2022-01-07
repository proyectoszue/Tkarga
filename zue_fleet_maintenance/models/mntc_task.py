from odoo import models, fields, api, _ 
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class mntc_tasks(models.Model):
    _name = 'mntc.tasks'
    _description = 'Tareas' 
    
    name = fields.Char(string='Name', store=True, required=True)
    workorder_id = fields.Many2one('mntc.workorder', string='Work order id')
    state_workorder = fields.Selection(related='workorder_id.state', string='Estado Orden de Trabajo', store=True)
    routine_id = fields.Many2one('mntc.routines', string='Routine id')
    activity_id = fields.Many2one('mntc.activity', string='Activity id')
    system_id = fields.Many2one('mntc.vehicle.system', string='System id', required=True)
    estimated_time = fields.Float(string='Estimated time', required=True, store=True)
    process_description = fields.Text(string='Decripción')
    spare_part_ids = fields.One2many('mntc.spare.part.x.task',inverse_name='task_id', string='Spare_parts_ids')
    technician_ids = fields.Many2many('mntc.technician', 'mntc_tasks_x_mntc_technician', 'task_id', 'technician_id', string='Technician_ids', domain=lambda self:self._get_technicians())
    spent_time = fields.Float(string='Spent time',compute='calculate_spent_time',store = True)
    state = fields.Selection([('started', "Abierto"), ('ended', "Finalizado"), ('canceled', "Cancelado")], string="State", default='started')#('draft', "Draft"),('programed', "Programed"), 
    start_programmed_date = fields.Datetime('Start Programmed Date', compute='calculate_start_programmed_date',store=True)
    end_programmed_date = fields.Datetime('End Programmed Date', compute='calculate_end_programmed_date',store=True)
    start_executed_date = fields.Datetime('Start Executed Date', compute='calculate_start_executed_date',store=True)
    end_executed_date = fields.Datetime('End Executed Date', compute='calculate_end_executed_date',store=True)
    counter_spare_parts = fields.Integer(string='Spare Parts')#compute='compute_counter_spare_parts', 
    garage_id = fields.Many2one('mntc.garage', string='Taller',  related='workorder_id.garage_id',store=True)
    tasks_cost = fields.Float(string='Spare Cost',compute='compute_tasks_cost', store=True)
    program_cost = fields.Float(string='Program cost',compute='get_program_cost', store=True)
    program_cost_supplier = fields.Float(string='Program cost supplier',compute='get_program_cost_supplier', store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle id',related='workorder_id.vehicle_id',store=True)
    movil_nro = fields.Char('Movil', readonly=True, store=True, related='workorder_id.movil_nro')
    type_mntc = fields.Selection([('type_mntc_1', 'Preventive'), ('type_mntc_2', 'Corrective'), ('type_mntc_3', 'Predictive'), ('type_mntc_4', 'Improvement')], 'type of maintenance', default='type_mntc_2', readonly=True, store=True, related='workorder_id.type_mntc')
    priority = fields.Selection([('priority_1', 'Emergency'), ('priority_2', 'Urgent'), ('priority_3', 'Programmed')], string='Priority', readonly=True, store=True, related="workorder_id.priority")
    request_id = fields.Many2one('mntc.request', string='Request', readonly=True, store=True, related='workorder_id.request_id')
    location_id = fields.Many2one('mntc.location', string='Location', domain="[('garage_id','=',garage_id)]", readonly=True, store=True, related='workorder_id.location_id')
    classification1 = fields.Many2one('mntc.workorder.classification', 'Clasificación')
    filter_components   = fields.Boolean(string='Filter Components') 
    fail_spare_id = fields.Many2one('mntc.spare.part.type', string='Failing part')
    cause_id = fields.Many2one('mntc.causes', string='Cause id')
    action_taken_id  = fields.Many2one('mntc.action.taken', string='Action taken')
    process_description_programm = fields.Text(string='Process description programm')
    symptom_ids = fields.Many2one('mntc.symptoms', string='Symptoms', readonly=True, store=True, related='request_id.symptom_ids')
    detection_method = fields.Many2one('mntc.detection.methods', string='Detection methods', readonly=True, store=True, related='request_id.detection_method')
    required_technicians = fields.Integer(string='Required technicians', store=True, compute='calculate_required_technicians')
    service_type_id = fields.Many2one('mntc.services.type', string='Service', related='vehicle_id.service_type_id', store=True)
    vehiculo_linea_id = fields.Many2one('vehiculos.lineas', string='Vehiculo linea', related='vehicle_id.vehiculo_linea', store=True)
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Marca', related='vehiculo_linea_id.marca', store=True)
    disponibilidad = fields.Selection([('vendido','Vendido'),('proceso_legalizacion','En legalizacion'),('operacion','En Operacion'),('fuera_operacion','Fuera de operacion'),('mantenimiento','En Mantenimiento')], 'Disponibilidad', related='vehicle_id.disponibilidad', store=True)
    inspection_ok = fields.Char(compute='get_inspection_ok', string='Inspection OK')
    odometer = fields.Float(string='odometer')
    odometer_compute = fields.Float(string='odometer_compute',compute='calculate_odometer_workorder')
    executed_inspections_ids = fields.One2many('mntc.executed.inspections', inverse_name='task_id', string='Executed inspections')
    disciplina_rh = fields.One2many('mntc.workforce.type.rh','task_id',string='Disciplina')
    disciplina_ejecutada_rh = fields.One2many('mntc.executed.workforce.type.rh', 'task_id', string='Disciplina ejecutada')
    repuesto = fields.One2many('mntc.repuestos', 'tasks_id', string='Repuestos')
    servicio = fields.One2many('mntc.servicios', 'tasks_id', string='Servicios')
    component_id =  fields.Many2one('mntc.component',string='Componentes', domain="[('id','in', component_ids)]")
    component_ids = fields.Many2many(related='system_id.component_ids', string='Componentes Sistema')
    spare_part_type_id = fields.Many2one('mntc.spare.part.type', string='Parte que falla', domain="[('component_ids','in',[component_id])]")
    workorder_state = fields.Selection(related='workorder_id.state',string='Estado ot')
    branch_id = fields.Many2one(related='garage_id.branch_id')
    request_classification1 = fields.Many2one(related='request_id.classification1', string='Clasificación solicitud',store=True)
    request_priority_id = fields.Selection(related='request_id.priority_id', string='Prioridad solicitud', store=True)
 
    def _get_technicians(self):
        context = self._context.copy()
        technician_ids = self._context.get('technician_ids') or False
        tech_ids = []
        domain = []
        if technician_ids:
            for tech_id in technician_ids[0][2]:

                tech_ids.append(tech_id)
            domain = "[('id','in'," + str(tech_ids) + ")]"
        else:
            domain = "[('id','<',0)]"

        return domain

    def compute_counter_spare_parts(self):
        count = self.env['mntc.spare.part.x.task'].search_count([('task_id', '=', self.id)])
        self.counter_spare_parts = count

    def calculate_odometer_workorder(self):       
        for tasks in self:
            odometer_task=0
            if  tasks.workorder_id:
                for odometer_io in tasks.workorder_id.io_ids:
                    if  odometer_task < odometer_io.odometer:
                        odometer_task = odometer_io.odometer
            tasks.odometer_compute = odometer_task
            tasks.write({'odometer':odometer_task})
        return True 
                
    @api.depends('executed_inspections_ids')
    def get_inspection_ok(self):

        inspection_count = 0
        inspection_ok_count = 0

        if self.executed_inspections_ids:
            for executed_inspection in self.executed_inspections_ids:
                inspection_count += 1
                if executed_inspection.ok:
                    inspection_ok_count += 1

        inspection_complete_of = "{}/{}".format(str(inspection_ok_count),str(inspection_count))    

        self.inspection_ok = inspection_complete_of
    
    # @api.constrains('required_technicians')
    # def _check_required_technicians(self):
    #     for task in self:
    #         if task.required_technicians > 5 or task.required_technicians < 1:
    #             raise ValidationError(_('Enter value between 1-5.'))

    #Costo repuesto
    @api.depends('repuesto')
    def compute_tasks_cost(self):
        for task in self:
            obj_repuesto = self.env['mntc.repuestos'].search([('tasks_id','=',task.id)])

            sum_repuesto = 0
            if obj_repuesto:
                for repuesto in obj_repuesto:
                    repuesto.get_standard_price()
                    tmp_sum = repuesto.qty_done * repuesto.standard_price
                    sum_repuesto += tmp_sum

            task.tasks_cost = sum_repuesto


    @api.depends('disciplina_ejecutada_rh')
    #Costo mano de obra
    def get_program_cost(self):
        for tasks in self:
            program_cost = tasks.garage_id.time_value
            spent_time = 0
            for program in tasks.disciplina_ejecutada_rh:
                if not program.res_partner_id:
                    spent_time += program.spent_time
          
            tasks.program_cost = spent_time * program_cost

    #Costo servicio
    @api.depends('servicio')
    def get_program_cost_supplier(self):
        for task in self:
            obj_servicio = self.env['mntc.servicios'].search([('tasks_id','=',task.id)])

            sum_servicio = 0
            if obj_servicio:
                for servicio in obj_servicio:
                    tmp_sum = servicio.cantidad * servicio.price_unit
                    sum_servicio += tmp_sum
           
            task.program_cost_supplier = sum_servicio
    
    def get_spare_and_inspection(self):
        if self.activity_id:
            self.system_id = self.activity_id.system_id
            self.estimated_time = self.activity_id.estimated_time
            self.process_description = self.activity_id.description
            self.required_technicians = self.activity_id.required_technicians

            for spare in self.spare_part_ids:
                spare[0].unlink()
            spare_ids = self.spare_part_ids.ids
            for spare_activity in self.activity_id.spare_part_type_ids:
                spare_vals = {
                    'task_id': self.id,
                    'spare_part_type_id': spare_activity.id,
                    'qty_used': 0,
                }
                info = (0,0,spare_vals)
                spare_new = self.env['mntc.spare.part.x.task'].create(spare_vals)
                spare_ids.append(spare_new.id)
            for executed in self.executed_inspections_ids:
                executed[0].unlink()                
            executed_ids = self.executed_inspections_ids.ids
            for inspection in self.activity_id.inspections_ids:
                inspection_vals = {
                    'name': inspection.name,
                    'task_id': self.id,
                    'inspection_type': inspection.inspection_type,
                    'sequence': inspection.sequence,
                    'min_value': inspection.min_value,
                    'max_value': inspection.max_value,
                    'inspection_id': inspection.id,
                    'test_uom_id': inspection.uom_id.id,
                    'uom_id': inspection.uom_id.id,
                    'condition': inspection.condition,
                 }
                executed_inspection_new = self.env['mntc.executed.inspections'].create(inspection_vals)
                executed_ids.append(executed_inspection_new.id)
                mntc_executed_inspections_answer_pool = self.env[ 'mntc.executed.inspections.answer']
                if inspection.inspection_type == "qualitative":
                    if inspection.inspection_values_ids: 
                        for inspection_values in inspection.inspection_values_ids:
                            inspection_inspections_answer_vals = {
                                'name': inspection_values.name,
                                'executed_inspection_id': executed_inspection_new.id,
                                'ok': inspection_values.ok,          
                            }
                            new_mntc_executed_inspections_answer = mntc_executed_inspections_answer_pool.create(inspection_inspections_answer_vals)

                            if new_mntc_executed_inspections_answer.ok:
                                executed_inspection_new.executed_inspection_answer_id = new_mntc_executed_inspections_answer.id
        return True

    @api.depends('disciplina_rh')
    def calculate_end_programmed_date(self):
        for tasks in self:
            dates = []

            for disciplina in tasks.disciplina_rh:
                if disciplina.end_programmed_date:
                    dates.append(disciplina.end_programmed_date)
            
            if not dates:
                tasks.end_programmed_date = tasks.workorder_id.end_programmed_date
            else:
                tasks.end_programmed_date = max(dates)

    @api.depends('disciplina_ejecutada_rh')
    def calculate_required_technicians(self):
        for tasks in self:
            sum_technicians = 0
            if not tasks.disciplina_ejecutada_rh:
                tasks.required_technicians = 0
            else:
                for disciplina in tasks.disciplina_ejecutada_rh:
                    sum_technicians += 1
                
                tasks.required_technicians = sum_technicians

    @api.depends('disciplina_rh')
    def calculate_start_programmed_date(self):
        for tasks in self:
            dates = []

            for disciplina in tasks.disciplina_rh:
                if disciplina.start_programmed_date:
                    dates.append(disciplina.start_programmed_date)
            
            if not dates:
                tasks.start_programmed_date = tasks.workorder_id.start_programmed_date
            else:
                tasks.start_programmed_date = min(dates)

    
    @api.depends('disciplina_ejecutada_rh')
    def calculate_spent_time(self):
        for tasks in self:
            sum_spent_time = 0
            if not tasks.disciplina_ejecutada_rh:
                tasks.spent_time = 0
            else:
                for disciplina in tasks.disciplina_ejecutada_rh:
                    sum_spent_time += disciplina.spent_time
                
                tasks.spent_time = sum_spent_time

    @api.depends('disciplina_ejecutada_rh')
    def calculate_end_executed_date(self):
        for tasks in self:
            dates = []
            for disciplina in tasks.disciplina_ejecutada_rh:
                if disciplina.end_executed_date:
                    dates.append(disciplina.end_executed_date)
            
            if not dates:
                tasks.end_executed_date = False
            else:
                tasks.end_executed_date = max(dates)

            # if tasks.spent_time:
            #     result = '{0:02.0f}:{1:02.0f}'.format(*divmod(tasks.spent_time * 60, 60))
            #     if tasks.start_executed_date:
            #         start = tasks.start_executed_date
            #         hours=int(result[0:2])
            #         minutes=int(result[3:5])
            #         date_field2 = start + timedelta(hours=hours,minutes=minutes)
            #         tasks.end_executed_date = date_field2
            #     else:
            #         tasks.end_executed_date = False
            # else:

    @api.depends('disciplina_ejecutada_rh')
    def calculate_start_executed_date(self):
        for tasks in self:
            count = 0
            fecha_tmp = 0
            tmp_start_executed_date = datetime.utcnow()

            if not tasks:
                tasks.start_executed_date = False
            else:
                if not tasks.disciplina_ejecutada_rh:
                    tasks.start_executed_date = False
                else:
                    for disciplina in tasks.disciplina_ejecutada_rh:
                        if count == 0:
                            count += 1
                            if disciplina.start_executed_date:
                                tmp_start_executed_date = disciplina.start_executed_date

                        if disciplina.start_executed_date:
                            fecha_tmp += 1
                            if disciplina.start_executed_date < tmp_start_executed_date:
                                tmp_start_executed_date = disciplina.start_executed_date
                    
                    if fecha_tmp > 0:
                        tasks.start_executed_date = tmp_start_executed_date
                    else:
                        tasks.start_executed_date = False
                

    @api.onchange('disciplina_rh')  
    def disciplina_rh_change(self):
        for disciplina in self.disciplina_rh:
            disciplina.task_id = self.id

    @api.onchange('component_id')  
    def component_change(self):
        for tasks in self:
            if tasks.component_id.name == 'GENERAL':
                obj_spare_part_id = self.env['mntc.spare.part.type'].search([('name', '=', 'GENERAL')])
                tasks.spare_part_type_id = obj_spare_part_id
            else:
                tasks.spare_part_type_id = False
            
    @api.onchange('activity_id')  
    def _get_complete_name(self):
        self.load_activity_fields()

    @api.onchange('system_id')
    def system_id_onchange(self):
        if self.system_id.name == 'GENERAL':
            obj_component_id = self.env['mntc.component'].search([('name', '=', 'GENERAL')])
            self.component_id = obj_component_id
        else:
            self.component_id = False

    @api.model
    def load_activity_fields(self):
        for tasks in self:
            if tasks.activity_id:
                tasks.executed_inspections_ids = False 
                tasks.disciplina_rh = False

                tasks.name = tasks.activity_id.name
                tasks.system_id = tasks.activity_id.system_id

                # if tasks.system_id.name == 'GENERAL':
                #     obj_component_id = self.env['mntc.component'].search([('name', '=', 'GENERAL')]).id
                #     obj_spare_part_id = self.env['mntc.spare.part.type'].search([('name', '=', 'GENERAL')]).id

                #     tasks.component_id = obj_component_id
                #     tasks.spare_part_type_id = obj_spare_part_id

                tasks.estimated_time = tasks.activity_id.estimated_time
                tasks.process_description = tasks.activity_id.description
                tasks.required_technicians = tasks.activity_id.required_technicians

                obj_repuesto = []
                for repuesto in tasks.activity_id.repuesto:
                    vals_repuesto = {
                        'producto': repuesto.producto.id,
                        'cantidad': repuesto.cantidad
                    }

                    obj_repuesto.append((0,0,vals_repuesto))

                tasks.repuesto = obj_repuesto

                obj_servicio = []
                for servicio in tasks.activity_id.servicio:
                    vals_servicio = {
                        'producto': servicio.producto.id,
                        'cantidad': servicio.cantidad,
                        'res_partner_id': servicio.res_partner_id.id,
                        'description': servicio.description,
                        'price_unit': servicio.price_unit,
                        'uom_id': servicio.uom_id.id
                    }

                    obj_servicio.append((0,0,vals_servicio))
                
                tasks.servicio = obj_servicio

                result = []
                for activity in tasks.activity_id.inspections_ids:
                    executed_inspection_answer_id = False
                    for respuesta in activity.inspection_values_ids:
                        if respuesta.ok:
                            executed_inspection_answer_id = respuesta.id


                    inspections_vals = {
                            'name': activity.name,
                            'sequence': activity.sequence,
                            'inspection_id': activity.id,
                            'executed_inspection_answer_id': executed_inspection_answer_id,
                            'inspection_type': activity.inspection_type,
                            'condition': activity.condition,
                            'min_value': activity.min_value,
                            'max_value': activity.max_value,
                            'uom_id': activity.uom_id,
                            'task_id': tasks.id,
                        }
                    result.append((0,0,inspections_vals))
                tasks.executed_inspections_ids = result

                if tasks.workorder_id.state == 'planeacion' or tasks.workorder_id.state == 'programmed':
                    result = []

                    for disciplina in tasks.activity_id.disciplina:
                        tmp_estimated_time = False
                        if disciplina.estimated_time:
                            tmp_estimated_time = disciplina.estimated_time
                        
                        if tasks.estimated_time:
                            tmp_estimated_time = tasks.estimated_time

                        if tmp_estimated_time:
                            date_result = '{0:02.0f}:{1:02.0f}'.format(*divmod(disciplina.estimated_time * 60, 60))
                            if tasks.start_programmed_date:
                                start = tasks.start_programmed_date
                                hours=int(date_result[0:2])
                                minutes=int(date_result[3:5])
                                date_field2 = start + timedelta(hours=hours,minutes=minutes)
                                tasks.end_programmed_date = date_field2
                            else:
                                tasks.end_programmed_date = False

                        disciplina_vals = {
                            'name' : disciplina.workforce_type_id.name,
                            'code' : disciplina.workforce_type_id.code,
                            'start_programmed_date': tasks.start_programmed_date,
                            'end_programmed_date': tasks.end_programmed_date,
                            'description' : disciplina.workforce_type_id.description,
                            'active' : disciplina.workforce_type_id.active,
                            'task_id' : tasks.id,
                            'programmed_time' : disciplina.estimated_time,
                            'workforce_type_id' : disciplina.workforce_type_id.id
                            }
                        result.append((0,0,disciplina_vals))
                    if tasks.disciplina_rh:
                        tasks.disciplina_rh += result
                    else:
                        tasks.disciplina_rh = result

                if tasks.workorder_id.state == 'in_progress':
                    result = []
                    for disciplina in tasks.activity_id.disciplina:
                        disciplina_ejecutada_vals = {
                                'name': disciplina.workforce_type_id.name,
                                'code': disciplina.workforce_type_id.code,
                                'description': disciplina.workforce_type_id.description,
                                'active': disciplina.workforce_type_id.active,
                                'task_id': tasks.id,
                                'workforce_type_id': disciplina.workforce_type_id.id,
                            }
                        result.append((0,0,disciplina_ejecutada_vals))

                    if result:
                        if tasks.disciplina_ejecutada_rh:
                            tasks.disciplina_ejecutada_rh += result
                        else:
                            tasks.disciplina_ejecutada_rh = result

    def get_technicians(self, id):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).id
        technician_id = self.env['mntc.technician'].search([('employee_id', '=', employee_id)]).id
        tasks_id = self.env['mntc.tasks'].search([('id', '=', id)])
        if employee_id:
            technician_ids = []
            for ids in tasks_id.technician_ids:
                technician_ids.append(ids.id)
            if technician_id in technician_ids:
                return technician_id
            else:
                raise ValidationError(_('Error in configured'+": "+"you must be assigned to this task to start runtime"))
        else:
            raise ValidationError(_('Error in configured'+": "+"You must be  registered as an employee"))
    
    def return_action_to_open_spare_parts(self):
        if self._context is None:
            self._context = {}
        if self._context.get('xml_id'):
            res = {
                'name': 'Partes que fallan',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mntc.spare.part.x.task',
                'target': 'current',
                'domain': "[('task_id','in',[" + str(self._ids[0]) + "])]"
            }
            return res
        return False    

class mntc_executed_inspections(models.Model):
    _name = 'mntc.executed.inspections'
    _description = 'Inspecciones ejecutadas'

    name = fields.Char(string="Question", required=True)
    task_id = fields.Many2one('mntc.tasks', string='Task')
    sequence = fields.Integer(string='Sequence')
    inspection_type = fields.Selection([('qualitative', 'Qualitative'), ('quantitative', 'Quantitative')], string='Type', required=True)
    quantitative_value = fields.Float('Quantitative value', digits=(16, 5), help="Value of the result if it's a quantitative question.")
    ql_value_text = fields.Char(string='Qualitative value')
    ok = fields.Boolean(string="Ok?", readonly=True, store=True, related="executed_inspection_answer_id.ok") 
    description = fields.Text(string='Description')
    not_apply = fields.Boolean(string="Not apply")
    short_note = fields.Char(string='Short note')
    inspection_id = fields.Many2one("mntc.inspections", string="Inspection")
    min_value = fields.Float(string='Min', digits=(16, 5), help="Minimum valid value if it's a quantitative question.")
    max_value = fields.Float(string='Max', digits=(16, 5), help="Maximum valid value if it's a quantitative question.")
    test_uom_id = fields.Many2one('product.uom', string='Test UoM', help="UoM for minimum and maximum values if it's a quantitative question.")
    test_uom_category = fields.Many2one("product.uom.categ", related="test_uom_id.category_id", store=True)
    uom_id = fields.Many2one('product.uom', string='UoM', domain="[('category_id', '=', test_uom_category)]", help="UoM of the inspection value if it's a quantitative question.")
    task_state = fields.Selection([('started', "Abierto"), ('ended', "Finalizado"), ('canceled', "Cancelado")], string="State", related="task_id.state")#('draft', "Draft"),('programed', "Programed"), 
    executed_inspection_answer_id = fields.Many2one('mntc.inspections.values', string='Respuesta', domain="[('inspection_id', '=', inspection_id)]")
    condition = fields.Selection([('greater_than', '>'),('greater_than_or_equal', '>='),('less_than', '<'),('less_than_or_equal', '<='),('equality', '=='),('inequality', '!='),('between', '<x<') ], string='Condition')

    @api.depends('inspection_type', 'uom_id', 'test_uom_id', 'max_value', 'min_value', 'quantitative_value')
    def quality_test_check(self):
        for record in self:
            if record.inspection_type == 'qualitative':     
                record.ok = record.executed_inspection_answer_id.ok
            else:
                if record.uom_id.id == record.test_uom_id.id:
                    amount = record.quantitative_value
                else:
                    amount = record.env['product.uom']._compute_qty(
                        record.uom_id.id, record.quantitative_value,
                        record.test_uom_id.id)
                if record.condition == 'between':
                    record.ok = record.max_value >= amount >= record.min_value
                elif record.condition == 'greater_than':
                    record.ok = True if amount > record.min_value else False
                elif record.condition == 'greater_than_or_equal':
                    record.ok = True if amount >= record.min_value else False
                elif record.condition == 'less_than':
                    record.ok = True if amount < record.min_value else False
                elif record.condition == 'less_than_or_equal':
                    record.ok = True if amount <= record.min_value else False
                elif record.condition == 'equality':
                    record.ok = True if amount == record.min_value else False
                elif record.condition == 'inequality':
                    record.ok = True if amount != record.min_value else False
                
    
    # def set_answer(self):
    #     if self.inspection_type == 'qualitative':
    #         for inspection in self.executed_inspections_answer_ids:
    #             if inspection.ok:
    #                 self.executed_inspection_answer_id = inspection.id

    @api.onchange('executed_inspection_answer_id')
    def ochange_qualitative_value(self):
        if self.executed_inspection_answer_id:
            self.ql_value_text = self.executed_inspection_answer_id.name
    
class mntc_executed_inspections_answer(models.Model):
    _name = 'mntc.executed.inspections.answer'
    _description = 'Respuesta de inspecciones ejecutadas'

    executed_inspection_id = fields.Many2one("mntc.executed.inspections", string="Inspection")
    name = fields.Char(string='Name', required=True)
    ok = fields.Boolean(string='Correct answer?', help="When this field is marked, the answer is considered correct.")


class purchase_requisition_multicompany(models.Model):
    _name = 'purchase.requisition.multicompany'
    _description = 'Requisición multicompañia, revisar'

    company_name = fields.Char(string='Company')
    workorder_id = fields.Many2one('mntc.workorder', string='Work order id')
    # purchase_requisition_id = fields.Many2one('purchase.requisition', string='Purchase requisition id')
    name = fields.Char(string='Reference')
    ordering_date = fields.Date(string='Date')
    user_id = fields.Many2one('res.users', string='User')
    date_end = fields.Datetime(string='Date End')
    origin = fields.Char(string='Origin')
    state = fields.Selection([
                ('draft', 'Draft'), 
                ('in_progress', 'Confirmed'),
                ('open', 'Bid Selection'), 
                ('done', 'PO Created'),
                ('cancel', 'Cancelled'),                
                ], string='Status')
    id_multicompany = fields.Integer(string='Id Multicompany')
    state_help = fields.Char(string='state help')

    