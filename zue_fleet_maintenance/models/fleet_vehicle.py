from odoo import models, fields, api, _
import time
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import pytz

class fleet_vehicle_documents(models.Model):
    _name = 'fleet.vehicle.documents'
    _description = 'Documentos del vehiculo'

    vehicle_id = fields.Many2one('fleet.vehicle','Vehiculo', ondelete='cascade')
    name = fields.Char('Descripción', required=True)
    expiration_date = fields.Date('Fecha de vencimiento')
    document = fields.Many2one('documents.document', required=True)

    #Acción planificada para realizar recordatorio de expiración de documento
    '''
    today = datetime.datetime.today().date()
    date_next_month = (datetime.datetime.today() + datetime.timedelta(days=30)).date()
    obj_fleet_vehicle = env['fleet.vehicle.documents'].search([('expiration_date','>=',today),('expiration_date','<=',date_next_month)])

    obj_model_fleet = env['ir.model'].search([('model','=','fleet.vehicle')])
    obj_activity_type = env['mail.activity.type'].search([('category','=','reminder')])

    for document in obj_fleet_vehicle:
        if (document.expiration_date - today).days == 30:
            msg = '<p>El documento '+document.name+' del vehiculo '+document.vehicle_id.placa_nro+' esta a 30 días de expirar, Fecha de vencimiento: '+str(document.expiration_date)+'</p>'
            values = {'res_model_id': obj_model_fleet.id,
                            'res_model':'fleet.vehicle',
                            'res_id':document.vehicle_id.id,
                            'res_name':document.vehicle_id.name,
                            'activity_type_id':obj_activity_type.id,
                            'note':msg,
                            'date_deadline':document.expiration_date,
                            'user_id':document.document.owner_id.id}
            env['mail.activity'].create(values)
    '''

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'
 
    x_acquisition_date = fields.Date(string='Fecha de matrícula')
    account_analytic_id = fields.Many2one('account.analytic.account', company_dependent=True, string='Account Analytic', track_visibility='onchange')
    #marca = fields.Many2one('account.analytic.account','Cuenta analítica', required=False, domain="[('type','!=','view')]")
    active_gps = fields.Boolean(string='Active GPS')
    afiliado_id = fields.Many2one('res.partner', 'Afiliado', track_visibility='onchange')
    belong_to = fields.Selection([('owner', 'Owner'), ('rented', 'Rented')], 'Belong to')
    carroceria = fields.Many2one('mntc.carroceria', string='Carrocería', track_visibility='onchange')
    catalog_id = fields.Many2one('mntc.catalog', string='Catalog', compute='get_catalog')
    code_reference = fields.Char(string='Code reference', size=2)
    daily_average = fields.Integer('Daily average', compute='compute_odometer')
    disponibilidad = fields.Selection([('operacion','En Operacion'),('mantenimiento','En Mantenimiento'),('baja','Dado de baja')], 'Disponibilidad', default='operacion')
    gps_number = fields.Integer(string='GPS Number')
    gps_state = fields.Selection([('inactive', 'Inactive'), ('active', 'Active')], 'GPS State')
    in_the_charge_of = fields.Many2one('res.company', string='Asignado a')
    is_rented = fields.Boolean(string="Rented") 
    rented_to = fields.Many2one('res.partner', string='Alquilado por', domain="[('x_type_thirdparty.id','=',3)]")
    message_last_post = fields.Datetime('Last Message Date')
    message_summary = fields.Text('Summary')
    mtto_planes = fields.One2many('vehiculo.mmto.planes', 'vehiculo', 'Plan de mantenimiento', ondelete='cascade')
    mtto_planes_correct = fields.One2many('mtto.correctivo', 'vehiculo', 'Mantenimiento correctivo', ondelete='cascade')
    property_fleet_account_output_categ = fields.Many2one('account.account', 'Gasto vehículo')
    rcc = fields.One2many('vehiculos.rcc', 'vehiculo', 'Rcc')
    rce = fields.One2many('vehiculos.rce', 'vehiculo', 'Rce')
    rendimiento = fields.One2many('vehiculos.rendimiento','vehiculo','Rendimiento')
    rodamiento_rutas = fields.One2many('contratos.rutas','ruta_vehiculo', ondelete='cascade',string='Rutas')
    soat = fields.One2many('vehiculos.soat', 'vehiculo', 'Soat')
    branch_id = fields.Many2one('zue.res.branch', 'Sucursal', track_visibility='onchange')
    tdr = fields.One2many('vehiculos.tdr', 'vehiculo', 'Todo riesgo')
    tecnicomecanica = fields.One2many('vehiculos.tecnicomecanica','vehiculo','Revision tecnicomecanica')
    tope = fields.One2many('vehiculos.tope', 'vehiculo', 'Tarjea operacion')
    documents_ids = fields.One2many('fleet.vehicle.documents', 'vehicle_id', 'Documentos')
    trazabilidad_disponibilida = fields.One2many('vehiculo.trazabilidad.disponibilidad', 'vehiculo','Trazabilidad', ondelte='cascade')
    vehiculo_cilindrada = fields.Integer('Cilindraje')
    vehiculo_fogmaker = fields.Boolean('Fogmaker')
    vehiculo_linea = fields.Many2one('vehiculos.lineas','Linea', domain=[('marca','=','vehiculo_marca')], track_visibility='onchange')
    vehiculo_marca = fields.Many2one('fleet.vehicle.model.brand','Marca vehículo', track_visibility='onchange')
    vehiculo_numero_ejes = fields.Integer('Numero de ejes')
    vehiculo_numero_motor = fields.Char('Numero de motor', size=255)
    vehiculo_numero_serie = fields.Char('Numero de serie', size=255)
    vehiculo_peso_bruto = fields.Integer('Peso Bruto')
    vehiculo_rutas_novedades = fields.One2many('gestion.diaria.despacho.novedades','ruta_vehiculo', ondelete='cascade')
    vehiculo_tipo_carroceria = fields.Char('Tipo de carroceria', size=255)
    movil_nro = fields.Char('No. móvil', help='Número del móvil asignado intenrnamente por la compañía', track_visibility='onchange')
    active = fields.Boolean('Activo')
    placa_nro = fields.Char('No. placa', help='Número de la placa', track_visibility='onchange')
    modelo = fields.Char('Año modelo', help='Número del móvil asignado intenrnamente por la compañía')
    owner_id = fields.Many2one('res.partner', 'Propietario', help='Propietario del vehículo', track_visibility='onchange')
    locator = fields.Char(string='Locatario')
    property_fleet_account_input_categ = fields.Many2one('account.account', string='Ingresos vehículo', help='Cuenta para registrar los ingresos del vehículo')
    service_type_id = fields.Many2one('mntc.services.type', string='Services Type', track_visibility='onchange')
    type_of_service = fields.Selection([('public','Público'),('private','Particular')], 'Type of service')
    contrato = fields.One2many('contratos.contratos', 'vehiculo', 'Contratos')
    fuel_type = fields.Selection(selection_add=[('gnv', 'Gas natural vehicular')])
    last_odometer_ws = fields.Char('Último odómetro')
    assigned_company_id = fields.Many2one('res.company',string='Compañia asignada', track_visibility='onchange')

    _sql_constraints = [
        ('placa_nro', 'UNIQUE (placa_nro)', 'No es posible crear un vehículo con una placa ya existente. Por favor verifique!')
    ]

    @api.model
    def create(self, vals):
        vals['company_id'] = None
        vals['state_id'] = 1
        obj_fleet = super(fleet_vehicle, self).create(vals)

        return obj_fleet
    
    def update_daily_odometer(self,str_date=''):
        if str_date == '':
            tmp_fecha = date.today()
            str_fecha = str(tmp_fecha) + ' 23:00:00'
            fecha_consulta = datetime.strptime(str_fecha, '%Y-%m-%d %H:%M:%S')
        else:
            fecha_consulta = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
            tmp_fecha = fecha_consulta.date()

        for vehicle in self:
            obj_odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', vehicle.id), ('date', '=', tmp_fecha)])

            if not obj_odometer:
                valor_odometro = 0
                valor_odometro = vehicle.get_odometer(fecha_consulta,1)

                if valor_odometro:
                    vehicle.write({'last_odometer_ws': valor_odometro})

            
    def get_odometer(self,date=None,return_odometer=0):
        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'check_vehicle_odometer')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configuraco un web service con el nombre 'check_vehicle_odometer'")) 

        for record in self:
            vehicle_odometer = ''
            placa = ''
            date_str = ''

            if date:
                date_str = date.strftime("%Y-%m-%d %H:%M:%S")  
            else:
                #date = datetime.now().astimezone(pytz.timezone('Etc/GMT+5'))#.replace(hour=0, minute=0, second=0)
                #date = (date+timedelta(days=1))-timedelta(seconds=1)-timedelta(days=1)
                date = datetime.now()-timedelta(hours=6)
                date_str = date.strftime("%Y-%m-%d %H:%M:%S")

            placa = record.placa_nro

            obj_odometer = obj_ws.connection_requests(date_str, placa)

            if 'odometro' in obj_odometer:
                for odometer_list in obj_odometer['odometro']:
                    for odometer in odometer_list:
                        vehicle_odometer = odometer['odometro']

            if vehicle_odometer:
                obj_vehicle_odometer = self.env['fleet.vehicle.odometer']

                if obj_vehicle_odometer.search_count(['&', ('vehicle_id', '=', record.id), ('date', '=', (date.date()))]) <= 0:
                    obj_vehicle_odometer.create({
                        'date': date.date(),
                        'vehicle_id' : record.id,
                        'value' : float(vehicle_odometer),
                        'source' : 'gps'
                    })     

                record.write({'last_odometer_ws': vehicle_odometer})                 

        if return_odometer == 0:
            return True
        else:
            if vehicle_odometer:
                return int(float(vehicle_odometer))
            else:
                return 0
        

    def name_get(self):
        result = []
        for record in self:            
            result.append((record.id, "{}/{}/{}/{} ".format(record.model_id.brand_id.name,record.model_id.name,record.placa_nro,record.movil_nro)))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|','|', '|', ('model_id', operator, name), ('brand_id', operator, name), ('placa_nro', operator, name), ('movil_nro', operator, name)]
        areas_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(areas_ids).name_get()

    def get_catalog(self):
        for vehicle in self:
            catalog_object = self.env['mntc.catalog'].search([('brand_id.id', '=', vehicle.vehiculo_marca.id), ('service_type_id.id', '=', vehicle.service_type_id.id), ('vehiculo_linea_id.id', '=', vehicle.vehiculo_linea.id)], limit=1)

            if catalog_object:
                vehicle.catalog_id = catalog_object.id
            else:
                vehicle.catalog_id = False

    def compute_odometer(self): 
        for vehicle in self:
            valor = 0
            valor_ant = 0
            valorT = 0
            date_ant = None
            days_t = 0

            vehicle_odometer_ids = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', vehicle.id)],order='date desc',limit=3)
            for item in vehicle_odometer_ids:
                valor = valor_ant - item.value

                if not date_ant:
                    date_ant = item.date
                else:
                    days_t += (date_ant - item.date).days
                    date_ant = item.date

                valor_ant = item.value

                if valor > 0:
                    valorT += valor
                else:
                    valorT = 0

            if days_t == 0:
                days_t = 1

            if len(vehicle_odometer_ids) <= 1:
                vehicle.daily_average= abs(valorT)
            else:
                vehicle.daily_average= abs(valorT/days_t)


    def get_fuel_rendimiento(self, cr, uid, ids, field_name, arg, context=None):
        rendimiento = 0
        odometro = 0
        fuel = 0
        res = dict.fromkeys(ids, False)

        fecha_anterior = (datetime.utcnow() - relativedelta(months=+1))
        month_anterior = fecha_anterior.month
        year_actual  =  datetime.utcnow().year

        first_date   =  datetime.datetime.strptime(str(year_actual)+"-"+str(month_anterior)+"-01", '%Y-%m-%d')
        last_date    =  datetime.datetime.strptime(str(year_actual)+"-"+str(month_anterior)+"-"+str(calendar.monthrange(year_actual, month_anterior)[1]),'%Y-%m-%d')

        for record in self.browse(cr,uid,ids,context=context):
            if record.odometer:
                odometer_object_ids = self.pool.get('fleet.vehicle.odometer').search(cr, uid, [('vehicle_id', '=', record.id),('date','>=',first_date),('date','<=',last_date)])
                odometer_object = self.pool.get('fleet.vehicle.odometer').browse(cr, uid, odometer_object_ids, context=context)
                odometro = round(sum([v.value for v  in odometer_object]))
            if record.log_fuel:
                fuel_object_ids = self.pool.get('fleet.vehicle.log.fuel').search(cr, uid, [('vehicle_id', '=', record.id),('date','>=',first_date),('date','<=',last_date)])
                fuel_object = self.pool.get('fleet.vehicle.log.fuel').browse(cr, uid, fuel_object_ids, context=context)
                fuel = round(sum([v.liter for v  in fuel_object]),2)
                _logger.debug("PRUEBAS odoo %s fuel %s fecha ini %s fecha fin %s ", odometro, fuel, first_date, last_date)
                if odometro > 0.0 and fuel > 0.0:
                    rendimiento = odometro / fuel
                    res[record.id] = rendimiento
        return res

    def get_odometro(self):
        last_type = ''
        last_date = ''
        odometro = 0
        odometer_secure = 0
        odometer_stimated = 0
        for record in self:
            if record.odometer:
                odometer_objects = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.id)])
                for odometer in odometer_objects:
                    if odometer.source in ['refuel', 'maintenance_in', 'maintenance_out']:
                        if odometer.date >= last_date:
                            if odometer.value > odometer_secure:
                                last_date = odometer.date
                                odometer_secure = odometer.value
                                last_type = 'secure'
                    else:
                        if odometer.date > last_date:
                            last_date = odometer.date
                            odometer_stimated = odometer.value
                            last_type = 'stimated'
        if last_type:        
            if last_type == 'secure':
                self.odometro_contador = odometer_secure
            else:
                self.odometro_contador = odometer_stimated
        else:
            self.odometro_contador = odometro              

    # def get_odometro(self, cr, uid, ids, field_name, arg, context=None):
    #     odometro = 0
    #     res = dict.fromkeys(ids, False)
    #     for record in self.browse(cr,uid,ids,context=context):
    #         if record.odometer:
    #             odometer_object_ids = self.pool.get('fleet.vehicle.odometer').search(cr, uid, [('vehicle_id', '=', record.id)])
    #             odometer_object = self.pool.get('fleet.vehicle.odometer').browse(cr, uid, odometer_object_ids, context=context)
    #             odometro = sum([v.value for v  in odometer_object])
    #             res[record.id] = round(odometro)
    #     return res

    def get_seguros(self,cr,uid,ids,field_name,arg,context=None):
        ir_fields_obj = self.pool.get('ir.model.fields')
        field_id = ir_fields_obj.search(cr, uid, [('name','=',field_name.replace("_contador","")),('model','=','fleet.vehicle')])
        field_obj = ir_fields_obj.browse(cr, uid, field_id)
        model_obj = self.pool.get(field_obj.relation)
        seguro = model_obj.search(cr, uid, [('vehiculo','=',ids[0]),('vehiculo_poliza_estado','=','vigente')],count=True)
        if seguro:
            return {ids[0]:seguro}
        else:
            return 0
    

    def get_rendimiento(self, cr, uid, ids, field_name, arg, context=None):
        rendimiento = 0
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr,uid,ids,context=context):
            if record.rendimiento:
                rendimiento = sum([v.maxima for v  in record.rendimiento])/len(record.rendimiento)
                res[record.id] = rendimiento
        return res


    def _vehicle_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.placa_nro
        return res

    def dar_baja(self, context=None):
        context = { 'default_vehiculo' : self.id,
                    'default_disponibilidad' : 'baja'}
        return {
                'type': 'ir.actions.act_window',
                'name': 'Movimientos en el vehiculo',
                'view_mode': 'form',
                'res_model': 'vehiculo.trazabilidad.disponibilidad',
                'context' : context,
                'target':'new',
                'nodestroy' : False

                }

    def cancelar_baja(self, context=None):
        context = { 'default_vehiculo' : self.id,
                    'default_disponibilidad' : 'operacion'}
        return {
                'type': 'ir.actions.act_window',
                'name': 'Movimientos en el vehiculo',
                'view_mode': 'form',
                'res_model': 'vehiculo.trazabilidad.disponibilidad',
                'context' : context,
                'target':'new',
                'nodestroy' : False

                }
    
    def traslado_operacion(self, context=None):
        context = { 'default_vehiculo' : self.id,
                    'default_disponibilidad' : 'traslado',
                    'default_sucursal_origen' : self.branch_id}
        return {
                'type': 'ir.actions.act_window',
                'name': 'Traslado de Operación',
                'view_mode': 'form',
                'res_model': 'vehiculo.trazabilidad.disponibilidad',
                'context' : context,
                'target':'new'
                }

