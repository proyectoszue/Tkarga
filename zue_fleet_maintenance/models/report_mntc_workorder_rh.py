# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class mntc_workorder_report_rh(models.Model):
    _name = "mntc.workorder.report.rh"
    _description = "Informe de Recurso Humano para la orden de trabajo"
    _auto = False
    _order = 'orden_trabajo_ot,prioridad_ot'

    orden_trabajo_ot  = fields.Char(string='Orden de Trabajo (OT)', readonly=True)
    prioridad_ot = fields.Char(string='Prioridad (OT)', readonly=True)
    tipo_mantenimiento_ot = fields.Char(string='Tipo de Mantenimiento (OT)', readonly=True)
    estado_ot  = fields.Char(string='Estado (OT)', readonly=True)
    fecha_de_inicio_programada_ot  = fields.Datetime(string='Fecha de Inicio Programada (OT)', readonly=True)
    fecha_de_finalizacion_programada_ot  = fields.Datetime(string='Fecha de Finalización Programada (OT)', readonly=True)
    tiempo_estimado_ot  = fields.Float(string='Tiempo Estimado Orden de Trabajo (OT)', readonly=True)
    fecha_inicio_real_ot  = fields.Datetime(string='Fecha de Inicio Real (OT)', readonly=True)
    fecha_finalizacion_ot  = fields.Datetime(string='Fecha de Finalización (OT)', readonly=True)
    tiempo_empleado_ot  = fields.Float(string='Tiempo Empleado (OT)', readonly=True)
    duracion_real_ot  = fields.Float(string='Duración Real (OT)', readonly=True)
    tarea  = fields.Char(string='Tarea', readonly=True)
    tiempo_estimado_ts  = fields.Float(string='Tiempo Estimado de la Tarea', default=0.0, readonly=True)
    total_horas_hombre_ts = fields.Float(string='Total Horas Hombre (TS)', readonly=True)
    estado_ts  = fields.Char(string='Estado (TS)', readonly=True)
    disciplina  = fields.Char(string='Disciplina', readonly=True)
    tecnico  = fields.Char(string='Técnico', readonly=True)
    fecha_inicio_ejecucion_rrhh = fields.Datetime(string='Fecha Inicial de Ejecución (RRHH)', readonly=True)
    fecha_final_ejecucion_rrhh  = fields.Datetime(string='Fecha Final de Ejecución (RRHH)', readonly=True)
    tiempo_gastado_rrhh = fields.Float(string='Tiempo Gastado (RRHH)', readonly=True)
    fecha_inicio_programado_rrhh = fields.Datetime(string='Fecha Inicial  Programada (RRHH)', readonly=True)
    fecha_final_programado_rrhh  = fields.Datetime(string='Fecha Final  Programada (RRHH)', readonly=True)
    tiempo_estimado_rrhh = fields.Float(string='Tiempo Estimado (RRHH)', readonly=True)
    odometro  = fields.Float(string='Odómetro', default=0.0, readonly=True)
    servicios  = fields.Char(string='Servicios', readonly=True)
    sucursal  = fields.Char(string='Sucursal', readonly=True)
    movil  = fields.Char(string='Móvil (OT)', readonly=True)
    vehiculo  = fields.Char(string='Vehículo (OT)', readonly=True)
    
    @api.model
    def _query(self):
        return '''
        select 
                    row_number() over(order by a.number,a.priority) as id,
                    a.number as orden_trabajo_ot, 
                    case when a.priority = 'priority_1' then 'Emergencia'
                            when a.priority = 'priority_2' then 'Urgente'
                            when a.priority = 'priority_3' then 'Programado'
                            else coalesce(a.priority,'') end as prioridad_ot,
                    case when a.type_mntc = 'type_mntc_1' then 'Preventivo' 
                            when a.type_mntc = 'type_mntc_2' then 'Correctivo' 
                            when a.type_mntc = 'type_mntc_3' then 'Predictivo' 
                            when a.type_mntc = 'type_mntc_4' then 'Mejorativo' 
                            else coalesce(a.type_mntc,'') end as  tipo_mantenimiento_ot,
					 case when a.state = 'planeacion' then 'Planeación' 
                            when a.state = 'waiting_parts' then 'En espera de partes' 
                            when a.state = 'programmed' then 'Programado' 
                            when a.state = 'in_progress' then 'En ejecución' 
							when a.state = 'stopped' then 'Detenido' 
							when a.state = 'ended' then 'Finalizado' 
							when a.state = 'canceled' then 'Cancelado' 
                            else coalesce(a.state,'') end as  estado_ot,
                    coalesce(a.start_programmed_date,'1900-01-01') as fecha_de_inicio_programada_ot,  
                    coalesce(a.end_programmed_date,'1900-01-01') as fecha_de_finalizacion_programada_ot, 
                    coalesce(a.estimated_time,0) as tiempo_estimado_ot, coalesce(a.start_date,'1900-01-01') as fecha_inicio_real_ot,
                    coalesce(a.end_date,'1900-01-01') as fecha_finalizacion_ot,
                    coalesce(a.spent_time,0) as tiempo_empleado_ot, coalesce(a.real_time,0) as  duracion_real_ot,
                    coalesce(b.name,'') as tarea, coalesce(b.estimated_time,0) as tiempo_estimado_ts, 
					coalesce(b.spent_time,0) as total_horas_hombre_ts,
					coalesce(b.state,'') as estado_ts,
                     coalesce(coalesce(e.name,i.name),'') as disciplina, coalesce(d.name,'') as tecnico, 
                    coalesce(c.start_executed_date,'1900-01-01') as fecha_inicio_ejecucion_rrhh,
                    coalesce(c.end_executed_date,'1900-01-01') as fecha_final_ejecucion_rrhh, 
					coalesce(c.spent_time,0) as tiempo_gastado_rrhh,
					coalesce(h.start_programmed_date,'1900-01-01') as fecha_inicio_programado_rrhh,
                    coalesce(h.end_programmed_date,'1900-01-01') as fecha_final_programado_rrhh, 
					coalesce(h.programmed_time ,0) as tiempo_estimado_rrhh,
					coalesce(g.odometer,0) as odometro,
                    coalesce(j.name,'') as servicios,
					coalesce(k.name,'') as sucursal,
                    coalesce(a.movil_nro,'') as movil,
                    coalesce(concat(coalesce(modelbrand.name,''), '/' , coalesce(model.name,''),'/',coalesce(bb.placa_nro,''),'/',coalesce(bb.movil_nro,'')),'') as vehiculo
                from mntc_workorder as a
                    inner join fleet_vehicle as bb on a.vehicle_id = bb.id
                    left  join fleet_vehicle_model as model on bb.model_id = model.id 
                    left  join fleet_vehicle_model_brand as modelbrand  on bb.brand_id = modelbrand.id 
                    left join mntc_tasks as b on a.id = b.workorder_id 
                    left join mntc_executed_workforce_type_rh as c on b.id = c.task_id
                    left join mntc_technician as d on d.id = c.technician_id 
                    left join mntc_workforce_type as e on e.id = c.workforce_type_id 
					left join mntc_io_x_mntc_workorder as f on f.workorder_id = a.id
					left join mntc_io as g on g.id = f.io_id 
					left join mntc_workforce_type_rh as h on b.id = h.task_id
					left join mntc_workforce_type as i on i.id = h.workforce_type_id
                    left join mntc_services_type as j on j.id = bb.service_type_id
					left join zue_res_branch as k on k.id = bb.branch_id      
        ''' 

    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                %s 
            )
        ''' % (
            self._table, self._query()
        ))