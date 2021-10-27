from odoo import models, fields, api, _
import time
import datetime
from odoo.exceptions import UserError, ValidationError

class gestion_diaria_programacion(models.Model):
    _name = 'gestion.diaria.programacion'
    _description = 'Programacion'
    
    fecha_inicial = fields.Date('Fecha inicial')
    fecha_final = fields.Date('Fecha final')
    contrato = fields.Many2one('contratos.contratos','Contrato', ondelete='cascade')
    ruta_dia = fields.Selection([('Lunes','Lunes'),('Martes','Martes'),('Miercoles','Miercoles'),('Jueves','Jueves'),('Viernes','Viernes'),('Sabado','Sabado'),('Domingo','Domingo')],'Dia')
    ruta_dia_final = fields.Selection([('Lunes','Lunes'),('Martes','Martes'),('Miercoles','Miercoles'),('Jueves','Jueves'),('Viernes','Viernes'),('Sabado','Sabado'),('Domingo','Domingo')],'Dia final')
    ruta_numero = fields.Integer('Numero')
    ruta_conductor = fields.Many2one("hr.employee", 'Conductor')
    ruta_vehiculo = fields.Many2one("fleet.vehicle", 'Vehiculo')
    ruta_hora_salida = fields.Many2one('contratos.rutas.horas','Salida')
    ruta_hora_llegada = fields.Many2one('contratos.rutas.horas','Llegada')
    ruta_ciudad_origen = fields.Char('Origen',size=50)
    ruta_ciudad_destino = fields.Char('Destino',size=50)
    ruta_kilometros = fields.Integer('Distancia')
    ruta_via = fields.Char('Via', size=50)
    ruta_costo = fields.Float('Costo')
    estado = fields.Selection([('programada','Programada'),('programada_novedad','Programada'),('despachada','Despachada'),('despachada_novedad','Despachada')], 'Estado')

    def default_get(self, cr, uid, fields, context=None):
        ret = super(gestion_diaria_programacion,self).default_get(cr, uid, fields, context=context)
        contrato_id = context.get('active_id',False)
        if contrato_id:
            ret['contrato'] = contrato_id
        return ret

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        if 'ruta_numero' in fields:
            fields.remove('ruta_numero')
        return super(gestion_diaria_programacion, self).read_group(cr, uid, domain, fields, groupby, offset, limit=limit, context=context, orderby=orderby, lazy=lazy)

    def cargar_programacion(self, cr, uid, ids,context=None):
        _logger.debug("IDS SON IN CREATE %s", ids)
        data = self.browse(cr, uid, ids)
        if 'active_id' in context:
            _logger.debug("ACTIVE IDS SON %s", context)
            contrato_ids = context['active_id']
            fecha_inicial = data.fecha_inicial
            fecha_final = data.fecha_final
            contrato_obj = self.pool.get('contratos.contratos').browse(cr, uid, [contrato_ids])
            iA, iM, iD = map(int, fecha_inicial.split("-"))
            fecha_inicial_date = datetime.date(iA, iM, iD)
            fA, fM, fD = map(int, fecha_final.split("-"))
            fecha_final_date = datetime.date(fA, fM, fD)
            diff_days = fecha_final_date - fecha_inicial_date
            dias_range = {'lunes':'0','martes':'1','miercoles':'2','jueves':'3','viernes':'4','sabado':'5','domingo':'6'}
            dais_reverse_range = {'0':'lunes','1':'martes','2':'miercoles','3':'jueves','4':'viernes','5':'sabado','6':'domingo'}
            data_contrato = {}
            date_generated = [fecha_inicial_date + datetime.timedelta(days=x) for x in range(0, diff_days.days + 1)]
            
            for date in date_generated:
                fecha_inicial =  date
                dia_fecha = date.day
                if contrato_obj.ruta:
                    for ruta in contrato_obj.ruta:
                        dia_inicial = ruta.ruta_dia.lower()
                        dia_final   = ruta.ruta_dia_final.lower()
                        for day_r in range(int(dias_range.get(dia_inicial)),int(dias_range.get(dia_final))+1):
                            dia_programacion = dais_reverse_range.get(str(day_r))
                            if dia_programacion == dia_fecha:
                                fecha_exist = self.search(cr, uid, [('contrato','=',contrato_ids), ('fecha_inicial','=', fecha_inicial),('ruta_dia','=',ruta.ruta_dia),('ruta_numero','=',ruta.ruta_numero)])
                                if not fecha_exist:
                                    data_contrato = {'fecha_inicial':fecha_inicial,
                                                     'fecha_final': fecha_final,
                                                     'contrato': contrato_ids,
                                                     'ruta_dia': dia_programacion.title(),
                                                     'ruta_dia_final':dia_final.title(),
                                                     'ruta_numero': ruta.ruta_numero,
                                                     'ruta_conductor': ruta.ruta_conductor.id,
                                                     'ruta_vehiculo': ruta.ruta_vehiculo.id,
                                                     'ruta_hora_salida':ruta.ruta_hora_salida.id,
                                                     'ruta_hora_llegada':ruta.ruta_hora_llegada.id,
                                                     'ruta_ciudad_origen':ruta.ruta_ciudad_origen,
                                                     'ruta_ciudad_destino':ruta.ruta_ciudad_destino,
                                                     'ruta_kilometros':ruta.ruta_kilometros,
                                                     'ruta_via':ruta.ruta_via,
                                                     'ruta_costo':ruta.ruta_costo,
                                                     'estado':'programada'
                                                     }
                                    self.create(cr, uid, data_contrato, context=context)
                else:
                    self.unlink(cr, uid, ids)
                    return {
                            'type': 'ir.actions.client',
                            'tag': 'action_warn',
                            'name': 'Warning',
                            'params': {
                                       'title': 'Warning!',
                                       'text': 'El contrato no tiene ruteros creados!',
                                       'sticky': True
                                       }
                            }

        self.unlink(cr, uid, ids)
        return {
                'type': 'ir.actions.act_window',
                'name': 'Programacion cargada',
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'gestion.diaria.programacion',
                'target': 'current',
                'context':"{'search_default_contrato': [%s],'group_by': ['fecha_inicial','ruta_dia']}" % contrato_ids
                }

    def validar_fecha(self, cr, uid, ids, fecha, tipo, contrato, context=None):
        fecha_exist = self.search(cr, uid, [('contrato','=',contrato), ('fecha_inicial','=', fecha)])
        if fecha_exist:
            if tipo == 'ini':
                return {'value':{'fecha_inicial':''},'warning':{'title':'Error!','message':"Ya existe programacion para esta fecha %s" % fecha}}
            else:
                return {'value':{'fecha_final':''},'warning':{'title':'Error!','message':"Ya existe programacion para esta fecha %s" % fecha}}
        return True

    def elimina_tildes(self,s):
        import unicodedata
        if isinstance(s, unicode):
            return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c)))
        else:
            return s