class vehiculo_trazabilidad_disponibilidad(models.Model):
    _name = 'vehiculo.trazabilidad.disponibilidad'
    _description ='Modelo para la verificacion de los movimientos del vehiculo'
    
    disponibilidad = fields.Selection([('operacion','En Operacion'),('mantenimiento','En Mantenimiento'),('baja','Dado de baja'),('traslado','Traslado de Operación')], 'Disponibilidad', readonly=True)
    vehiculo = fields.Many2one('fleet.vehicle', 'Vehiculo', required=True, readonly=True)
    sucursal_origen = fields.Many2one('zue.res.branch','Sucursal origen')
    sucursal = fields.Many2one('zue.res.branch','Sucursal destino')
    razon = fields.Char('Razon del movimiento')
    io_id = fields.Many2one('mntc.io', 'Entrada/Salida')

    @api.model
    def create(self, vals):
        obj_trazabilidad = super(vehiculo_trazabilidad_disponibilidad, self).create(vals)
        
        if obj_trazabilidad.disponibilidad == 'operacion':
            vehicle_object = self.env['fleet.vehicle'].search([('id', '=', obj_trazabilidad.vehiculo.id),('active','=',False)])
        else:
            vehicle_object = self.env['fleet.vehicle'].search([('id', '=', obj_trazabilidad.vehiculo.id)])

        if obj_trazabilidad.disponibilidad == 'traslado':
            vehicle_object.write({'branch_id' : obj_trazabilidad.sucursal})
        
        if obj_trazabilidad.disponibilidad == 'baja':
            vehicle_object.write({'disponibilidad' : obj_trazabilidad.disponibilidad,
                                    'state_id': 3,
                                    'active' : False})

        if obj_trazabilidad.disponibilidad == 'operacion':
            vehicle_object.write({'disponibilidad' : obj_trazabilidad.disponibilidad,
                                    'state_id': 1,
                                    'active' : True})

        return obj_trazabilidad


