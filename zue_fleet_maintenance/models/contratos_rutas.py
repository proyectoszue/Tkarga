from odoo import models, fields, api, _
import time
import datetime
from odoo.exceptions import UserError, ValidationError

class contratos_rutas(models.Model):
    _name = 'contratos.rutas'
    _description = 'Rutas para el contrato'
    
    contrato = fields.Many2one('contratos.contratos','Contrato', ondelete='cascade')
    contrato_analitico_sucursal = fields.Many2one('zue.res.branch', related='contrato', string='Sucursal')
    ruta_dia = fields.Selection([('Lunes','Lunes'),('Martes','Martes'),('Miercoles','Miercoles'),('Jueves','Jueves'),('Viernes','Viernes'),('Sabado','Sabado'),('Domingo','Domingo')],'Dia inicial')
    ruta_dia_final = fields.Selection([('Lunes','Lunes'),('Martes','Martes'),('Miercoles','Miercoles'),('Jueves','Jueves'),('Viernes','Viernes'),('Sabado','Sabado'),('Domingo','Domingo')],'Dia final')
    ruta_numero = fields.Integer('Numero',required=True)
    ruta_conductor = fields.Many2one("hr.employee", 'Conductor',required=True)
    ruta_vehiculo = fields.Many2one("fleet.vehicle", 'Vehiculo', required=True)
    ruta_hora_salida = fields.Many2one('contratos.rutas.horas','Salida',required=True)
    ruta_hora_llegada = fields.Many2one('contratos.rutas.horas','Llegada',required=True)
    ruta_ciudad_origen = fields.Char('Origen',size=250,required=True)
    ruta_ciudad_destino = fields.Char('Destino',size=250,required=True)
    ruta_kilometros = fields.Integer('Distancia',required=True)
    ruta_via = fields.Char('Via', size=250)
    ruta_costo = fields.Float('Costo unitario',required=True)
    ruta_costo_total = fields.Float('Costo total')
    #contrato_analitico_estado = fields.Char(related='contrato', size=16, string='Estado' )
    contrato_analitico_estado = fields.Char('Estado', size=16)
    
    def copy(self, cr, uid, data,default=None,context=None):
        datos = self.browse(cr, uid,data, context=context)
        if len(datos) == 1:
            last_ruta_numero = max(self.search(cr, uid, [('contrato','=',datos.contrato.id)],context=context))
            last_ruta_numero_obj = self.browse(cr, uid, last_ruta_numero,context=context)
            contrato             = datos.contrato.id
            ruta_dia             = datos.ruta_dia
            ruta_dia_final       = datos.ruta_dia_final
            ruta_numero          = last_ruta_numero_obj.ruta_numero + 1
            conductor            = datos.ruta_conductor.id
            ruta_vehiculo        = datos.ruta_vehiculo.id
            ruta_hora_salida     = last_ruta_numero_obj.ruta_hora_llegada.id + 2
            ruta_ciudad_origen   = last_ruta_numero_obj.ruta_ciudad_destino
            ruta_ciudad_destino  = last_ruta_numero_obj.ruta_ciudad_origen
            ruta_kilometros      = datos.ruta_kilometros
            ruta_via             = datos.ruta_via
            costo                = datos.ruta_costo
            ruta_hora_llegada_dict    = self.validar_distancias(cr, uid, [contrato], ruta_dia, ruta_kilometros, ruta_hora_salida, None, ruta_vehiculo,ruta_ciudad_origen,ruta_ciudad_destino,ruta_numero)
            ruta_hora_llegada    = ruta_hora_llegada_dict.get('value').get('ruta_hora_llegada')
            default = { 'contrato':contrato,
                        'ruta_dia':ruta_dia,
                        'ruta_dia_final':ruta_dia_final,
                        'ruta_numero':ruta_numero,
                        'ruta_conductor':conductor,
                        'ruta_vehiculo':ruta_vehiculo,
                        'ruta_hora_salida':ruta_hora_salida,
                        'ruta_hora_llegada':ruta_hora_llegada,
                        'ruta_ciudad_origen':ruta_ciudad_origen,
                        'ruta_ciudad_destino':ruta_ciudad_destino,
                        'ruta_kilometros':ruta_kilometros,
                        'ruta_via':ruta_via,
                        'ruta_costo':costo
                        }
            super(contratos_rutas, self).copy(cr,uid, data[0], default=default, context=context)
        else:
            raise ValidationError(_('Error de duplicacion', 'Solo puede seleccionar una ruta para copiar!'))
        return {}

    def write(self, cr, uid, ids, data, context=None):
        product_product_obj = self.pool.get('product.template')
        obj_contrato = self.browse(cr, uid, ids, context=context)
        cliente_name = obj_contrato.contrato.name.name
        dia          = obj_contrato.ruta_dia
        dia_final    = obj_contrato.ruta_dia_final
        ruta_numero  = obj_contrato.ruta_numero
        producto_name = '%s %s a %s RUTA %s' % (cliente_name.upper(),dia.upper(),dia_final.upper(),ruta_numero)
        product_id   = product_product_obj.search(cr, uid, [('name','=',producto_name)],context=context)
        if 'ruta_costo' in data:
            product_product_obj.write(cr, 1, product_id, {'list_price':data.get('ruta_costo')},context=context)
        if 'ruta_dia' in data and 'ruta_dia_final' in data:
            dia = data.get('ruta_dia')
            dia_final = data.get('ruta_dia_final')
            producto_name = '%s %s a %s RUTA %s' % (cliente_name.upper(),dia.upper(),dia_final.upper(),ruta_numero)
            product_product_obj.write(cr, 1, product_id, {'name':producto_name,'default_code':producto_name},context=context)
        if 'ruta_dia' in data and not 'ruta_dia_final' in data:
            dia = data.get('ruta_dia')
            producto_name = '%s %s a %s RUTA %s' % (cliente_name.upper(),dia.upper(),dia_final.upper(),ruta_numero)
            product_product_obj.write(cr, 1, product_id, {'name':producto_name,'default_code':producto_name},context=context)
        if not 'ruta_dia' in data and 'ruta_dia_final' in data:
            dia_final = data.get('ruta_dia_final')
            producto_name = '%s %s a %s RUTA %s' % (cliente_name.upper(),dia.upper(),dia_final.upper(),ruta_numero)
            product_product_obj.write(cr, 1, product_id, {'name':producto_name,'default_code':producto_name},context=context)
        return super(contratos_rutas, self).write(cr, uid, ids, data, context=context)

    def unlink(self, cr, uid, ids, context=None):
        obj_invoice_line = self.pool.get('account.move.line')
        product_product_obj = self.pool.get('product.product')
        if ids:
            for id_r in ids:
                obj_rutas    = self.browse(cr, uid, id_r, context=context)
                cliente_name = obj_rutas.contrato.name.name
                dia          = obj_rutas.ruta_dia
                dia_final    = obj_rutas.ruta_dia_final
                ruta_numero  = obj_rutas.ruta_numero
                producto_name = '%s %s a %s RUTA %s' % (cliente_name.upper(),dia.upper(),dia_final.upper(),ruta_numero)
                product_id   = product_product_obj.search(cr, uid, [('name','=',producto_name)],context=context)
                if product_id:
                    check_invoice = obj_invoice_line.search(cr, uid, [('product_id','in',product_id)],context=context)
                    if len(check_invoice) <= 0:
                        product_product_obj.unlink(cr, 1, product_id,context=context)
                        super(contratos_rutas, self).unlink(cr, uid, id_r, context=context)
                    else:
                        raise ValidationError(_('Error de eliminacion', 'No se puede borrar la ruta, esta cuenta con facturacion asociada!'))
                else:
                    super(contratos_rutas, self).unlink(cr, uid, id_r, context=context)
        else:
            raise ValidationError(_('Error de eliminacion', 'Debe seleccionar al menos 1 registro para borrar!'))
        return True


    def create(self, cr, uid, data, context=None):
        if data:
            costo =  data['ruta_costo']
            '''Validamos que el costo de la ruta sea mayor a 0'''
            if costo > 0:
                '''Si el costo esta correcto creamos producto'''
                dia = data['ruta_dia']
                dia_final = data['ruta_dia_final']
                contrato = data['contrato']
                ruta_numero = data['ruta_numero']
                costo_total = data['ruta_costo_total']
                '''definimos los objetos de consulta'''
                obj_categoria = self.pool.get('product.category')
                obj_contrato = self.pool.get('contratos.contratos').browse(cr, uid, contrato)
                obj_product = self.pool.get('product.template')
                '''extraemos el nombre del contrato'''
                cliente_name = obj_contrato.name.name
                facturacion_concepto = obj_contrato.facturacion_unica
                '''extraemos los impuestos aplicados al contrato para el porducto'''
                contrato_impuestos = [impuesto.id for impuesto in obj_contrato.impuestos_contrato]
                '''definimos el nombre del producto'''
                producto_name = '%s %s a %s RUTA %s' % (cliente_name.upper(),dia.upper(),dia_final.upper(),ruta_numero)
                '''Extraemos categoria de producto para el cliente'''
                categoria_contrato = obj_categoria.search(cr, uid, [('name','=','SERVICIOS %s' % cliente_name)])
                '''Extraemos la informacion adicional de ingresos y egresos de la categoria padre'''
                categoria_br = obj_categoria.browse(cr, uid, categoria_contrato)
                '''Validamos si existe el costo total de la ruta'''
                if costo_total == 0 or not costo_total:
                    costo_total_ruta  = self.get_total_value(cr, uid, [], dia, dia_final, costo, context)
                    if costo_total_ruta:
                        costo = costo_total_ruta.get('value').get('ruta_costo_total')
                        data['ruta_costo_total'] = costo
                    else:
                        raise ValidationError(_('Error de costo', 'No se puede calcular el costo de la ruta!'))
                '''Validamos si el producto existe si no existe lo creamos y si existe no hacemos nada!'''
                product_exist = obj_product.search(cr, uid, [('name','=',producto_name)])
                if not product_exist and facturacion_concepto == False:
                    product_create = {'name':producto_name,
                                      'sale_ok':True,
                                      'purchase_ok':False,
                                      'type':'service',
                                      'list_price':costo,
                                      'categ_id':categoria_contrato[0],
                                      'default_code': producto_name,
                                      'property_account_income':categoria_br.property_account_income_categ.id,
                                      'property_account_expense':categoria_br.property_account_expense_categ.id,
                                      'taxes_id': [(6, 0, contrato_impuestos)],
                                      }
                    obj_product.create(cr, 1, product_create, context=context)

            else:
                '''Si es 0 o negativo no dejamos que se cree'''
                raise ValidationError(_('Error de costo', 'El costo de la ruta  no puede ser menor o igual a 0!'))
                return True
        res = super(contratos_rutas, self).create(cr, uid, data,context=context)
        return res

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        res = super(contratos_rutas, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        self.widget_dinamyc_planes(cr, uid, ids)
        return res

    def get_total_value(self, cr, uid, ids, ruta_ini, ruta_fin, total_uni, context=None):
        if total_uni > 0 and ruta_ini and ruta_fin:
            dias_range = {'lunes':'1','martes':'2','miercoles':'3','jueves':'4','viernes':'5','sabado':'6','domingo':'7'}
            dia_inicial   = dias_range.get(ruta_ini.lower())
            dia_final     = dias_range.get(ruta_fin.lower())
            if dia_inicial > dia_final:
                return {'value':{'ruta_costo_total':None,'ruta_dia':None},'warning':{'title':'Error de validacion de dias','message':'El dia inicial no puede ser superior al final'}}
            total         = len(range(int(dia_inicial),int(dia_final)+1))
            costo_total   = float(total) * float(total_uni)
            return {'value':{'ruta_costo_total':costo_total}}
        if total_uni <= 0 and ruta_ini and ruta_fin:
            return {'value':{'ruta_costo_total':None,'ruta_costo':None},'warning':{'title':'Error de validacion en costo unitario','message':'El costo unitario debe ser mayor a 0!'}}
        else:
            return True

    def widget_dinamyc_planes(self, cr, uid, ids):
        resultados = {}
        if ids:
            rutas = self.browse(cr, uid, ids)
            resultados = dict((ruta.contrato.name.name,{}) for ruta in rutas)
            for ruta in rutas:
                resultados[ruta.contrato.name.name][ruta.id] = {'contratante':ruta.contrato.name.name,
                                   'nombre':ruta.contrato.contrato_analitico.name,
                                   'dia':ruta.ruta_dia,
                                   'costo':ruta.ruta_costo,
                                   'rutanumero':ruta.ruta_numero,
                                   'conductor': ruta.ruta_conductor.name,
                                   'salida':ruta.ruta_hora_salida.name,
                                   'llegada':ruta.ruta_hora_llegada.name,
                                   'origen':ruta.ruta_ciudad_origen,
                                   'destino':ruta.ruta_ciudad_destino,
                                   'dia_final':ruta.ruta_dia_final,
                                   'distancia':ruta.ruta_kilometros}
        return resultados

    def validar_conductor(self, cr, uid, ids, ruta_conductor,ruta_dia,ruta_hora_salida,ruta_hora_llegada,ruta_numero, context=None):
        if ruta_conductor:
            model_conductor = self.pool.get('hr.employee')
            obj_conductor = model_conductor.browse(cr, uid, [ruta_conductor], context=context)
            cedula = obj_conductor.identification_id
            vigencia_licencia = obj_conductor.licencia_vigencia
            hoy = (datetime.datetime.today() + datetime.timedelta(days=10))
            if not cedula:
                return {'value':{'ruta_conductor':''},'warning':{'title':'Error!','message':"El conductor no tiene cedula relacionada verifique el campo numero de identificacion en el modulo de recursos humanos!"}}
            #FIXME: volver a colocar esta validacion cuando la informacion se encuentre completa
            #if vigencia_licencia <= hoy:
            #    return {'value':{'ruta_conductor':''},'warning':{'title':'Error!','message':"La licencia de conduccion se encuentra vencida!"}}
            mensaje = self.validar_disponibilidad_conductor(cr, uid, ruta_conductor,ruta_dia,ruta_hora_salida,ruta_hora_llegada,ruta_numero, context)
            _logger.debug("PRUEBAS %s",mensaje)
            if mensaje:
                return {'value':{'ruta_conductor':''},'warning':{'title':'Error!','message':mensaje}}
            return True
    
    #TODO: CON VALIDACION DE DISTANCIAS Y DISPONIBILIDAD DEL VEHICULO CONDUCTOR SIEMPRE DISPONIBLE
    def validar_disponibilidad_conductor(self,cr, uid, conductor, ruta_dia,ruta_hora_salida,ruta_hora_llegada,ruta_numero,context=None):
        model_ruta = self.pool.get('contratos.rutas')
        model_hora = self.pool.get('contratos.rutas.horas')
        #hora_salida = model_hora.browse(cr, uid, [ruta_hora_salida],context=context).name
        hora_llegada = model_hora.browse(cr, uid, [ruta_hora_llegada],context=context).name
        rxc_ids = model_ruta.search(cr, uid, [('ruta_dia','=',ruta_dia),('ruta_conductor','=',conductor),('ruta_numero','!=',ruta_numero)],context=context)
        if rxc_ids:
            rxc_obj = model_ruta.browse(cr, uid, rxc_ids, context=context)
            for rxc in rxc_obj:
                rxc_hsalida = rxc.ruta_hora_salida.name
                rxc_hllegada = rxc.ruta_hora_llegada.name
                contrato = rxc.contrato.name.name
                conductor = rxc.ruta_conductor.name
                ruta = rxc.ruta_numero
                dia = rxc.ruta_dia
               
        return False
    
    def get_ruta_number(self, cr, uid, ids, contrato, context=None):
        if contrato:
            last_ruta_numero = self.search(cr, uid, [('contrato','=',contrato)],context=context)
            if last_ruta_numero:
                last_ruta_numero = max(last_ruta_numero)
                last_ruta_numero_obj = self.browse(cr, uid, last_ruta_numero,context=context)
                ruta_numero          = last_ruta_numero_obj.ruta_numero + 1
            else:
                ruta_numero = 1
            return {'value':{'ruta_numero':ruta_numero}}

    def validar_distancias(self, cr, uid, ids, dia, kms, salida, llegada, vehiculo, origen, destino,ruta):
        promedio_velocidad = 40
        horario_obj =  self.pool.get('contratos.rutas.horas')
        if dia:
            tiempo_recorrido_aprox = self.get_compute_time((float(kms) / float(promedio_velocidad))*(60*60))
            if kms < 2 or kms > 1400:
                return {'value':{'ruta_kilometros':''},'warning':{'title':'Error!','message':"Seguro que la distancia es %s" % kms}}

            if salida and llegada:
                if salida == llegada:
                    salida_ref = horario_obj.browse(cr, uid, [salida]).name
                    compute_time = self.get_operation_time(salida_ref ,"SUM" ,tiempo_recorrido_aprox)
                    tiempo_llegada_aprox = horario_obj.search(cr, uid, [('name','=',compute_time)])[0]
                    return {'value':{'ruta_hora_llegada':tiempo_llegada_aprox},'warning':{'title':'CALCULO AUTOMATICO','message':'La hora de salida no puede ser igual a la hora de llegada\n Se ha calculado automaticamente la hora de llegada!'}}
                if salida > llegada:
                    salida_ref = horario_obj.browse(cr, uid, [salida]).name
                    compute_time = self.get_operation_time(salida_ref ,"SUM" ,tiempo_recorrido_aprox)
                    tiempo_llegada_aprox = horario_obj.search(cr, uid, [('name','=',compute_time)])[0]
                    return {'value':{'ruta_hora_llegada':tiempo_llegada_aprox},'warning':{'title':'CALCULO AUTOMATICO','message':'La hora de salida no puede ser mayor a la hora de llegada\n Se ha calculado automaticamente la hora de llegada!'}}
                if llegada > salida:
                    validar_ocupacion = self.get_vehiculo_transito(cr, uid, dia, salida, vehiculo, tiempo_recorrido_aprox, origen,destino,ruta)
                    if validar_ocupacion != 0:
                        return validar_ocupacion
            if salida:
                salida_ref = horario_obj.browse(cr, uid, [salida]).name
                compute_time = self.get_operation_time(salida_ref ,"SUM" ,tiempo_recorrido_aprox)
                tiempo_llegada_aprox = horario_obj.search(cr, uid, [('name','=',compute_time)])[0]
                validar_ocupacion = self.get_vehiculo_transito(cr, uid, dia, salida, vehiculo, tiempo_recorrido_aprox, origen,destino,ruta)
                if validar_ocupacion != 0:
                    return validar_ocupacion
                #return {'value':{'ruta_hora_llegada':tiempo_llegada_aprox},'warning':{'title':'CALCULO AUTOMATICO!','message':"Se ha calculado automaticamente la hora de llegada!"}}
            if llegada:
                llegada_ref = horario_obj.browse(cr, uid, [llegada]).name
                compute_time = self.get_operation_time(llegada_ref ,"RES" ,tiempo_recorrido_aprox)
                tiempo_llegada_aprox = horario_obj.search(cr, uid, [('name','=',compute_time)])[0]
                validar_ocupacion = self.get_vehiculo_transito(cr, uid, dia, salida, vehiculo, tiempo_recorrido_aprox, origen,destino,ruta)
                if validar_ocupacion != 0:
                    return validar_ocupacion
                #return {'value':{'ruta_hora_salida':tiempo_llegada_aprox},'warning':{'title':'CALCULO AUTOMATICO!','message':"Se ha calculado automaticamente la hora de salida!"}}
        return True

    def get_compute_time(self, compute_time):
        m, s = divmod(compute_time, 60)
        h, m = divmod(m, 60)
        compute_time = "%02d:%02d:%02d" % (h, m, s)
        return compute_time

    def get_operation_time(self, ini_time, operador ,fin_time):
        if ini_time and fin_time:
            ini_time = ini_time
            fH, fM, fS = map(int, fin_time.split(":"))
            if fM < 30:
                fM = 30
            if fM > 30:
                fM = 0
                fH += 1
            if fS > 0:
                fS = 0
            if operador == "SUM":
                resultado = ini_time + datetime.timedelta(hours=int(fH), minutes=int(fM), seconds=int(fS))
            if operador == "RES":
                resultado = ini_time - datetime.timedelta(hours=int(fH), minutes=int(fM), seconds=int(fS))
            try:
                resultado = resultado
            except:
                resultado = "%02d:%02d:%02d" % (fH,fM,fS)
            return resultado

    def get_vehiculo_transito(self, cr, uid, dia, hora, vehiculo, tiempo_recorrido_aprox, origen, destino, ruta_act):
        en_transito = 0
        horario_obj =  self.pool.get('contratos.rutas.horas')
        ruta_ids = self.search(cr, uid, [('ruta_dia','=', dia),("ruta_numero",'!=',ruta_act),('ruta_vehiculo','=',vehiculo)])
        if ruta_ids:
            ultimo_bloque = self.browse(cr, uid, max(ruta_ids))
            ubicacion_actual_vehiculo = ultimo_bloque.ruta_ciudad_destino.upper()
            '''VALIDAR UBICACION DEL VEHICULO'''
            if origen.upper() != ubicacion_actual_vehiculo:
                pass
                #return {'value':{'ruta_ciudad_destino':origen.upper(),'ruta_ciudad_origen':ultimo_bloque.ruta_ciudad_destino.upper()},
                #        'warning':{'title':'ERROR DE PROGRAMACION DE RUTA',
                #                    'message':'EL VEHICULO NO SE ENCUENTRA EN LA CIUDAD!\n SE ENCUENTRA EN %s NO EN %s\n \
                #                    SE PROGRAMARA %s A %s' %(ultimo_bloque.ruta_ciudad_destino.upper(),origen.upper(),ultimo_bloque.ruta_ciudad_destino.upper(),origen.upper())}}
            hora_ref = horario_obj.browse(cr, uid, hora)
            ruta_obj = self.browse(cr, uid, ruta_ids)
            compute_time_salida = self.get_operation_time(ultimo_bloque.ruta_hora_llegada.name ,"SUM" ,"00:05:00")
            compute_time_llegada = self.get_operation_time(compute_time_salida ,"SUM" ,tiempo_recorrido_aprox)
            transito_salida = horario_obj.search(cr, uid, [('name','=',compute_time_salida)])[0]
            transito_llegada = horario_obj.search(cr, uid, [('name','=',compute_time_llegada)])[0]

            aprox_llegada = self.get_operation_time(hora_ref.name ,"SUM" ,tiempo_recorrido_aprox)
            for ruta in ruta_obj:
                if hora_ref.name and ruta.ruta_hora_llegada.name and ruta.ruta_hora_salida.name:
                    if hora_ref.name <= ruta.ruta_hora_llegada.name and hora_ref.name >= ruta.ruta_hora_salida.name:
                        pass
                    else:
                        if aprox_llegada >= ruta.ruta_hora_salida.name and aprox_llegada <= ruta.ruta_hora_llegada.name:
                            pass
                          
        return en_transito

    def validar_seguros(self, cr, uid, ids, vehiculo, context=None): 
        return {}
        '''
        if vehiculo:
            vehiculo_obj = self.pool.get('fleet.vehicle')
            vehiculos = vehiculo_obj.browse(cr, uid, vehiculo, context)
            hoy = datetime.utcnow()
            for vehiculo in vehiculos:
                soat_id = self.pool.get('vehiculos.soat').search(cr, uid, [('vehiculo_poliza_estado','=','vigente'),('vehiculo','=',vehiculo.id)],context=context)
                soat_vehiculo = self.pool.get('vehiculos.soat').browse(cr, uid, soat_id, context=context)
                if soat_vehiculo:
                    soat_fecha_vencimiento = soat_vehiculo.vehiculo_fecha_vigencia_final
                    fecha_permitida = soat_fecha_vencimiento - datetime.timedelta(days=1)
                    if hoy > fecha_permitida:
                        return {'value':{'ruta_vehiculo':''},'warning':{'title':'SOAT','message':'El soat del vehiculo se encuentra vencido'}}
                else:
                    return {'value':{'ruta_vehiculo':''},'warning':{'title':'SOAT','message':'El vehiculo no tiene SOAT agregados!'}}

                rcc_id = self.pool.get('vehiculos.rcc').search(cr, uid, [('vehiculo_poliza_estado','=','vigente'),('vehiculo','=',vehiculo.id)],context=context)
                rcc_vehiculo = self.pool.get('vehiculos.rcc').browse(cr, uid, rcc_id, context=context)

                if rcc_vehiculo:
                    rcc_fecha_vencimiento = rcc_vehiculo.vehiculo_fecha_vigencia_final
                    fecha_permitida = rcc_fecha_vencimiento - datetime.timedelta(days=1)
                    if hoy > fecha_permitida:
                        return {'value':{'ruta_vehiculo':''},'warning':{'title':'RCC','message':'El seguro de responsabilidad civil contractual del vehiculo se encuentra vencido'}}
                else:
                    return {'value':{'ruta_vehiculo':''},'warning':{'title':'RCC','message':'El vehiculo no tiene seguro de responsabilidad civil contractual agregados!'}}

                rce_id = self.pool.get('vehiculos.rce').search(cr, uid, [('vehiculo_poliza_estado','=','vigente'),('vehiculo','=',vehiculo.id)],context=context)
                rce_vehiculo = self.pool.get('vehiculos.rce').browse(cr, uid, rce_id, context=context)

                if vehiculo.rce:
                    rce_fecha_vencimiento = rce_vehiculo.vehiculo_fecha_vigencia_final
                    fecha_permitida = rce_fecha_vencimiento - datetime.timedelta(days=1)
                    if hoy > fecha_permitida:
                        return {'value':{'ruta_vehiculo':''},'warning':{'title':'RCE','message':'El seguro de responsabilidad civil extra contractual del vehiculo se encuentra vencido'}}
                else:
                    return {'value':{'ruta_vehiculo':''},'warning':{'title':'RCE','message':'El vehiculo no tiene seguro de responsabilidad civil extra contractual agregados!'}}


                #tdr_id = self.pool.get('vehiculos.tdr').search(cr, uid, [('vehiculo_poliza_estado','=','vigente'),('vehiculo','=',vehiculo.id)],context=context)
                #tdr_vehiculo = self.pool.get('vehiculos.tdr').browse(cr, uid, tdr_id, context=context)
                #if tdr_vehiculo:
                    #tdr_fecha_vencimiento = tdr_vehiculo.vehiculo_fecha_vigencia_final
                    #fecha_permitida = tdr_fecha_vencimiento - datetime.timedelta(days=1)
                    #if hoy > fecha_permitida:
                        #return {'value':{'ruta_vehiculo':vehiculo.id},'warning':{'title':'TDR','message':'El seguro todo riesgo del vehiculo se encuentra vencido'}}
                #else:
                    #return {'value':{'ruta_vehiculo':vehiculo.id},'warning':{'title':'TDR','message':'El vehiculo no tiene seguro todo riesgo agregados!'}}

                tope_id = self.pool.get('vehiculos.tope').search(cr, uid, [('vehiculo_poliza_estado','=','vigente'),('vehiculo','=',vehiculo.id)],context=context)
                topes_vehiculo = self.pool.get('vehiculos.tope').browse(cr, uid, tope_id, context=context)
                if topes_vehiculo:
                    tope_fecha_vigencia = topes_vehiculo.vehiculo_fecha_vencimiento
                    tope_fecha_vencimiento = tope_fecha_vigencia
                    fecha_permitida = tope_fecha_vencimiento - datetime.timedelta(days=1)
                    if hoy > fecha_permitida:
                        return {'value':{'ruta_vehiculo':''},'warning':{'title':'Tarjeta operacion','message':'La Tarjeta de operacion del vehiculo se encuentra vencida!'}}
                else:
                    return {'value':{'ruta_vehiculo':''},'warning':{'title':'Tarjeta operacion','message':'El vehiculo no tiene tarjeta de operacion!'}}

                tecnico_id = self.pool.get('vehiculos.tecnicomecanica').search(cr, uid, [('vehiculo_poliza_estado','=','vigente'),('vehiculo','=',vehiculo.id)],context=context)
                tecnico_vehiculo = self.pool.get('vehiculos.tecnicomecanica').browse(cr, uid, tecnico_id, context=context)
                modelo_vehiculo = vehiculo.modelo
                if not modelo_vehiculo:
                    return {'value':{'ruta_vehiculo':''},'warning':{'title':'Modelo del vehiculo','message':'El vehiculo no tiene modelo asignado! no puede programarlo!'}}
                else:
                    modelo_vehiculo = int(modelo_vehiculo) + 1
                ano_actual = datetime.date.today().year
                if modelo_vehiculo >= ano_actual:
                    pass
                else:
                    if tecnico_id:
                        tecnico_fecha_vigencia = tecnico_vehiculo.vehiculo_fecha_vencimiento
                        tecnico_fecha_vencimiento = tecnico_fecha_vigencia
                        fecha_permitida = tecnico_fecha_vencimiento - datetime.timedelta(days=1)
                        if hoy > fecha_permitida:
                            return {'value':{'ruta_vehiculo':''},'warning':{'title':'Revision tecnico mecanica','message':'La Revision tecnico mecanica del vehiculo se encuentra vencida!'}}
                    else:
                        return {'value':{'ruta_vehiculo':''},'warning':{'title':'Revision tecnico mecanica','message':'El vehiculo no tiene revision tecnico mecanica!'}}
            '''

class contratos_rutas_horas(models.Model):
    _name = 'contratos.rutas.horas'
    _description = 'Horarios para las rutas'
    
    name = fields.Char('Horario', size=50)
    tipo = fields.Selection([('diurno','Diurno'),('nocturno','Nocturno')],"Tipo de horario")
