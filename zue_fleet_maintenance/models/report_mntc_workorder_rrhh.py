# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class mntc_workorder_report_rrhh(models.Model):
    _name = "mntc.workorder.report.rrhh"
    _description = "Informe de los  recursos humanos que tienen las orden de trabajo"
    _auto = False
    _order = 'prioridad_ot,prioridad_ot'

    orden_trabajo_ot  = fields.Char(string='Orden de Trabajo (OT)', readonly=True)
    prioridad_ot = fields.Char(string='Prioridad (OT)', readonly=True)
    tipo_mantenimiento_ot = fields.Char(string='Tipo de Mantenimiento (OT)', readonly=True)
    estado_ot  = fields.Char(string='Estado (OT)', readonly=True)
    a_cargo_ot  = fields.Char(string='A cargo (OT)', readonly=True)
    fecha_de_creacion_ot  = fields.Datetime(string='Fecha de Creación (OT)', readonly=True)
    fecha_de_inicio_programada_ot  = fields.Datetime(string='Fecha de Inicio Programada (OT)', readonly=True)
    fecha_de_finalizacion_programada_ot  = fields.Datetime(string='Fecha de Finalización Programada (OT)', readonly=True)
    tiempo_estimado_ot  = fields.Float(string='Tiempo Estimado Orden de Trabajo (OT)', readonly=True)
    fecha_inicio_real_ot  = fields.Datetime(string='Fecha de Inicio Real (OT)', readonly=True)
    fecha_finalizacion_ot  = fields.Datetime(string='Fecha de Finalización (OT)', readonly=True)
    tiempo_empleado_ot  = fields.Float(string='Tiempo Empleado (OT)', readonly=True)
    duracion_real_ot  = fields.Float(string='Duración Real (OT)', readonly=True)
    total_horas_hombre_ot  = fields.Float(string='Total Horas Hombre (OT)', readonly=True)
    movil  = fields.Char(string='Móvil (OT)', readonly=True)
    vehiculo  = fields.Char(string='Vehículo (OT)', readonly=True)
    taller  = fields.Char(string='Taller (OT)', readonly=True)
    ubicacion  = fields.Char(string='Ubicación (OT)', readonly=True)
    fecha_aprobada_ot  = fields.Datetime(string='Fecha de Aprobación (OT)', readonly=True)
    aprobado_por_ot  = fields.Char(string='Aprobado Por (OT)', readonly=True)
    creado_por_ot  = fields.Char(string='Creado Por (OT)', readonly=True)
    finalizado_por_ot  = fields.Char(string='Finalizado Por (OT)', readonly=True)
    costo = fields.Float(string='Costo (OT)', readonly=True)
    costo_servicio  = fields.Float(string='Costo de Servicio (OT)', readonly=True)
    costo_mano_obra  = fields.Float(string='Costo Mano de Obra (OT)', readonly=True)
    disciplina  = fields.Char(string='Disciplina', readonly=True)
    tecnico  = fields.Char(string='Técnico', readonly=True)
    fecha_inicio_ejecucion_rrhh = fields.Datetime(string='Fecha Inicial Ejecutada RRHH', readonly=True)
    fecha_final_ejecucion_rrhh  = fields.Datetime(string='Fecha Final Ejecutada RRHH', readonly=True)
    tiempo_gastado_rrhh  = fields.Float(string='Tiempo gastado RRHH', default=0.0, readonly=True)
    fecha_inicio_programado_rrhh = fields.Datetime(string='Fecha Inicial Programada RRHH', readonly=True)
    fecha_final_programado_rrhh  = fields.Datetime(string='Fecha Final Programada RRHH', readonly=True)
    tiempo_estimado_rrhh = fields.Float(string='Tiempo Estimado RRHH', readonly=True)
    servicios  = fields.Char(string='Servicios', readonly=True)
    sucursal  = fields.Char(string='Sucursal', readonly=True)
    clasificacion_solicitud  = fields.Char(string='Clasificación (Solicitud)', readonly=True)
    prioridad_solicitud  = fields.Char(string='Prioridad (Solicitud)', readonly=True)
    
    @api.model
    def _query(self):
        return '''
      		Select row_number() over(order by A.orden_trabajo_ot,A.prioridad_ot) as id,* 
          From (
            select   
            -- campos orden de trabajo 
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
                        case when a.in_charge = 'planning' then 'Planificación' 
                                when a.in_charge = 'coordinating' then 'Coordinación'
                                else coalesce(a.in_charge,'') end as  a_cargo_ot,
                        coalesce(a.create_date,'1900-01-01') as fecha_de_creacion_ot,
                        coalesce(a.start_programmed_date,'1900-01-01') as fecha_de_inicio_programada_ot,  
                        coalesce(a.end_programmed_date,'1900-01-01') as fecha_de_finalizacion_programada_ot, 
                        coalesce(a.estimated_time,0) as tiempo_estimado_ot, coalesce(a.start_date,'1900-01-01') as fecha_inicio_real_ot,
                        coalesce(a.end_date,'1900-01-01') as fecha_finalizacion_ot,
                        coalesce(a.spent_time,0) as tiempo_empleado_ot, coalesce(a.real_time,0) as  duracion_real_ot,
                        coalesce(a.spent_time,0) as total_horas_hombre_ot,
                        coalesce(a.movil_nro,'') as movil,
                        coalesce(b.name,'') as vehiculo,
                        coalesce(c.display_name,'') as taller,
                        coalesce(c.name,'') as ubicacion,
                        coalesce(a.approved_date,'1900-01-01') as fecha_aprobada_ot, 
                        coalesce(e.name,'') as aprobado_por_ot,
                        coalesce(ff.name,'') as creado_por_ot,
                        coalesce(gg.name,'') as finalizado_por_ot,
			  			coalesce(a.workorder_cost,0) as costo, 
				  		coalesce(a.workforce_cost_pro_supplier,0) as costo_servicio,
			  			coalesce(a.workforce_cost_pro,0) as costo_mano_obra,
                        -- Recurso Humano  
                        coalesce(coalesce(data_executed.name_disciplina,data_programmed.name_disciplina),'') as disciplina,
                        coalesce(data_executed.name_technician,'') as tecnico,
                        coalesce(data_executed.fecha_inicio_ejecucion_rrhh,'1900-01-01') as fecha_inicio_ejecucion_rrhh,
                        coalesce(data_executed.fecha_final_ejecucion_rrhh,'1900-01-01') as fecha_final_ejecucion_rrhh, 
                        coalesce(data_executed.tiempo_gastado_rrhh,0) as tiempo_gastado_rrhh,
                        coalesce(data_programmed.fecha_inicio_programado_rrhh,'1900-01-01') as fecha_inicio_programado_rrhh,
                        coalesce(data_programmed.fecha_final_programado_rrhh,'1900-01-01') as fecha_final_programado_rrhh, 
                        coalesce(data_programmed.tiempo_estimado_rrhh ,0) as tiempo_estimado_rrhh,
                        coalesce(o.odometer,0) as odometro,
                        coalesce(i.name,'') as servicios,
			  		    coalesce(j.name,'') as sucursal,
                        coalesce(mntc_classification.name,'') as clasificacion_solicitud,
						case 	when mntc_solicitud.priority_id = 'priority_1' then 'Emergencia'
                         		when mntc_solicitud.priority_id = 'priority_2' then 'Urgente'
                         		when mntc_solicitud.priority_id = 'priority_3' then 'Programado'
                    			else coalesce(mntc_solicitud.priority_id,'') end as prioridad_solicitud 
                        from mntc_workorder as a 
                        inner join fleet_vehicle as b on a.vehicle_id = b.id 
                        left join mntc_garage as c on a.garage_id = c.id
                        left join mntc_location as d on a.location_id = d.id
                        left join mntc_technician as e  on a.approved_tech_id = e.id
                        left join res_users as f on a.created_by = f.id
                        left join res_partner as ff on f.partner_id = ff.id
                        left join res_users as g on a.ended_by = g.id
                        left join res_partner as gg on g.partner_id = gg.id
                        left join mntc_tasks as h on  h.workorder_id = a.id 
                        left join mntc_io_x_mntc_workorder as n on n.workorder_id = a.id
                        left join mntc_io as o on o.id = n.io_id
                        left join mntc_services_type as i on i.id = b.service_type_id
			 	 	    left join zue_res_branch as j on j.id = b.branch_id
                        Left Join (Select a.id, coalesce(l.start_programmed_date,'1900-01-01') as fecha_inicio_programado_rrhh,
                                    coalesce(l.end_programmed_date,'1900-01-01') as fecha_final_programado_rrhh, 
                                        coalesce(l.programmed_time ,0) as tiempo_estimado_rrhh, 
                                            h.id as id_tarea,m.id as id_disciplina, m.name as name_disciplina
                                    from mntc_workorder as a 
                                    left join mntc_tasks as h on  h.workorder_id = a.id 
                                    left join mntc_workforce_type_rh as l on  l.task_id = h.id 
                                    left join mntc_workforce_type as m on m.id = l.workforce_type_id 
                                ) As data_programmed on a.id = data_programmed.id and h.id = data_programmed.id_tarea 
                        Left Join (Select a.id, coalesce(i.start_executed_date,'1900-01-01') as fecha_inicio_ejecucion_rrhh,
                                        coalesce(i.end_executed_date,'1900-01-01') as fecha_final_ejecucion_rrhh, 
                                        coalesce(i.spent_time,0) as tiempo_gastado_rrhh, 
                                            h.id as id_tarea,j.id as id_disciplina, j.name as name_disciplina, k.name as name_technician
                                    from mntc_workorder as a 
                                    left join mntc_tasks as h on  h.workorder_id = a.id 
                                    left join mntc_executed_workforce_type_rh as i on i.task_id = h.id 
                                    left join mntc_workforce_type as j on j.id = i.workforce_type_id
                                    left join mntc_technician as k on k.id = i.technician_id 
                                ) As data_executed on a.id = data_executed.id and h.id = data_executed.id_tarea and data_executed.id_disciplina = data_programmed.id_disciplina
                        left join mntc_request as mntc_solicitud on mntc_solicitud.id = a.request_id
						left join mntc_workorder_classification as mntc_classification  on mntc_classification.id = mntc_solicitud.classification1
                                    Where a.state = 'programmed'							  
        Union All
            select   
  		    -- campos orden de trabajo                     
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
					case when a.in_charge = 'planning' then 'Planificación' 
                            when a.in_charge = 'coordinating' then 'Coordinación'
							 else coalesce(a.in_charge,'') end as  a_cargo_ot,
					coalesce(a.create_date,'1900-01-01') as fecha_de_creacion_ot,
                    coalesce(a.start_programmed_date,'1900-01-01') as fecha_de_inicio_programada_ot,  
                    coalesce(a.end_programmed_date,'1900-01-01') as fecha_de_finalizacion_programada_ot, 
                    coalesce(a.estimated_time,0) as tiempo_estimado_ot, coalesce(a.start_date,'1900-01-01') as fecha_inicio_real_ot,
                    coalesce(a.end_date,'1900-01-01') as fecha_finalizacion_ot,
                    coalesce(a.spent_time,0) as tiempo_empleado_ot, coalesce(a.real_time,0) as  duracion_real_ot,
					coalesce(a.spent_time,0) as total_horas_hombre_ot,
					coalesce(a.movil_nro,'') as movil,
					coalesce(b.name,'') as vehiculo,
					coalesce(c.display_name,'') as taller,
					coalesce(c.name,'') as ubicacion,
					coalesce(a.approved_date,'1900-01-01') as fecha_aprobada_ot, 
					coalesce(e.name,'') as aprobado_por_ot,
					coalesce(ff.name,'') as creado_por_ot,
					coalesce(gg.name,'') as finalizado_por_ot,
			  		coalesce(a.workorder_cost,0) as costo, 
				  	coalesce(a.workforce_cost_pro_supplier,0) as costo_servicio,
			  		coalesce(a.workforce_cost_pro,0) as costo_mano_obra,
					-- Recurso Humano  
					coalesce(coalesce(data_executed.name_disciplina,data_programmed.name_disciplina),'') as disciplina,
					coalesce(data_executed.name_technician,'') as tecnico,
					coalesce(data_executed.fecha_inicio_ejecucion_rrhh,'1900-01-01') as fecha_inicio_ejecucion_rrhh,
                    coalesce(data_executed.fecha_final_ejecucion_rrhh,'1900-01-01') as fecha_final_ejecucion_rrhh, 
					coalesce(data_executed.tiempo_gastado_rrhh,0) as tiempo_gastado_rrhh,
					coalesce(data_programmed.fecha_inicio_programado_rrhh,'1900-01-01') as fecha_inicio_programado_rrhh,
                    coalesce(data_programmed.fecha_final_programado_rrhh,'1900-01-01') as fecha_final_programado_rrhh, 
					coalesce(data_programmed.tiempo_estimado_rrhh ,0) as tiempo_estimado_rrhh,
					coalesce(o.odometer,0) as odometro,
                    coalesce(i.name,'') as servicios,
			  		coalesce(j.name,'') as sucursal,
                    coalesce(mntc_classification.name,'') as clasificacion_solicitud,
					case 	when mntc_solicitud.priority_id = 'priority_1' then 'Emergencia'
                         	when mntc_solicitud.priority_id = 'priority_2' then 'Urgente'
                         	when mntc_solicitud.priority_id = 'priority_3' then 'Programado'
                    		else coalesce(mntc_solicitud.priority_id,'') end as prioridad_solicitud
					from mntc_workorder as a 
					inner join fleet_vehicle as b on a.vehicle_id = b.id 
					left join mntc_garage as c on a.garage_id = c.id
					left join mntc_location as d on a.location_id = d.id
					left join mntc_technician as e  on a.approved_tech_id = e.id
					left join res_users as f on a.created_by = f.id
					left join res_partner as ff on f.partner_id = ff.id
					left join res_users as g on a.ended_by = g.id
					left join res_partner as gg on g.partner_id = gg.id
					left join mntc_tasks as h on  h.workorder_id = a.id 
					left join mntc_io_x_mntc_workorder as n on n.workorder_id = a.id
					left join mntc_io as o on o.id = n.io_id 
                    left join mntc_services_type as i on i.id = b.service_type_id
			 	 	left join zue_res_branch as j on j.id = b.branch_id
					Left Join (Select a.id, coalesce(i.start_executed_date,'1900-01-01') as fecha_inicio_ejecucion_rrhh,
									  coalesce(i.end_executed_date,'1900-01-01') as fecha_final_ejecucion_rrhh, 
									  coalesce(i.spent_time,0) as tiempo_gastado_rrhh, 
							   			h.id as id_tarea,j.id as id_disciplina, j.name as name_disciplina, k.name as name_technician
								from mntc_workorder as a 
								left join mntc_tasks as h on  h.workorder_id = a.id 
								left join mntc_executed_workforce_type_rh as i on i.task_id = h.id 
								left join mntc_workforce_type as j on j.id = i.workforce_type_id
							  	left join mntc_technician as k on k.id = i.technician_id 
							  ) As data_executed on a.id = data_executed.id and h.id = data_executed.id_tarea
					Left Join (Select a.id, coalesce(l.start_programmed_date,'1900-01-01') as fecha_inicio_programado_rrhh,
                    			coalesce(l.end_programmed_date,'1900-01-01') as fecha_final_programado_rrhh, 
									coalesce(l.programmed_time ,0) as tiempo_estimado_rrhh, 
							   			h.id as id_tarea,m.id as id_disciplina, m.name as name_disciplina
								from mntc_workorder as a 
								left join mntc_tasks as h on  h.workorder_id = a.id 
								left join mntc_workforce_type_rh as l on  l.task_id = h.id 
								left join mntc_workforce_type as m on m.id = l.workforce_type_id 
							  ) As data_programmed on a.id = data_programmed.id and h.id = data_programmed.id_tarea and data_executed.id_disciplina = data_programmed.id_disciplina
                    left join mntc_request as mntc_solicitud on mntc_solicitud.id = a.request_id
					left join mntc_workorder_classification as mntc_classification  on mntc_classification.id = mntc_solicitud.classification1
					Where a.state != 'programmed'
			) as A						  
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