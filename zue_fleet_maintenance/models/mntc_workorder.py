from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class mntc_workorder(models.Model):
    _name = 'mntc.workorder'
    _rec_name = 'number'
    _description = 'Órden de trabajo'

    number = fields.Char(string='Number', required=True, default='New')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle id')
    request_id = fields.Many2one('mntc.request', string='Request', readonly=True) 
    work_routine_ids = fields.Many2many('mntc.routines', string='Work routine ids')#,'mntc_workorder_x_mntc_routines', 'workorder_id', 'routine_id'
    work_task_ids = fields.One2many('mntc.tasks','workorder_id',string='Work task ids')
    estimated_time = fields.Float(string='Estimated time', compute='compute_estimated_time', store=True)
    spent_time = fields.Float(string='Spent time', compute='calculate_time', store=True)
    # spent_time_store = fields.Float(string='Spent time store')
    technician_ids = fields.Many2many('mntc.technician', 'mntc_workorder_x_mntc_technician', 'workorder_id', 'technician_id', string='Technician_ids')
    start_programmed_date = fields.Datetime(string='Start programmed date')#,compute='get_programed_date'
    end_programmed_date = fields.Datetime(string='End programmed date')#,compute='get_programed_date', store=True)
    start_date = fields.Datetime(string='Start date', compute='get_start_date', store=True)
    end_date = fields.Datetime(string='End date', compute='get_end_date', store=True)
    state = fields.Selection([('planeacion', "Planeación"), ('waiting_parts', 'Waiting Parts'), ('programmed', "Programmed"), ('in_progress', "In progress"), ('stopped', "Stopped"), ('ended', "Ended"), ('canceled', "Canceled")], string="State", default='planeacion')
    origin_state = fields.Selection([('planeacion', "Planeación"), ('waiting_parts', 'Waiting Parts'), ('programmed', "Programmed"), ('in_progress', "In progress"), ('stopped', "Stopped"), ('ended', "Ended"), ('canceled', "Canceled")], string="Estado Origen", default='planeacion')
    priority = fields.Selection([('priority_1', 'Emergency'), ('priority_2', 'Urgent'), ('priority_3', 'Programmed')], string='Priority')
    observation = fields.Text(string='Observation')
    type_mntc = fields.Selection([('type_mntc_1', 'Preventive'), ('type_mntc_2', 'Corrective'), ('type_mntc_3', 'Predictive'), ('type_mntc_4', 'Improvement')], 'type of maintenance', default='type_mntc_2')
    supplier_id = fields.Many2one('zue.res.branch', 'Supplier')
    garage_arrival_date = fields.Datetime(string='Garage arrival date')
    movil_nro = fields.Char('Movil', related='vehicle_id.movil_nro', store=True)
    scheduled_start_date = fields.Datetime(string='Scheduled start date')
    scheduled_end_date = fields.Datetime(string='Scheduled end date')
    garage_id = fields.Many2one('mntc.garage', string='Taller')
    location_id = fields.Many2one('mntc.location', string='Location', domain="[('garage_id','=',garage_id)]")
    io_ids = fields.Many2many('mntc.io', 'mntc_io_x_mntc_workorder', 'workorder_id', 'io_id','Input/Outputs', track_visibility='onchange', domain="[('vehicle_id','=',vehicle_id),('state','=','in')]")  
    counter_stock_picking = fields.Integer(compute='compute_counter_stock_picking', string='Órdenes de Entrega')
    counter_purchase_order = fields.Integer(compute='compute_counter_purchase_order', string='Solicitudes de Cotización')
    stock_picking_ids = fields.One2many('stock.picking','workorder_id',string='Órdenes de entrega')
    purchase_order_ids = fields.One2many('purchase.order','workorder_id',string='Solicitud de cotización')
    #fleet_id = fields.Many2one('fleet.vehicle','Vehículo')
    # purchase_requisition_ids = fields.One2many('purchase.requisition','workorder_id',string='Purchase requisition ids')
    approved_tech_id = fields.Many2one('mntc.technician', 'Approved by', readonly=True)
    approved_date = fields.Datetime('Approved Date' , readonly=True)
    company_id = fields.Many2one('res.company', compute='get_company',string='Company')
    purchase_requisition_multicompany_ids = fields.One2many('purchase.requisition.multicompany','workorder_id',string='Purchase requisition ids')
    in_charge = fields.Selection(selection=[('planning', 'Planning'), ('coordinating', 'Coordinating')], string="In Charge")
    workorder_cost = fields.Float(compute='compute_workorder_cost',string='Cost', store=True) 
    workforce_cost_pro = fields.Float('Workforce cost', compute='get_worforce_cost_pro', store=True) 
    workforce_cost_pro_supplier = fields.Float('Workforce cost supplier', compute='get_worforce_cost_pro_supplier', store=True) 
    service_type_id = fields.Many2one('mntc.services.type',related="vehicle_id.service_type_id",string='Tipo Servicio',readonly=True, store=True)
    repuesto_summary = fields.One2many('mntc.resumen.repuestos', 'workorder_id', string='Repuestos', compute='_get_repuestos_summary', store=False) 
    servicio_summary = fields.One2many('mntc.resumen.servicios', 'workorder_id', string='Servicios', compute='_get_servicios_summary', store=False)
    branch_id = fields.Many2one(related='garage_id.branch_id') 
    counter_io = fields.Integer(compute='compute_counter_io', string='Entradas')
    real_time = fields.Float(string='Duración Real', compute='calculate_real_time', store=True)
    created_by = fields.Many2one('res.users', string='Creado por', readonly=True)
    ended_by = fields.Many2one('res.users', string='Finalizado por', readonly=True)
    #workorder_odometer = fields.One2many('mntc.workorder.routines', 'workorder_id', string='Orden de trabajo x Rutina')
    odometer = fields.Integer(string='Odómetro')
    assigned_company_id = fields.Many2one(related='vehicle_id.assigned_company_id')
 
    def call_up_wizard(self):
        yes_no = ''
        count_repuesto = 0
        count_repuesto_without_move = 0
        count_repuesto_sin_entrega = 0

        if self.work_task_ids:
            for tasks in self.work_task_ids: 
                if tasks.repuesto:
                    for repuestos in tasks.repuesto:
                        if not repuestos.move_line_id:
                            count_repuesto_without_move += 1
                        else:
                            if repuestos.move_line_id.state in ['cancel']:
                                count_repuesto_sin_entrega += 1
                else:
                    count_repuesto += 1

            if count_repuesto_without_move > 0:
                yes_no = "Hay repuestos sin orden de entrega.\n"

            if count_repuesto > 0:
                yes_no = "Algunas tareas no tienen repuestos en la órden de trabajo.\n"
                    
            if count_repuesto_sin_entrega > 0:
                yes_no = "Los repuestos no fueron entregados."
                
            yes_no += "\n¿Desea continuar?"

            return {
                    'name': 'Deseas continuar?',
                    'type': 'ir.actions.act_window',
                    'res_model': 'confirm.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_workorder_id': self.id,
                                'default_yes_no': yes_no}
                    }
        else:
            self.mntc_workorder_end()

    @api.model
    def create(self, vals):
        garage_object = self.env['mntc.garage'].search([('id', '=', vals['garage_id'])])
        sequence_code = 'mntc_OT-' + garage_object.code
        sequence_object = self.env['ir.sequence'].search([('code', '=', sequence_code)])
        last_write_date = sequence_object.write_date
        date = last_write_date
        last_year = date.year
        last_month = date.month
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().month

        if vals['priority'] == 'priority_3':
            vals['state'] = 'planeacion'

        vals['origin_state'] = vals['state']

        if last_year == current_year:
            if int(last_month) < int(current_month):
                sequence_object.write({'number_next': 1})
            elif int(last_year) < int(current_year):
                sequence_object.write({'number_next': 1})
        seq = self.env['ir.sequence'].next_by_code(sequence_code) or '/'

        vals['number'] = seq + "/"

        obj_workorder = super(mntc_workorder, self).create(vals)

        name = ""

        if obj_workorder.request_id:
            obj_workorder.write({'number': obj_workorder.number + obj_workorder.request_id.name})
        elif obj_workorder.work_routine_ids:
            for routines in obj_workorder.work_routine_ids:
                name = routines.name
                break

            obj_workorder.write({'number': obj_workorder.number + name})

        odometer = 0
        if obj_workorder.work_routine_ids:
            for routine in obj_workorder.work_routine_ids:
                odometer_task = 0

                if obj_workorder.io_ids:
                    for odometer_io in obj_workorder.io_ids:
                        if  odometer_io.state in ['in']:
                                odometer_task = odometer_io.odometer
                        
                        odometer = odometer_task
                    if not odometer:
                        odometer_counter = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=',obj_workorder.vehicle_id.id)],order='value desc',limit=1)
                        odometer = odometer_counter 
                
                workorder_routines_obj = self.env['mntc.workorder.routines'].search([('routine_id', '=', routine.id),('vehicle_id', '=', self.vehicle_id.id)])

                if not workorder_routines_obj:
                    if not odometer:
                        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'check_vehicle_odometer')])
                        if not obj_ws:
                            raise ValidationError(_("Error! No ha configuraco un web service con el nombre 'check_vehicle_odometer'")) 
                
                        date = (datetime.now()-timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
                        placa = str(obj_workorder.vehicle_id.placa_nro)

                        obj_odometer = obj_ws.connection_requests(date,placa)

                        if 'odometro' in obj_odometer:
                            for odometer_list in obj_odometer['odometro']:
                                for odometer in odometer_list:
                                    odometer = int(odometer['odometro'])
                        
                        if odometer:
                            obj_workorder.vehicle_id.write({'last_odometer_ws': odometer})    
                            if not workorder_routines_obj:
                                vals2 = {
                                        'workorder_id': obj_workorder.id,
                                        'routine_id':   routine.id,
                                        'vehicle_id':   obj_workorder.vehicle_id.id,
                                        'odometer' :    odometer 
                                        }   
                                workorder_routines_obj.create(vals2)
                            else:
                                workorder_routines_obj.write({'workorder_id': obj_workorder.id,
                                                                'odometer': odometer})

        obj_workorder.write({'odometer': int(float(obj_workorder.vehicle_id.last_odometer_ws))})

        return obj_workorder

    def write(self, vals):
        obj_workorder = super(mntc_workorder, self).write(vals)

        if "start_programmed_date" in vals:
            self.start_programmed_date_change()

        return obj_workorder



    def _get_repuestos_summary(self):
        for record in self:
            #Se recorren los repuestos para saber cuales tienen orden de entrega y actualizar el resumen de repuestos
            repuestos = []

            for tasks in record.work_task_ids: 
                for productos in tasks.repuesto:
                    sum_reserved_availability = 0
                    sum_quantity_done = 0
                    tmp_qty_available = 0

                    if productos.move_line_id.id:
                        query = '''
                            select a.product_qty, a.qty_done
                            from stock_move_line a
                            where a.move_id = %s 
                            limit 1
                        ''' % (productos.move_line_id.id)

                        self.env.cr.execute(query)

                        stock_move_ids = self.env.cr.fetchone()
                    
                        if not stock_move_ids:
                            sum_reserved_availability = 0
                            sum_quantity_done = 0
                        else:
                            sum_reserved_availability = stock_move_ids[0]
                            sum_quantity_done = stock_move_ids[1]

                        # obj_orden_entrega = record.env['stock.picking'].search(['&',('partner_id','=', self.env.user.partner_id.id),('workorder_id','=',record.id),('product_id','=',productos.producto.id),('state','!=','cancel')])
                        
                        # sum_uom_qty = 0

                        if record.garage_id.stock_location_id.complete_name and record.assigned_company_id.id:
                            query = '''
                                select a.id
                                from stock_location a
                                where a.complete_name = '%s' and a.company_id = %s 
                                limit 1
                            ''' % (record.garage_id.stock_location_id.complete_name,record.assigned_company_id.id)

                            self.env.cr.execute(query)

                            obj_stock = self.env.cr.fetchone()
                            if obj_stock:
                                stock_destino = obj_stock[0]

                            if stock_destino:
                                query = '''
                                    select a.quantity
                                    from stock_quant a
                                    where a.product_id = '%s' and a.company_id = %s and a.location_id = %s 
                                    limit 1
                                ''' % (productos.producto.product_variant_id.id,record.assigned_company_id.id,stock_destino)

                                self.env.cr.execute(query)

                                stock_picking_ids = self.env.cr.fetchone()
                                if not stock_picking_ids:
                                    tmp_qty_available = 0
                                else:
                                    tmp_qty_available = stock_picking_ids[0]
                       

                    # for orden_entrega in obj_orden_entrega.move_ids_without_package:
                    #     if orden_entrega.state != 'cancel':
                    #         if orden_entrega.product_id.id == productos.producto.id:
                    #             sum_uom_qty += orden_entrega.product_uom_qty
                    #             sum_reserved_availability += orden_entrega.reserved_availability
                    #             sum_quantity_done += orden_entrega.quantity_done
                        
                    repuesto_vals = {
                            'producto': productos.producto.id,
                            'uom_id': productos.uom_id.id,
                            'product_uom_qty': productos.cantidad,
                            'reserved_availability': sum_reserved_availability, 
                            'quantity_done': sum_quantity_done,
                            'qty_available': tmp_qty_available,
                            'workorder_id': record.id,
                            'task_id': tasks.id,
                        }
                    
                    repuestos.append(repuesto_vals)
            
            resumen = self.env['mntc.resumen.repuestos'].create(repuestos) 
            record.repuesto_summary = resumen

    def _get_servicios_summary(self):
        for record in self:
            #Se recorren los servicios para saber cuales tienen solicitud de cotización y actualizar el resumen de repuestos
            servicios = []
            for tasks in record.work_task_ids:
                for servicio in tasks.servicio:
                    if servicio.order_line_id:
                        servicio_vals = {
                                'producto': servicio.producto.id,
                                'name': servicio.description,
                                'product_qty': servicio.order_line_id.product_qty,
                                'price_unit': servicio.order_line_id.price_unit,
                                'taxes_id': servicio.order_line_id.taxes_id.id,
                                'price_subtotal': servicio.order_line_id.price_subtotal,
                                'res_partner_id': servicio.res_partner_id.id,
                                'workorder_id': record.id,
                                'task_id': tasks.id,
                            }
                    else:
                        servicio_vals = {
                                'producto': servicio.producto.id,
                                'name': servicio.description,
                                'product_qty': servicio.cantidad,
                                'price_unit': servicio.price_unit,
                                'taxes_id': servicio.taxes_id,
                                'price_subtotal': 0,
                                'res_partner_id': servicio.res_partner_id.id,
                                'workorder_id': record.id,
                                'task_id': tasks.id,
                            }
        
                    servicios.append(servicio_vals)

            resumen = self.env['mntc.resumen.servicios'].create(servicios)
            record.servicio_summary = resumen

    def unlock_spare_parts(self):
        obj_stock_picking = self.env['stock.picking'].search(['&',('id', 'in',  self.stock_picking_ids.ids),('state', '=', 'confirmed')])
        if obj_stock_picking:
            for record in obj_stock_picking:
                record.action_cancel()

        self.state = self.origin_state

    # def mntc_reprogram(self):
    #     self.start_programmed_date_change()

    def generate_requisition(self):
        if not self.work_task_ids:
            raise ValidationError(_('Error!. No hay tareas registradas para generar una órden de entrega'))

        products = []
        repuestos = []
        services = []
        tmp_services = [] 
        count_service = 0
        proveedores = []
        id_account_analytic = self.vehicle_id.with_context(force_company=self.vehicle_id.assigned_company_id.id).account_analytic_id.id
        obj_stock_location = self.garage_id.with_context(force_company=self.vehicle_id.assigned_company_id.id).stock_location_id
        
        for tasks in self.work_task_ids: 
            # Repuestos
            for productos in tasks.repuesto:                
                id_product = self.env['product.product'].search([('product_tmpl_id','=',productos.producto.id)], limit=1).id
                if not productos.move_line_id:
                    product_vals = {
                            'id_repuesto': productos.id,
                            'name': productos.producto.name,
                            'product_id': id_product,
                            'product_uom': productos.uom_id.id,
                            'product_uom_qty': productos.cantidad,
                            'analytic_account_id': id_account_analytic, #self.vehicle_id.account_analytic_id.id
                            'company_id': self.vehicle_id.assigned_company_id.id,
                        }

                    products.append(product_vals)
                else:
                    if productos.move_line_id.state == 'cancel':
                        product_vals = {
                                'id_repuesto': productos.id,
                                'name': productos.producto.name,
                                'product_id': id_product,
                                'product_uom': productos.uom_id.id,
                                'product_uom_qty': productos.cantidad,
                                'analytic_account_id': id_account_analytic, #self.vehicle_id.account_analytic_id.id
                                'company_id': self.vehicle_id.assigned_company_id.id,
                            }

                        products.append(product_vals)
                   
            # Servicios
            for servicios in tasks.servicio:
                id_product = self.env['product.product'].search([('product_tmpl_id','=',servicios.producto.id)], limit=1).id
                if not servicios.order_line_id:
                    count_service += 1

                    if not servicios.res_partner_id.id in proveedores:
                        proveedores.append(servicios.res_partner_id.id)

                    service_vals = {
                            'id': servicios.id,
                            'product_id': id_product,
                            'name': servicios.producto.name,
                            'account_analytic_id': id_account_analytic, #self.vehicle_id.account_analytic_id.id,
                            'product_qty': servicios.cantidad,
                            'product_uom': servicios.uom_id.id,
                            'price_unit': servicios.price_unit,
                            'taxes_id': servicios.taxes_id.ids,
                            'date_planned': datetime.utcnow(),
                            'company_id': self.vehicle_id.assigned_company_id.id,
                            'proveedor': servicios.res_partner_id.id
                        }

                    tmp_services.append(service_vals)
                else:
                    if servicios.order_line_id.state == 'cancel':
                        count_service += 1

                        if not servicios.res_partner_id.id in proveedores:
                            proveedores.append(servicios.res_partner_id.id)

                        service_vals = {
                                'id': servicios.id,
                                'product_id': id_product,
                                'name': servicios.producto.name,
                                'account_analytic_id': id_account_analytic, #self.vehicle_id.account_analytic_id.id,
                                'product_qty': servicios.cantidad,
                                'product_uom': servicios.uom_id.id,
                                'price_unit': servicios.price_unit,
                                'taxes_id': servicios.taxes_id.ids,
                                'date_planned': datetime.utcnow(),
                                'company_id': self.vehicle_id.assigned_company_id.id,
                                'proveedor': servicios.res_partner_id.id
                            }
                        
                        tmp_services.append(service_vals)

        # Repuestos 
        if products:
            if not self.garage_id.branch_id or not obj_stock_location:
                raise ValidationError(_('Error!. No se ha configurado una ubicación de almacen para el taller.'))

            query = '''
                select spt.id, spt.default_location_src_id, spt.default_location_dest_id
                from stock_picking_type spt
                inner join ir_sequence is2 on spt.sequence_id = is2.id 
                inner join res_company rc on is2.company_id = rc.id 
                inner join stock_warehouse sw on spt.warehouse_id = sw.id
                inner join zue_res_branch zrb on zrb.id = sw.store_id
                where spt.code ='outgoing' and rc.id = %s and zrb.id = %s and spt.default_location_src_id = %s
                limit 1
            ''' % (self.vehicle_id.assigned_company_id.id, self.garage_id.branch_id.id, obj_stock_location.id)

            self.env.cr.execute(query)

            picking_type = self.env.cr.fetchone()
            if not picking_type:
                raise ValidationError(_('Error!. No se encontró un tipo de operación [outgoing] para la compañia que contenga la misma sucursal del taller seleccionado en la orden de trabajo.'))
            else:
                picking_type_id = picking_type[0]
                default_location_src_id = picking_type[1]
                default_location_dest_id = picking_type[2]
                respuestos_sin_id = []

            for record in products:
                product_vals = {
                                'name': record['name'],
                                'product_id': record['product_id'],
                                'product_uom': record['product_uom'],
                                'product_uom_qty': record['product_uom_qty'],
                                'analytic_account_id': record['analytic_account_id']
                            }
                
                respuestos_sin_id.append((0,0,product_vals))


            data_products = {'partner_id': self.env.user.partner_id.id,
                            'scheduled_date': datetime.utcnow(),
                            'picking_type_id': picking_type_id,
                            'origin': self.number,
                            'move_ids_without_package': respuestos_sin_id,
                            'location_id': default_location_src_id,
                            'location_dest_id': default_location_dest_id,
                            'fleet_id': self.vehicle_id.id,
                            'company_id': self.vehicle_id.assigned_company_id.id,
                            'workorder_id': self.id }

            obj_stock = self.env['stock.picking'].with_context(force_company=self.vehicle_id.assigned_company_id.id).create(data_products)
            obj_stock.action_confirm()
            obj_stock.action_assign()

            obj_stock.write({'company_id': self.vehicle_id.assigned_company_id.id})

            for productos in products:
                obj_repuestos = self.env['mntc.repuestos'].search([('id','=',productos['id_repuesto'])])
                producto_id = productos["product_id"]

                if obj_repuestos:
                    for record in obj_stock.move_ids_without_package:
                        if producto_id == record.product_id.id:
                            obj_repuestos.write({'move_line_id': record.id})

                
                    obj_repuestos.get_standard_price()
                    
            self.work_task_ids.compute_tasks_cost()

            espera_partes = 0
            for stock in obj_stock.move_ids_without_package:
                if stock.reserved_availability <= 0:
                    espera_partes += 1

            if espera_partes >= 1:
                self.state = "waiting_parts"
        
        # Servicios
        if count_service > 0:
            if not self.garage_id.branch_id or not obj_stock_location:
                raise ValidationError(_('Error!. No se ha configurado una ubicación de almacen para el taller.'))

            query = '''
                select spt.id, spt.default_location_src_id, spt.default_location_dest_id
                from stock_picking_type spt
                inner join ir_sequence is2 on spt.sequence_id = is2.id 
                inner join res_company rc on is2.company_id = rc.id 
                inner join stock_warehouse sw on spt.warehouse_id = sw.id
                inner join zue_res_branch zrb on zrb.id = sw.store_id
                where spt.code ='incoming' and rc.id = %s and zrb.id = %s and spt.default_location_dest_id = %s
                limit 1
            ''' % (self.vehicle_id.assigned_company_id.id, self.garage_id.branch_id.id, obj_stock_location.id)

            self.env.cr.execute(query)

            picking_type = self.env.cr.fetchone()
            if not picking_type:
                raise ValidationError(_('Error!. No se encontró un tipo de operación [incoming] para la compañia que contenga la misma sucursal del taller seleccionado en la orden de trabajo.'))
            else:
                picking_type_id = picking_type[0]
                default_location_src_id = picking_type[1]
                default_location_dest_id = picking_type[2]
                respuestos_sin_id = []

            for proveedor in proveedores:  
                service_x_proveedor = []
                for record in tmp_services:
                    if proveedor == record.get("proveedor"):
                        service_vals = {
                            'product_id': record['product_id'],
                            'name': record['name'],
                            'account_analytic_id': record['account_analytic_id'],
                            'product_qty': record['product_qty'],
                            'product_uom': record['product_uom'],
                            'price_unit': record['price_unit'],
                            'taxes_id': record['taxes_id'],
                            'date_planned': record['date_planned'],
                            'company_id': self.vehicle_id.assigned_company_id.id,
                        }

                        service_x_proveedor.append((0,0,service_vals))

                if service_x_proveedor:
                    data_services = {'partner_id': proveedor,
                                    'date_order': datetime.utcnow(),
                                    'partner_ref': self.number,
                                    'order_line': service_x_proveedor,
                                    'branch_id': self.garage_id.branch_id.id,
                                    'picking_type_id': picking_type_id,
                                    'company_id': self.vehicle_id.assigned_company_id.id,
                                    'workorder_id': self.id }
                
                    orden = self.env['purchase.order'].with_context(force_company=self.vehicle_id.assigned_company_id.id).create(data_services)

                    for record in tmp_services:
                        search_service = self.env['mntc.servicios'].search([('id','=',record['id'])], limit=1)
                        proveedor_id = record.get("proveedor")
                        
                        if search_service:
                            for producto in orden.order_line:
                                if proveedor == proveedor_id and search_service.producto.id == producto.product_id.id:
                                    search_service.write({'order_line_id': producto.id})


        
    
    # @api.depends('work_task_ids','start_programmed_date')
    # def get_programed_date(self):
    #     for workorder in self:
    #         if not workorder.start_programmed_date:
    #             workorder.end_programmed_date = None
    #         else:
    #             dates = []
    #             for tasks in self.work_task_ids:
    #                 for disciplina in tasks.disciplina_rh:
    #                     if disciplina.end_programmed_date:
    #                         dates.append(disciplina.end_programmed_date)
                
    #             if not dates:
    #                 tasks.end_programmed_date = False
    #             else:
    #                 tasks.end_programmed_date = max(dates)

                # last_task = self.env['mntc.tasks'].search([('workorder_id', 'in', workorder.ids)],order='start_programmed_date desc',limit=1)

                # if not last_task:
                #     workorder.end_programmed_date = None
                # else:
                #     workorder.end_programmed_date = last_task.end_programmed_date

    @api.depends('work_task_ids')
    def get_start_date(self):
        for workorder in self:
            tasks = self.env['mntc.tasks'].search([('workorder_id', 'in', workorder.ids)])

            if not tasks:
                workorder.start_date = False
            else:
                dates = []
                for task in tasks:
                    if not task.disciplina_ejecutada_rh:
                        workorder.start_date = False
                    else:
                        for disciplina in task.disciplina_ejecutada_rh:
                            if disciplina.start_executed_date:
                                dates.append(disciplina.start_executed_date)
                        
                if not dates:
                    workorder.start_date = False
                else:
                    workorder.start_date = min(dates)
                
    @api.depends('work_task_ids')
    def get_end_date(self):
        for workorder in self:
            tasks = self.env['mntc.tasks'].search([('workorder_id', 'in', workorder.ids)])

            if not tasks:
                workorder.end_date = False
            else:
                dates = []
                for task in tasks:
                    if not task.disciplina_ejecutada_rh:
                        workorder.end_date = False
                    else:
                        for disciplina in task.disciplina_ejecutada_rh:
                            if disciplina.end_executed_date:
                                dates.append(disciplina.end_executed_date)
                        
                if not dates:
                    workorder.end_date = False
                else:
                    workorder.end_date = max(dates)

    def get_company(self):
        for workorder in self:
            workorder.company_id = workorder.env.user.company_id
        return True

    def return_action_to_open_purchase_order(self):
        if self._context is None:
            self._context = {}
        if self._context.get('xml_id'):
            res = {
                'name': 'Solicitud de Cotización',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'target': 'current',
                'domain': "[('workorder_id','in',[" + str(self._ids[0]) + "])]"
            }
            return res
        return False

    def return_action_to_open_stock_picking(self):
        if self._context is None:
            self._context = {}
        if self._context.get('xml_id'):
            res = {
                'name': 'Órden de Entrega',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'target': 'current',
                'domain': "[('workorder_id','in',[" + str(self._ids[0]) + "])]"
            }
            return res
        return False

    def return_action_to_open(self):
        res = {
            'name': 'Entrada/Salida',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mntc.io',
            'target': 'current',
            'domain': "[('workorder_ids','in',[" + str(self._ids[0]) + "])]"
        }
        return res    

    def compute_counter_stock_picking(self):
        query = '''
            select count(a.id)
            from stock_picking a
            where a.workorder_id = %s
            limit 1
        ''' % (self.id)

        self.env.cr.execute(query)

        count = self.env.cr.fetchone()

        if count:
            self.counter_stock_picking = count[0]
        else:
            self.counter_stock_picking = 0

    def compute_counter_purchase_order(self):
        query = '''
            select count(a.id)
            from purchase_order a
            where a.workorder_id = %s
            limit 1
        ''' % (self.id)

        self.env.cr.execute(query)

        count = self.env.cr.fetchone()

        if count:
            self.counter_purchase_order = count[0]
        else:
            self.counter_purchase_order = 0

    def compute_counter_io(self):
        count = self.env['mntc.io'].search_count([('workorder_ids', 'in', self.id)])
        self.counter_io = count


    # Repuestos
    @api.depends('work_task_ids')
    def compute_workorder_cost(self):
        for worker_order in self:
            workorder_cost=0
            for task in worker_order.work_task_ids:
                if  task.tasks_cost:
                    workorder_cost += task.tasks_cost

            worker_order.workorder_cost= workorder_cost

    # Mano de obra
    @api.depends('work_task_ids')
    def get_worforce_cost_pro(self):
        for worker_order in self:
            workorder_cost=0
            for task in worker_order.work_task_ids:
                if  task.program_cost:
                    workorder_cost += task.program_cost

            worker_order.workforce_cost_pro= workorder_cost
        
    # Servicios
    @api.depends('work_task_ids')
    def get_worforce_cost_pro_supplier(self):
        for worker_order in self:
            workorder_cost=0
            for task in worker_order.work_task_ids:
                if  task.program_cost_supplier:
                    workorder_cost += task.program_cost_supplier

            worker_order.workforce_cost_pro_supplier= workorder_cost
        
    @api.depends('work_task_ids','start_date', 'end_date')
    def calculate_time(self):
        for worker_order in self:
            count = 0.0
            for task in worker_order.work_task_ids:
                if task.spent_time:
                    count += task.spent_time
                    
            worker_order.spent_time = count

    @api.depends('work_task_ids','start_date','end_date')
    def calculate_real_time(self):
        for worker_order in self:
            if worker_order.start_date and worker_order.end_date:
                diff = worker_order.end_date - worker_order.start_date

                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60

                worker_order.real_time = hours + minutes / 60
            else:
                worker_order.real_time = False

    @api.depends('work_task_ids')
    def compute_estimated_time(self):
        for worker_order in self:
            count = 0
            for task in worker_order.work_task_ids:
                if task.estimated_time:
                    count += task.estimated_time

            worker_order.estimated_time = count

    @api.model
    @api.onchange('work_routine_ids')
    def mntc_work_routine_ids_onchange(self):
        for task in self.work_task_ids:
            if task.routine_id.id not in self.work_routine_ids.ids and task.routine_id:
                self.work_task_ids = [(2,task.id,0)]

    def mntc_work_routine_ids(self):
        result = []
        # self.work_task_ids = False

        for rutinas in self.work_routine_ids:
            
            for activities in rutinas.activity_ids:
                if activities.description:
                    tasks_vals = {
                        'name':activities.name,
                        'workorder_id': self.id,
                        'routine_id': rutinas.id,
                        'activity_id': activities.id,
                        'system_id': activities.system_id.id,
                        'estimated_time': activities.estimated_time,
                        'process_description': activities.description,
                        'required_technicians': activities.required_technicians,
                    }
                else :

                    tasks_vals = {
                        'name':activities.name,
                        'workorder_id': self.id,
                        'routine_id': rutinas.id,
                        'activity_id': activities.id,
                        'system_id': activities.system_id.id,
                        'estimated_time': activities.estimated_time,
                        'required_technicians': activities.required_technicians,
                    }


                result.append((0,0,tasks_vals))

        self.work_task_ids = result
        #self.work_task_ids.load_activity_fields()

        for tasks in self.work_task_ids:
            tasks.load_activity_fields()


    @api.onchange('movil_nro')
    def mntc_movil_nro_onchange(self):
        if self.movil_nro:
            vehicle_id = self.env['fleet.vehicle'].search([('movil_nro', '=', self.movil_nro)])
            if vehicle_id:
                self.vehicle_id = vehicle_id
            else  :
                self.vehicle_id = False
                raise ValidationError(_('Error in movil'+": "+'¡The vehicle does not have an associated fleet number'))

    @api.onchange('vehicle_id')
    def mntc_vehicle_id_onchange(self):
        if self.vehicle_id:
            self.movil_nro = self.vehicle_id.movil_nro

    @api.onchange('request_id')
    def mntc_request_onchange(self):
        if self.request_id:
            self.vehicle_id = self.request_id.vehicle_id
            self.priority = self.request_id.priority_id
            self.type_mntc = self.request_id.type_mntc

    @api.onchange('start_programmed_date')
    def start_programmed_date_on_change(self):
        self.start_programmed_date_change()

    def start_programmed_date_change(self): 
        if not self.start_programmed_date:
            raise ValidationError(_('Error! Debe especificar la fecha de inicio programada.'))

        if self.start_programmed_date:
            # dates = []
            # for tasks in self.work_task_ids:
            #     for disciplina in tasks.disciplina_rh:
            #         if disciplina.end_programmed_date:
            #             dates.append(disciplina.end_programmed_date)
            
            end_programmed_date = None

            end_programmed_date = self.start_programmed_date + timedelta(hours=self.estimated_time)

            # if not dates:
            #     end_programmed_date = self.start_programmed_date
            # else:
            #     end_programmed_date = max(dates)
            
            self.end_programmed_date = end_programmed_date

            #obj_tasks = self.env['mntc.tasks'].search([('workorder_id','in',self.ids)])
            #obj_tasks = self.env['mntc.tasks'].search([('id','in',self.work_task_ids.ids)])
            
            for tasks in self.work_task_ids:
                tasks.start_programmed_date = self.start_programmed_date
                tasks.end_programmed_date = self.end_programmed_date

                for disciplina in tasks.disciplina_rh:
                    disciplina.start_programmed_date = self.start_programmed_date
                    disciplina.end_programmed_date = end_programmed_date

            for io in self.io_ids:
                if io.state == 'programmed':
                    io.scheduled_incoming_date = self.start_programmed_date
                    io.scheduled_outgoing_date = end_programmed_date

            # self.write({'end_programmed_date': end_programmed_date})

            # #obj_tasks = self.env['mntc.tasks'].search([('workorder_id','in',self.ids)])
            # obj_tasks = self.env['mntc.tasks'].search([('id','in',self.work_task_ids.ids)])
            
            # for tasks in obj_tasks:
            #     tasks.write({'start_programmed_date': self.start_programmed_date})

            #     for disciplina in tasks.disciplina_rh:
            #         disciplina.write({'start_programmed_date': self.start_programmed_date,
            #                         'end_programmed_date': end_programmed_date})

            # obj_io = self.env['mntc.io'].search([('id','in',self.io_ids.ids)])
            # for io in obj_io:
            #     if io.state == 'programmed':
            #         io.write({'scheduled_incoming_date': self.start_programmed_date,
            #                   'scheduled_outgoing_date': end_programmed_date})


    def mntc_workorder_programmed(self): 
        if self.start_programmed_date:
            for tasks in self.work_task_ids:
                tasks.write({'start_programmed_date': self.start_programmed_date})
        else:    
            raise ValidationError(_('Error! Debe especificar la fecha de inicio programada.'))

        if self.work_task_ids:
            #self.get_programed_date()
            self.compute_estimated_time()
            self.state = 'programmed'
        else:
            raise ValidationError(_('Error! No ha seleccionado ninguna tarea a programar.'))

        #odometer_val = 0
        for tasks in self.work_task_ids:
            #odometer_val += tasks.odometer_compute
               
            for disciplina in tasks.disciplina_rh:
                if not disciplina.start_programmed_date or not disciplina.end_programmed_date:
                    disciplina.write({'start_programmed_date': self.start_programmed_date,
                                    'end_programmed_date': self.end_programmed_date})
 

        # if odometer_val == 0:
        #     odometer_val = 1

        count_entrada = self.env['mntc.io'].search_count([('workorder_ids','in',self.ids)])

        if count_entrada == 0:
            obj_employee = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
            obj_io = self.env['mntc.io'].search(['&',('vehicle_id','=',self.vehicle_id.id), ('state','=','programmed')])
            io_id = 0

            if obj_io:
                for io in obj_io:
                    if datetime.date(io.scheduled_incoming_date) == datetime.date(self.start_programmed_date):
                        io.write({'workorder_ids': [(4, self.id)]})
                        io_id = io.id
                if not io_id:
                    tmp_obj_io = self.env['mntc.io'].create(
                        {
                            'odometer': self.odometer,
                            'scheduled_incoming_date': self.start_programmed_date,
                            'scheduled_outgoing_date': self.end_programmed_date,
                            'garage_id': self.garage_id.id,
                            'vehicle_id': self.vehicle_id.id,
                            'movil_nro': self.vehicle_id.movil_nro,
                            'location_type': 'location_1',
                            'estimated_time': self.estimated_time,
                            'mntc_request_ids': self.request_id.ids,
                            'state': 'programmed',
                            'workorder_ids': self.ids,
                            'requester_id': obj_employee.id,
                            'company_id': self.env.company.ids,
                        }
                    )

                    io_id = tmp_obj_io.id
            else:
                obj_io.create(
                    {
                        'odometer': self.odometer,
                        'scheduled_incoming_date': self.start_programmed_date,
                        'scheduled_outgoing_date': self.end_programmed_date,
                        'garage_id': self.garage_id.id,
                        'vehicle_id': self.vehicle_id.id,
                        'movil_nro': self.vehicle_id.movil_nro,
                        'location_type': 'location_1',
                        'estimated_time': self.estimated_time,
                        'mntc_request_ids': self.request_id.ids,
                        'state': 'programmed',
                        'workorder_ids': self.ids,
                        'requester_id': obj_employee.id,
                        'company_id': self.env.company.ids,
                    }
                )

                io_id = obj_io.id

            obj_vehicle = self.env['fleet.vehicle'].search([('id','=',self.vehicle_id.id)])
            #obj_vehicle.write({'disponibilidad': 'mantenimiento', 'state_id': 2})

            for request in self.request_id:
                request.write({'mntc_io_id': io_id})

            if io_id:
                self.io_ids = [io_id]

        else:
            obj_io = self.env['mntc.io'].search([('workorder_ids','in',self.ids)])

            if obj_io:
                obj_io.write({
                    'scheduled_incoming_date': self.start_programmed_date,
                    'scheduled_outgoing_date': self.end_programmed_date,
                    'estimated_time': self.estimated_time,
                    'state': 'programmed'
                })



    def validate_wo_and_io_scheduled(self, valid_mntc_io, state):
        workorder_inputs_ids = []
        for mntc_io in valid_mntc_io:
            if state == 'in':
                if self.start_programmed_date <= mntc_io.incoming_date:
                    mntc_io.incoming_date = self.start_programmed_date

                if self.end_programmed_date >= mntc_io.outgoing_date:
                    mntc_io.scheduled_outgoing_date = self.end_programmed_date
            else:
                if self.start_programmed_date <= mntc_io.scheduled_incoming_date:
                    mntc_io.scheduled_incoming_date = self.start_programmed_date

                if self.end_programmed_date >= mntc_io.scheduled_outgoing_date:
                    mntc_io.scheduled_outgoing_date = self.end_programmed_date

            workorder_inputs_ids = self.io_ids.ids
            if not mntc_io.id in workorder_inputs_ids:
                workorder_inputs_ids.append(mntc_io.id)
                self.write({'io_ids':[(6, 0, workorder_inputs_ids)]})
                break


    def mntc_workorder_end(self):
        active_program =True
        repuestos = 0
        repuestos_con_orden = 0

        for task in self.work_task_ids:
            for repuesto in task.repuesto:
                repuestos += 1
                if repuesto.move_line_id:
                    repuestos_con_orden += 1
            
            if not task.component_id or not task.spare_part_type_id or not task.cause_id or not task.action_taken_id:
                raise ValidationError(_("Error! Debe especificar los datos de cierre de cada tarea."))

        if active_program:
            self.state = 'ended'

            is_ok = True

            if not self.work_task_ids:
                raise ValidationError(_("Error! No hay tareas configuradas. Por favor verifique."))

            for task_lines in self.work_task_ids:
                # for inspections in task_lines.executed_inspections_ids:
                #     if inspections.ok or inspections.not_apply:
                #         is_ok = True
                #     else:
                #         is_ok = False
                #         break
                
                if is_ok == False:
                    raise ValidationError(_("Error! Hay inspecciones que aun no tienen una respuesta. Por favor verifique."))

                if not task_lines.start_executed_date:
                    raise ValidationError(_("Error! Debe especificar la fecha de inicio de ejecución de todas las tareas programadas"))     
                if not task_lines.end_executed_date:
                    raise ValidationError(_("Error! Debe especificar la fecha de finalización de ejecución de todas las tareas programadas"))     
                # if not task_lines.spent_time:
                #     raise ValidationError(_("Error! Debe especificar el tiempo asignado en las tareas programadas"))     

                task_lines.state = 'ended'
           
            if self.request_id:
                self.request_id.state = 'ended'

            self.ended_by = self.env.user.id

            if self.work_routine_ids:
                odometer_task = 0
                odometer = 0
                if self.io_ids:
                    for odometer_io in self.io_ids:
                        if  odometer_io.state in ['in']:
                                odometer_task = odometer_io.odometer
                        odometer = odometer_task
                    if not odometer:
                        odometer_counter = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', self.vehicle_id.id)],limit=1)
                        odometer = odometer_counter 

                for routine in self.work_routine_ids:
                    workorder_routines_obj = self.env['mntc.workorder.routines'].search([('routine_id', '=', routine.id),('vehicle_id', '=', self.vehicle_id.id)])

                    if not workorder_routines_obj:
                        vals2 = {
                                'workorder_id': self.id,
                                'routine_id':   routine.id,
                                'vehicle_id':   self.vehicle_id.id,
                                'odometer' :    odometer
                                }   
                        workorder_routines_obj.create(vals2)
                    else:
                        workorder_routines_obj.write({'workorder_id': self.id,
                                                      'odometer': odometer})
        else:
            raise ValidationError(_('Error in configured'+": "+"error you have an active programming"))



    def mntc_workorder_pause(self):
        self.state = 'stopped'
        # if self.program_lines_ids:
        #     active_line = False
        #     for program_line in self.program_lines_ids:
        #         for execution_line in program_line.execution_line_ids:
        #             if not execution_line.end_date:
        #                 active_line = True
        # if not active_line:
        #     self.state = 'stopped'
        # else:
        #     raise ValidationError(_('Error active task'+": "+"Cannot pause work order there is an active task"))


    def mntc_workorder_continue(self):
        io_count = 0

        if self.io_ids:
            for io in self.io_ids:
                if io.state == 'in':
                    io_count += 1

            if io_count == 0:
                raise ValidationError(_("Se debe dar ingreso al vehículo antes de pasar a ejecución la orden. Por favor verifique!"))
        
        self.state = 'in_progress'

        # input_pool = self.env['mntc.io']
        # workorder_inputs_ids = []

        # active_io = False
        # imput_count=0
        # for input in self.io_ids:
        #     if input.state == 'in':
        #         imput_count+=1

        # if imput_count == 0:
        #     input_search = input_pool.search([('vehicle_id','=',self.vehicle_id.id),('state','in',['in'])])
        #     if input_search:
        #         active_io = True
        #         workorder_inputs_ids = self.io_ids.ids
        #         workorder_inputs_ids.append(input_search[0].id)
        #         self.write({'io_ids':[(6, 0, workorder_inputs_ids)]})
        # else:
        #     active_io = True

        # if active_io:
        #     self.state = 'in_progress'
        # else:
        #     raise ValidationError(_('Error in entry'+": "+"you do not have a valid vehicle entry"))


    def mntc_workorder_execution(self):
        self.state = 'in_progress' 
        io_count = 0

        result = []
        if self.io_ids:
            for io in self.io_ids:
                if io.state == 'in':
                    io_count += 1

            if io_count == 0:
                raise ValidationError(_("Se debe dar ingreso al vehículo antes de pasar a ejecución la orden. Por favor verifique!"))

        for tasks in self.work_task_ids:
            if tasks.disciplina_rh:
                for disciplina in tasks.disciplina_rh:
                    disciplina_ejecutada_vals = { 
                            'workforce_type_id': disciplina.workforce_type_id.id,
                            'name': disciplina.name,
                            'code': disciplina.code,
                            'description': disciplina.description,
                            'active': disciplina.active,
                            'task_id': tasks.id,
                            'start_executed_date': disciplina.start_programmed_date,
                            'end_executed_date': disciplina.end_programmed_date,
                            'spent_time': disciplina.programmed_time,
                        }
                    result.append((0,0,disciplina_ejecutada_vals))
                
            else:
                for disciplina in tasks.activity_id.disciplina.workforce_type_id:
                    disciplina_ejecutada_vals = {
                            'workforce_type_id': disciplina.id, 
                            'name': disciplina.name,
                            'code': disciplina.code,
                            'description': disciplina.description,
                            'active': disciplina.active,
                            'task_id': tasks.id,
                        }
                    result.append((0,0,disciplina_ejecutada_vals))
            
            tasks.write({'disciplina_ejecutada_rh': result})
            result = []
            
        
    def mntc_workorder_canceled(self):
        io_state = 0
        if self.observation:
            if self.io_ids:
                for io_id in self.io_ids:
                    if  io_id.state == 'programmed':
                        for workorder_id in io_id.workorder_ids:
                            if  workorder_id.state not in ['ended','canceled']:#'draft',
                                io_state = io_state + 1
                        if  io_state <= 1:
                            io_id.state = 'canceled'

            if self.work_task_ids:
                for work_task_id in  self.work_task_ids:
                    if  work_task_id.state != 'ended':
                        work_task_id.state = 'canceled'

            if self.stock_picking_ids:
                for stock_picking in self.stock_picking_ids:
                    stock_picking.action_cancel()
            
            if self.purchase_order_ids:
                for purchase_order in self.purchase_order_ids:
                    purchase_order.button_cancel()

            self.state = 'canceled'
        else:
            raise ValidationError(_('Error in configured'+": "+"a observation is required"))

    def mntc_questions(self,id_task):
        questions = self.env['mntc.inspections'].search([('id', '=', id_task.inspection_id.id),('inspection_type','=','qualitative')])
        inspection_values_ids = questions.inspection_values_ids
        for variable in inspection_values_ids:
            variable.name
        return inspection_values_ids

    @api.model
    def _get_default_id(self):
        return self.env.ref('big_documents_type.mntc_documents_types_workorder')


    def generate_tasks(self):
        task_pool = self.env['mntc.tasks']
        spare_part_x_task_pool = self.env['mntc.spare.part.x.task']
        executed_inspections_pool = self.env['mntc.executed.inspections']
        mntc_executed_inspections_answer_pool = self.env[ 'mntc.executed.inspections.answer']
        if self.work_routine_ids:
            for task in self.work_task_ids:
                task[0].unlink()
            tasks_ids = self.work_task_ids.ids
            for routine in self.work_routine_ids:
                for activities in routine.activity_ids:
                    if activities.description:
                        description=activities.description
                        tasks_vals = {
                            'name':activities.name,
                            'workorder_id': self.id,
                            'routine_id': routine.id,
                            'activity_id': activities.id,
                            'system_id': activities.system_id.id,
                            'estimated_time': activities.estimated_time,
                            'estimated_time': activities.estimated_time,
                            'process_description': activities.description,
                            'required_technicians': activities.required_technicians,
                        }
                    else :
                       
                        tasks_vals = {
                            'name':activities.name,
                            'workorder_id': self.id,
                            'routine_id': routine.id,
                            'activity_id': activities.id,
                            'system_id': activities.system_id.id,
                            'estimated_time': activities.estimated_time,
                            'estimated_time': activities.estimated_time,
                            'required_technicians': activities.required_technicians,
                        }
                    task_new = task_pool.create(tasks_vals)
                    tasks_ids.append(task_new.id)
                    for spare in task_new.spare_part_ids:
                        spare[0].unlink()
                    spare_ids = task_new.spare_part_ids.ids
                    # for spare_activity in activities.spare_part_type_ids:
                    #     spare_vals = {
                    #         'task_id': task_new.id,
                    #         'spare_part_type_id': spare_activity.id,
                    #         'qty_used': 0,
                    #     }
                    #     spare_new = spare_part_x_task_pool.create(spare_vals)
                    #     spare_ids.append(spare_new.id)
                    for executed in task_new.executed_inspections_ids:
                        executed[0].unlink()                
                    executed_ids = task_new.executed_inspections_ids.ids
                    for inspection in activities.inspections_ids:
                        inspection_vals = {
                            'name': inspection.name,
                            'task_id': task_new.id,
                            'inspection_type': inspection.inspection_type,
                            'sequence': inspection.sequence,
                            'min_value': inspection.min_value,
                            'max_value': inspection.max_value,
                            'inspection_id': inspection.id,
                            'test_uom_id': inspection.uom_id.id,
                            'uom_id': inspection.uom_id.id,
                            'condition': inspection.condition,
                        }
                        executed_inspection_new = executed_inspections_pool.create(inspection_vals)
                        executed_ids.append(executed_inspection_new.id)

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


class stock_picking_multicompany(models.Model):
    _name = 'stock.picking.multicompany'
    _description = 'Inventario multicompañia'

    company_name = fields.Char(string='Company')
    workorder_id = fields.Many2one('mntc.workorder', string='Work order id')
    stock_picking_id = fields.Many2one('stock.picking', string='Stock picking id')
    name = fields.Char(string='Reference')
    placa = fields.Many2one('fleet.vehicle', string='Placa')
    partner_id = fields.Many2one('res.partner', string='Partner')
    owner_id = fields.Many2one('res.partner', string='Owner')
    date = fields.Datetime(string='Date')
    origin = fields.Char(string='Origin')
    state = fields.Selection([
                ('draft', 'Draft'),
                ('cancel', 'Cancelled'),
                ('waiting', 'Waiting Another Operation'),
                ('confirmed', 'Waiting Availability'),
                ('partially_available', 'Partially Available'),
                ('assigned', 'Ready to Transfer'),
                ('done', 'Transferred'),
                ], string='Status')
    id_multicompany = fields.Integer(string='Id Multicompany')
    state_help = fields.Char(string='state help')


class mntc_workorder_routines(models.Model):

    _name = 'mntc.workorder.routines'
    _description = 'Rutinas de la orden de trabajo'
    
    workorder_id = fields.Many2one('mntc.workorder', string='Workorder')
    routine_id = fields.Many2one('mntc.routines', string='Routines')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    odometer = fields.Integer('Odometer')