class vehiculo_mmto_planes(models.Model):
    _name = 'vehiculo.mmto.planes'
    _description = 'Planes vehículo'
    
    vehiculo = fields.Many2one('fleet.vehicle', 'Vehiculo', required=True)
    name = fields.Char("Intervalo de intervension", size=50)
    rutines = fields.Char('Rutinas', size=50)
    costo_plan = fields.Float('Costo Total')
    estado = fields.Selection([('noaplicado','No aplicado'),('aplicado','Aplicado'),('proximo','Proximo a aplicarse')],'Plan cumplido')
    notificado = fields.Boolean('Notificado')
    autorizado = fields.Boolean('Autorizado')
    orden_mantenimiento = fields.Char('Orden de mantenimiento', size=250)
    autorizado_por = fields.Char('Autorizado por', size=250)
    fecha_prevista = fields.Date('Plazo de ejecucion')
    
    def aplicar_mmto(self, cr, uid, ids, context=None):
        mtto_obj = self.browse(cr, uid, ids, context=context)
        stock_picking = self.pool.get('stock.picking')
        ids_stock = []
        for mtto in mtto_obj:
            orden_mtto = mtto.orden_mantenimiento
            stock_picking_ids = stock_picking.search(cr, uid, [('origin','=',orden_mtto)], context=context)
            stock_picking.do_transfer( cr, uid, stock_picking_ids, context=None)
            ids_stock.append(stock_picking_ids)
            self.write(cr, uid, mtto.id, {'estado':'aplicado'}, context=context)
            try:
                notificacion_ids = self.pool.get('notificaciones.opciones').search(cr, uid,[('flujo','=','odometro')],context=context)
                notificacion_obj = self.pool.get('notificaciones.opciones').browse(cr, uid, notificacion_ids, context=context)
                usuarios = [i.email for i in notificacion_obj]
                msg  = "LA ORDEN %s FUE PROCESADA " % orden_mtto
                mail_to_users = self.pool.get('res.partner').search(cr, uid, [('email','in',usuarios)])
                post_vars = {'subject': "SE HA DESPACHADO EL MATERIAL PARA LA ORDEN DEL PLAN DE MANTENIMIENTO",'body': msg,'partner_ids': mail_to_users}
                thread_pool = self.pool.get('mail.thread')
                thread_pool.message_post(cr, uid, False,type="notification",subtype="mt_comment",context=None,**post_vars)
            except Exception as Error:
                _logger.debug("OCURRIO UN ERROR EN aplicar_mmto %s", Error)

        context = dict(context or {}, active_ids=ids_stock)
        return self.pool.get("report").get_action(cr, uid, ids_stock, 'stock.report_picking', context=context)

