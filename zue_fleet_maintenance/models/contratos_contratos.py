from odoo import models, fields, api, _
import time
import datetime
from odoo.exceptions import UserError, ValidationError

class contratos_contratos(models.Model): 
    _name = 'contratos.contratos'
    _description = 'Contratos existentes'

    vehiculo = fields.Many2one('fleet.vehicle','Vehículo')
    name = fields.Many2one('res.partner', 'Entidad contratante',required=True)
    contrato_analitico = fields.Many2one('account.analytic.account','Contrato relacionado', required=True)
    contrato_analitico_referencia = fields.Char(related='contrato_analitico.code', string='Referencia' )
    vigencia = fields.Integer('Vigencia')
    valor_contrato = fields.Float('Valor contrato')
    ruta = fields.One2many('contratos.rutas', 'contrato', 'Rutas')
    programacion = fields.One2many('gestion.diaria.programacion', 'contrato', 'Programacion')
    cantidad_programadas = fields.Integer('Total Programadas',compute='get_programadas')
    cantidad_novedades = fields.Integer(compute='get_novedades', string='Total Novedades')
    cantidad_vehiculos = fields.Integer(compute='get_cantidad', string='Total vehiculos')
    cantidad_rutas = fields.Integer(compute='get_cantidad', string='Total rutas')
    cantidad_conductores = fields.Integer(compute='get_cantidad', string='Total conductores')
    cantidad_mantenimiento = fields.Integer(compute='get_cantidad', string='Total mantenimiento')
    cantidad_despachada = fields.Integer(compute='get_cantidad', string='Total despachadas')
    impuestos_contrato = fields.Many2many('account.tax', 'contrato_product_tax', 'contrato_id', 'tax_id', 'Impuestos')
    cuenta_ingresos = fields.Many2one('account.account','Cuenta de ingresos', required=True)
    cuenta_gastos = fields.Many2one('account.account','Cuenta de gastos', required=True)
    facturacion_unica = fields.Boolean('Unico concepto de facturacion')
    facturacion_unica_producto = fields.Many2one('product.template','Concepto unico')
    company_id = fields.Many2one('res.company','Empresa', required=True)
    responsable = fields.Many2one('res.partner', 'Responsable',required=True)
    tipo_sociedad = fields.Selection([('convenio','CONVENIO'),('consorcio','CONSORCIO'),('union_temporal','UNION TEMPORAL')],'Tipo socio')
    empresa_socia = fields.Many2one('res.partner', 'Empresa socio')
    objeto_contrato = fields.Char('Objeto del contrato', size=255,required=True)
    direccion_operaciones = fields.Many2one('hr.employee','Director de operaciones')
    responsable_mtto = fields.Many2one('hr.employee','Responsable mantenimiento')
    ubicacion_salida_almacen = fields.Many2one('stock.location','Ubicacion de salida almacen')
    codigo_contrato = fields.Char('Codigo contrato')

    @api.depends('cantidad_programadas')
    def get_programadas(self, cr, uid, ids, field_name, arg, context=None):
        hoy = datetime.utcnow()
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr,uid,ids,context=context):
            total = 0.0
            programacion = 0.0
            despachados = 0.0
            if record.programacion:
                for programadas in record.programacion:
                    if hoy == programadas.fecha_inicial:
                        programacion += 1
                    if hoy == programadas.fecha_inicial and programadas.estado == 'despachada':
                        despachados += 1
                if programacion != 0 and despachados != 0:
                    total = float((despachados * 100 ) / programacion)

                res[record.id] = total
        return res

    @api.depends('cantidad_novedades')
    def get_novedades(self, cr, uid, ids, field_name, arg, context=None):
        hoy = datetime.utcnow()
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr,uid,ids,context=context):
            programacion = 0.0
            despachados = 0.0
            total = 0.0
            if record.programacion:
                for programadas in record.programacion:
                    if hoy == programadas.fecha_inicial:
                        programacion += 1
                    if hoy == programadas.fecha_inicial and programadas.estado == 'despachada_novedad':
                        despachados += 1
                    if programacion != 0 and despachados != 0:
                        total = float((despachados * 100 ) / programacion)
                res[record.id] = total
        return res
    
    @api.depends('cantidad_vehiculos','cantidad_rutas','cantidad_conductores','cantidad_mantenimiento','cantidad_despachada')
    def get_cantidad(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, False)
        total = 0
        for record in self.browse(cr,uid,ids,context=context):
            if record.ruta:
                if field_name == 'cantidad_vehiculos':
                    total = len(set([i.ruta_vehiculo for i in record.ruta]))
                    res[record.id] = int(total)
                if field_name == 'cantidad_rutas':
                    total = len(set([i for i in record.ruta]))
                    res[record.id] = int(total)
                if field_name == 'cantidad_conductores':
                    total = len(set([i.ruta_conductor for i in record.ruta]))
                    res[record.id] = int(total)
                if field_name == 'cantidad_mantenimiento':
                    vehiculos = list(set([i.ruta_vehiculo for i in record.ruta]))
                    if vehiculos:
                        for vehiculo in vehiculos:
                            if vehiculo.mtto_planes:
                                for mmto in vehiculo.mtto_planes:
                                    if mmto.estado == 'proximo' and mmto.autorizado == True:
                                        total += 1
                        res[record.id] = int(total)
            if record.programacion:
                if field_name == 'cantidad_despachada':
                    for programacion in record.programacion:
                        if programacion.estado in ['despachada','despachada_novedad'] and programacion.facturado == False:
                            total += 1
                    res[record.id] = int(total)
        return res                

    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        record_name=self.browse(cr,uid,ids,context)
        for object_contract in record_name:
            if object_contract.name:
                nombre_contrato = str(object_contract.name.name) + " - " + str(object_contract.contrato_analitico_referencia)
                res.append((object_contract.id,nombre_contrato))
        return res

    def write(self, cr, uid, ids, data, context=None):
        object_contrato = self.browse(cr, uid, ids, context=context)
        product_category_obj = self.pool.get('product.category')
        product_product_obj = self.pool.get('product.template')
        cliente_name = object_contrato.name.name
        category_id = product_category_obj.search(cr, uid, [('name','=','SERVICIOS %s' % cliente_name)],context=context)
        product_lists_ids = product_product_obj.search(cr, uid, [('categ_id','in',category_id)],context=context)
        if 'cuenta_ingresos' in data:
            '''Si se realiza cambio en la cuenta de ingresos se realiza actualizacion'''
            '''Actualizamos la categoria'''
            product_category_obj.write(cr, 1, category_id, {'property_account_income_categ':data.get('cuenta_ingresos')},context=context)
            '''Actualizamos el producto'''
            for prod_account_incoming in product_lists_ids:
                product_product_obj.write(cr, 1, prod_account_incoming, {'property_account_income':data.get('cuenta_ingresos')},context=context)
        if 'cuenta_gastos' in data:
            '''Si se realiza cambio en la cuenta de gasto se realiza la actualizacion'''
            '''Actualizamos la categoria'''
            product_category_obj.write(cr, 1, category_id, {'property_account_income_categ':data.get('cuenta_gastos')},context=context)
            '''Actualizamos el producto'''
            for prod_account_incoming in product_lists_ids:
                product_product_obj.write(cr, 1, prod_account_incoming, {'property_account_income':data.get('cuenta_gastos')},context=context)
        if 'impuestos_contrato' in data:
            '''Se se realiza cambio en los impuestos se realiza la actualizacion'''
            '''En el producto'''
            for prod_account_incoming in product_lists_ids:
                product_product_obj.write(cr, 1, prod_account_incoming, {'taxes_id':data.get('impuestos_contrato')})
        return super(contratos,self).write(cr, 1, ids, data, context=context)

    def create(self, cr, uid, data, context=None):
        res = super(contratos, self).create(cr, uid, data,context=context)
        '''Definimos las cuentas de ingreso y egreso'''
        cuenta_ingresos = data['cuenta_ingresos']
        cuenta_gastos = data['cuenta_gastos']
        '''Definimos los datos del cliente'''
        nombre_cliente = self.pool.get('res.partner').browse(cr, uid, [data['name']]).name
        '''Validamos si existe la categoria servicios clientes'''
        product_category_obj = self.pool.get('product.category')
        product_category = product_category_obj.search(cr, uid, [('name','=','SERVICIOS CLIENTES')])
        '''Validamos que las cuentas de ingresos y egresos existan'''
        ingresos = self.pool.get('account.account').search(cr, uid, [('id','=',cuenta_ingresos)])
        egresos = self.pool.get('account.account').search(cr, uid, [('id','=',cuenta_gastos)])
        if ingresos and egresos:
            ingresos = ingresos[0]
            egresos = egresos[0]
        else:
            raise ValidationError(_('Error de cuentas', 'Verifique que la cuenta %s de ingreso y la cuenta %s de egreso existan!' % (cuenta_ingresos, cuenta_gastos)))
            return True

        if not product_category:
            '''Si no existe creamos la categoria de productos SERVICIOS CLIENTES'''
            data_create = {'name':'SERVICIOS CLIENTES',
                           'property_account_income_categ':ingresos,
                           'property_account_expense_categ':egresos,
                           }
            id_categoria = product_category_obj.create(cr, uid, data_create)
            '''Creamos la categoria del cliente'''
            data_create_cliente = {'name':'SERVICIOS %s' % nombre_cliente,
                                   'property_account_income_categ':ingresos,
                                   'property_account_expense_categ':egresos,
                                   'parent_id':id_categoria}
            product_category_obj.create(cr, 1, data_create_cliente)
        else:
            '''Si existe creamos la categoria del nombre del contrato'''
            '''Extraemos la categoria del cliente'''
            product_categoria_cliente = product_category_obj.search(cr, uid, [('name','=','SERVICIOS %s' % nombre_cliente)])
            if not product_categoria_cliente:
                '''Si no existe la creamos'''
                data_create_cliente = {'name':'SERVICIOS %s' % nombre_cliente,
                                       'property_account_income_categ':ingresos,
                                       'property_account_expense_categ':egresos,
                                       'parent_id':product_category[0]}
                product_category_obj.create(cr, 1, data_create_cliente)
        return res

    def setResponsable(self, cr, uid, ids, costumer,context=None):
        if costumer:
            partner = self.pool.get('res.partner').browse(cr, uid, [costumer],context=context)
            if partner.is_company:
                if not partner.child_ids:
                    raise ValidationError(_('Cliente sin contactos!', 'El cliente seleccionado no tiene contactos asignados, no se puede asignar el campo responsable requerido para el FUEC!'))
                    return True
            else:
                return {'value':{'responsable':costumer}}

    def setUniqueProduct(self, cr, uid, ids, idContratante, context=None):
        obj_partner = self.pool.get('res.partner')
        obj_category = self.pool.get('product.category')
        obj_product_template = self.pool.get('product.template')
        if idContratante:
            entidad_nombre = obj_partner.browse(cr, uid, idContratante, context=context).name
            contrato_name = "SERVICIO DE TRANSPORTE TERRESTRE ESPECIAL DE PASAJEROS"
            #categoria_id   = obj_category.search(cr, uid, [('name','=',contrato_name)],context=context)
            productos_ids  = obj_product_template.search(cr, uid, [('name','=',contrato_name)],context=context)
            if productos_ids:
                return {'domain':{'facturacion_unica_producto':[('id','in',productos_ids)]}}
            else:
                raise ValidationError(_('Error de usuario','Seleccione primero la entidad contratante!'))
        else:
            raise ValidationError(_('Error de usuario','Seleccione primero la entidad contratante!'))
        return {'value':{'facturacion_unica_producto':[]}}

    def validar_contrato(self,cr, uid, ids, contrato, context=None):
        from dateutil import relativedelta as rdelta
        if contrato:
            contrato = self.pool.get('account.analytic.account').browse(cr, uid, contrato, context=context)
            if not contrato.date:
                return {'value':{'contrato_analitico':''},'warning':{'title':'Error!','message':"El contrato no tiene fecha de finalizacion! requerida para fuec!"}}
            if not contrato.date_start:
                return {'value':{'contrato_analitico':''},'warning':{'title':'Error!','message':"El contrato no tiene fecha de inicio! requerida para fuec!"}}
            if not contrato.amount_max:
                return {'value':{'contrato_analitico':''},'warning':{'title':'Error!','message':"El contrato no tiene precio previsto!"}}
            if not contrato.description:
                return {'value':{'contrato_analitico':''},'warning':{'title':'Error!','message':"El contrato no tiene plazos y condiciones! requerida para el fuec!"}}

            else:
                costo_total = contrato.amount_max
                d1 = contrato.date_start
                d2 = contrato.date
                rd = rdelta.relativedelta(d2,d1)
                contract_time = (rd.years * 12) + rd.months
                objeto_contrato = contrato.description
                return {'value':{'valor_contrato':costo_total,'vigencia':contract_time,'objeto_contrato':objeto_contrato}}

        return True