class gestion_diaria_despacho(models.Model):
    _name = 'gestion.diaria.despacho'
    _description = 'Despacho'
    
    fecha = fields.Date('Fecha')
    contrato = fields.Many2one('contratos.contratos','Contrato', ondelete='cascade')
    ruta_dia = fields.Selection([('Lunes','Lunes'),('Martes','Martes'),('Miercoles','Miercoles'),('Jueves','Jueves'),('Viernes','Viernes'),('Sabado','Sabado'),('Domingo','Domingo')],'Dia')
    ruta_dia_final = fields.Selection([('Lunes','Lunes'),('Martes','Martes'),('Miercoles','Miercoles'),('Jueves','Jueves'),('Viernes','Viernes'),('Sabado','Sabado'),('Domingo','Domingo')],'Dia final')
    ruta_numero = fields.Integer('Numero')
    ruta_conductor = fields.Many2one("hr.employee", 'Conductor')
    ruta_vehiculo = fields.Many2one("fleet.vehicle", 'Vehiculo')
    ruta_hora_salida = fields.Many2one('contratos.rutas.horas','Salida')
    ruta_hora_llegada = fields.Many2one('contratos.rutas.horas','Llegada')
    ruta_ciudad_origen = fields.Char('Origen',size=50)
    ruta_ciudad_destino = fields.Char('Destino',size=50)
    ruta_kilometros = fields.Integer('Distancia')
    ruta_via = fields.Char('Via', size=50)
    ruta_costo = fields.Float('Costo')
    estado = fields.Selection([('programada','Programada'),('programada_novedad','Programada con novedad'),('despachada','Despachada'),('despachada_novedad','Despachada con novedad')], 'Estado')
    novedades = fields.One2many('gestion.diaria.despacho.novedades', 'despacho', 'Novedades', ondelete='cascade')
                

    def agregar_novedar(self, cr, uid, ids, context=None):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Registrar Novedad',
                'view_mode': 'form',
                'view_type': 'tree,form',
                'res_model': 'gestion.diaria.despacho',
                'target':'new',
                'res_id': ids[0],
                }

    def registrar_novedad(self, cr, uid, ids, context=None):
        error = 0
        if 'novedades' in context:
            for nov in context['novedades']:
                nov_new = nov[-1]
                if nov_new:
                    programacion_obj = self.pool.get('gestion.diaria.programacion')
                    self.write(cr, uid, ids, {'estado':'programada_novedad'})
                    datos = self.browse(cr, uid, ids)
                    contrato = datos.contrato.id
                    fecha = datos.fecha
                    ruta_dia = datos.ruta_dia
                    ruta_dia_final = datos.ruta_dia_final
                    ruta_numero = datos.ruta_numero
                    programacion_ids = programacion_obj.search(cr,uid, [('contrato','=',contrato),('fecha_inicial','=',fecha),('ruta_dia','=',ruta_dia),('ruta_dia_final','=',ruta_dia_final),('ruta_numero','=',ruta_numero)])
                    programacion_obj.write(cr, uid, programacion_ids,{'estado':'programada_novedad'})
                    error = 1
                else:
                    error = 0
        if error == 1:
            return {'type': 'ir.actions.client','tag': 'action_notify','name': 'Information','params': {'title': 'Registro Correcto','text': 'Se ha registrado la novedad!','sticky': True}}

    def despachar_vehiculos(self, cr, uid, ids, context=None):
        despacho_objs = self.browse(cr, uid, ids)
        programacion_obj = self.pool.get('gestion.diaria.programacion')
        for despacho in despacho_objs:
            novedades = despacho.novedades
            contrato = despacho.contrato.id
            fecha = despacho.fecha
            ruta_dia = despacho.ruta_dia
            ruta_dia_final = despacho.ruta_dia_final
            ruta_numero = despacho.ruta_numero
            programacion_ids = programacion_obj.search(cr,uid, [('contrato','=',contrato),('fecha_inicial','=',fecha),('ruta_dia','=',ruta_dia),('ruta_dia_final','=',ruta_dia_final),('ruta_numero','=',ruta_numero)])
            if novedades:
                programacion_obj.write(cr, uid, programacion_ids,{'estado':'despachada_novedad'})
                self.write(cr, uid, despacho.id, {'estado':'despachada_novedad'})
            else:
                self.write(cr, uid, despacho.id, {'estado':'despachada'})
                programacion_obj.write(cr, uid, programacion_ids,{'estado':'despachada'})
        return {}