class mtto_correctivo(models.Model):
    _name = 'mtto.correctivo'
    _description = 'Mantenimiento correctivo para los vehiculos'

    vehiculo = fields.Many2one('fleet.vehicle', 'Vehiculo', required=True)
    fecha = fields.Date('Fecha ejecucion', required=True)
    producto_id = fields.Many2one('product.template', 'Producto sistema')
    producto_historico = fields.Char('Producto reportado')
    producto_type = fields.Selection([('product','Almacenable'),('consu','Consumible'),('service','Service')], 'Tipo producto')
    producto_categ = fields.Many2one('product.category','Categoria')
    account_analytic = fields.Many2one('account.analytic.account', 'Cuenta analitica')
    documento_origen = fields.Char('Documento origen')
    qty = fields.Float('Cantidad', required=True)
    cost = fields.Float('Costo unitario')
    observaciones = fields.Text('Observaciones')
    valor_total = fields.Float('Costo total')

class vehiculos_rcc(models.Model):
    _name = "vehiculos.rcc"
    _description = 'Seguro de RCC de vehiculo'

    vehiculo = fields.Many2one('fleet.vehicle','Vehiculo', ondelete='cascade')
    vehiculo_numero_poliza = fields.Char('Numero de poliza', size=50)
    vehiculo_entidad_expedicion = fields.Char('Compañia aseguradora',size=50)
    vehiculo_fecha_expedicion = fields.Date('Fecha de expedicion')
    vehiculo_fecha_vigencia_inicio = fields.Date('Fecha inicio de vigencia')
    vehiculo_fecha_vigencia_final = fields.Date('Fecha final de vigencia')
    vehiculo_cobertura = fields.Integer('Cobertura SMLV')
    vehiculo_valor_prima_anual = fields.Float('Valor prima anual')
    vehiculo_poliza_estado = fields.Selection([('vigente','Vigente'),('proxima','Proxima'),('vencida','Vencida')],"Estado de poliza")
    notificado = fields.Boolean('Notificado')

class vehiculos_rce(models.Model):
    _name = "vehiculos.rce"
    _description = 'Seguro RCE de vehiculo'
    
    vehiculo = fields.Many2one('fleet.vehicle','Vehiculo', ondelete='cascade')
    vehiculo_numero_poliza = fields.Char('Numero de poliza', size=50)
    vehiculo_entidad_expedicion = fields.Char('Compañia aseguradora',size=50)
    vehiculo_fecha_expedicion = fields.Date('Fecha de expedicion')
    vehiculo_fecha_vigencia_inicio = fields.Date('Fecha inicio de vigencia')
    vehiculo_fecha_vigencia_final = fields.Date('Fecha final de vigencia')
    vehiculo_cobertura = fields.Integer('Cobertura SMLV')
    vehiculo_valor_prima_anual = fields.Float('Valor prima anual')
    vehiculo_poliza_estado = fields.Selection([('vigente','Vigente'),('proxima','Proxima'),('vencida','Vencida')],"Estado de poliza")
    notificado = fields.Boolean('Notificado')
    
class vehiculos_rendimiento(models.Model):
    _name ='vehiculos.rendimiento'
    _description = 'Rendimiento de vehiculos'
    
    vehiculo = fields.Many2one('fleet.vehicle', 'Vehiculo', required=True)
    fecha = fields.Date('Fecha')
    hora = fields.Char('Hora',size=50)
    latitud = fields.Char('Lat', size=250)
    longitud = fields.Char('Lon', size=250)
    ubicacion = fields.Char('Ubicacion', size=250)
    ciudad = fields.Char('Ciudad', size=250)
    limite = fields.Integer('Limite')
    maxima = fields.Integer('Maxima')
    tiempo_maxima = fields.Integer('Tiempo de maxima')
    notificado = fields.Boolean('Notificado')
    conductor = fields.Many2one("hr.employee", 'Conductor')
    