class gestion_diaria_despacho_novedades(models.Model):
    _name = 'gestion.diaria.despacho.novedades'
    _description = 'Gestión diaria novedades'
    
    despacho = fields.Many2one('gestion.diaria.despacho','Despacho', ondelete='cascade')
    categoria_novedad = fields.Selection([('personal','Personal'),('vehiculo','Vehiculo'),('siniestro','Siniestro'),('relevo_ruta','Relevo en ruta')],'Categoria', required=True)
    novedad = fields.Many2one('gestion.diaria.novedades.tipo', 'Novedad', required=True)
    nota_novedad = fields.Text('Notas', required=True)
    ruta_conductor = fields.Many2one("hr.employee", 'Conductor')
    ruta_vehiculo = fields.Many2one("fleet.vehicle", 'Vehiculo')
    permitir_modificar = fields.Boolean("Permitir modificar")
    relevo_conductor = fields.Boolean("Relevo conductor")
    reemplazo_conductor = fields.Many2one("hr.employee", 'Reemplazo conductor')
    relevo_vehiculo = fields.Boolean("Relevo Vehiculo")
    reemplazo_vehiculo = fields.Many2one("fleet.vehicle", 'Reemplazo vehiculo')

    def setRelevos(self, cr, uid, ids, novedad,context=None):
        result = {'value':{}}
        if novedad:
            novedad_obj = self.pool.get('gestion.diaria.novedades.tipo').browse(cr, uid, [novedad],context=context)
            relevo_personal = novedad_obj.relevo_personal
            relevo_vehiculo = novedad_obj.relevo_vehiculo
            result['value'].update({'relevo_conductor':relevo_personal,'relevo_vehiculo':relevo_vehiculo})
        _logger.debug("RESULTADO ES %s", result)
        return result

    def create(self, cr, uid, data, context=None):
        if 'despacho' in data:
            obj_despacho = self.pool.get('gestion.diaria.despacho').browse(cr, uid, [data['despacho']])
            tipo_personal = data['relevo_conductor']
            tipo_vehiculo = data['relevo_vehiculo']
            _logger.debug("data %s", data)
            if tipo_personal:
                data.update({'ruta_conductor':obj_despacho.ruta_conductor.id})
            if tipo_vehiculo:
                data.update({'ruta_vehiculo':obj_despacho.ruta_vehiculo.id})
            if 'permitir_modificar' in data:
                data['permitir_modificar'] = False
        return super(gestion_diaria_despacho_novedades, self).create(cr, uid, data, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        _logger.debug("vals len %s %s", len(vals) , vals)
        if 'permitir_modificar' not in vals:
            vals.update({'permitir_modificar':False})
        return super(gestion_diaria_despacho_novedades, self).write(cr, uid, ids, vals, context=context)

    def set_autorizar(self, cr, uid, ids, context=None):
        _logger.debug("AUTORIZAR NOVEDADES %s", ids)
        if ids:
            self.write(cr, uid, ids, {'permitir_modificar':True})
        return {}


class gestion_diaria_novedades_tipo(models.Model):
    _name = 'gestion.diaria.novedades.tipo'
    _description = 'Tipo de novedades'
    
    name = fields.Char('Nombre', size=250, required=True)
    categoria = fields.Selection([('personal','Personal'),('vehiculo','Vehiculo'),('siniestro','Siniestro'),('relevo_ruta','Relevo en ruta')],'Categoria de novedad', required=True)
    relevo_personal = fields.Boolean('Relevo personal')
    relevo_vehiculo = fields.Boolean('Relevo vehiculo')
    