class vehiculos_soat(models.Model):
    _name ='vehiculos.soat'
    _description = 'Gestion de soat de veliculo'
    
    vehiculo = fields.Many2one('fleet.vehicle','Vehiculo', ondelete='cascade')
    vehiculo_numero_poliza = fields.Char('Numero de poliza', size=50)
    vehiculo_fecha_expedicion = fields.Date('Fecha de expedicion')
    vehiculo_fecha_vigencia_inicio = fields.Date('Fecha inicio de vigencia')
    vehiculo_fecha_vigencia_final = fields.Date('Fecha final de vigencia')
    vehiculo_entidad_expedicion = fields.Char('Entidad que exipide',size=50)
    vehiculo_poliza_estado = fields.Selection([('vigente','Vigente'),('proxima','Proxima'),('vencida','Vencida')],"Estado de poliza")
    notificado = fields.Boolean('Notificado')
    vehiculo_total_apagar = fields.Float('Total a pagar')

class vehiculos_tdr(models.Model):
    _name = "vehiculos.tdr"
    _description = 'Seguros todo riesgo'
    
    vehiculo = fields.Many2one('fleet.vehicle','Vehiculo', ondelete='cascade')
    vehiculo_numero_poliza = fields.Char('Numero de poliza', size=50)
    vehiculo_entidad_expedicion = fields.Char('Compañia aseguradora',size=50)
    vehiculo_fecha_expedicion = fields.Date('Fecha de expedicion')
    vehiculo_fecha_vigencia_inicio = fields.Date('Fecha inicio de vigencia')
    vehiculo_fecha_vigencia_final = fields.Date('Fecha final de vigencia')
    vehiculo_cobertura = fields.Integer('Cobertura SMLV')
    vehiculo_deducible = fields.Float('Valor deducible')
    vehiculo_valor_prima_anual = fields.Float('Valor prima anual')
    vehiculo_poliza_estado = fields.Selection([('vigente','Vigente'),('proxima','Proxima'),('vencida','Vencida')],"Estado de poliza")
    notificado = fields.Boolean('Notificado')

class vehiculos_tope(models.Model):
    _name = "vehiculos.tope"
    _description = 'Tarjetas de operacion'
    
    vehiculo = fields.Many2one('fleet.vehicle','Vehiculo', ondelete='cascade')
    vehiculo_razon_social = fields.Char("Razon social", size=255)
    vehiculo_sede = fields.Char("Entidad territorial", size=255)
    vehiculo_numero_tarjeta_operacion = fields.Char("Numero tarjeta", size=255)
    vehiculo_radio_operacion = fields.Char("Radio operacion", size=255)
    vehiculo_fecha_expedicion = fields.Date('Fecha de expedicion')
    vehiculo_fecha_vencimiento = fields.Date('Fecha de vencimiento')
    vehiculo_poliza_estado = fields.Selection([('vigente','Vigente'),('proxima','Proxima'),('vencida','Vencida')],"Estado de tarjeta")
    notificado = fields.Boolean('Notificado')

class vehiculos_tecnicomecanica(models.Model):
    _name = "vehiculos.tecnicomecanica"
    _description = 'Revision tecnico mecanica'
    
    vehiculo = fields.Many2one('fleet.vehicle','Vehiculo', ondelete='cascade')
    vehiculo_numero = fields.Char("Numero de certificado", size=255)
    vehiculo_fecha_expedicion = fields.Date('Fecha de expedicion')
    vehiculo_fecha_vencimiento = fields.Date('Fecha de vencimiento')
    vehiculo_poliza_estado = fields.Selection([('vigente','Vigente'),('proxima','Proxima'),('vencida','Vencida')],"Estado")
    notificado = fields.Boolean('Notificado')

class fleet_vehicle_odometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    source = fields.Selection(selection=[('gps', 'GPS'), ('route', 'Ruta'), ('cost', 'Costo'), ('maintenance_in', 'Entrada a mantenimiento'), ('maintenance_out', 'Salida mantenimiento')], string='Fuente de datos')

class mntc_carroceria(models.Model):
    _name = "mntc.carroceria"
    _description = 'Carroceria de vehiculo'

    name = fields.Char('Nombre', size=50)