from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class mntc_indicators_dashboard_filters(models.TransientModel):
    _name = "mntc.indicators.dashboard.filters"
    _description = "Indicadores Mantenimiento Filtros"

    date_start = fields.Datetime(string='Fecha Inicial', required=True)
    date_end = fields.Datetime(string='Fecha Final', required=True)
    branch_id = fields.Many2one('zue.res.branch',string='Sucursal', required=True)

    def execute_indicators_dashboard(self):
        ctx = self.env.context.copy()
        ctx.update({'date_start': self.date_start, 'date_end': self.date_end, 'branch_id': self.branch_id.name})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Indicadores Mantenimiento',
            'res_model': 'mntc.indicators.dashboard',
            'domain': [],
            'view_mode': 'form',
            'context': ctx
        }

class mntc_indicators_dashboard(models.TransientModel):
    _name = "mntc.indicators.dashboard"
    _description = "Indicadores Mantenimiento"

    def get_indicators_respuestos(self):
        obj_reporte = self.env['mntc.respuestos.indicators']
        obj_reporte.init(self.env.context)
        return self.env['mntc.respuestos.indicators'].search([('id', '!=', False)]).ids

    def get_indicators_workorder(self):
        obj_reporte = self.env['mntc.workorder.indicators']
        obj_reporte.init(self.env.context)
        return self.env['mntc.workorder.indicators'].search([('id', '!=', False)]).ids

    def get_indicators_working_staff(self):
        obj_reporte = self.env['mntc.working.staff']
        obj_reporte.init(self.env.context)
        return self.env['mntc.working.staff'].search([('id', '!=', False)]).ids

    def get_indicators_absenteeism(self):
        obj_reporte = self.env['mntc.absenteeism.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.absenteeism.indicator'].search([('id', '!=', False)]).ids

    def get_indicators_security(self):
        obj_reporte = self.env['mntc.security.working.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.security.working.indicator'].search([('id', '!=', False)]).ids

    def get_indicators_events(self):
        obj_reporte = self.env['mntc.events.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.events.indicator'].search([('id', '!=', False)]).ids

    def get_ten_days_garage_vehicle(self):
        obj_reporte = self.env['mntc.days.garage.vehicle.ind']
        obj_reporte.init(self.env.context)
        return self.env['mntc.days.garage.vehicle.ind'].search([('id', '!=', False)]).ids

    def get_acum_costs(self):
        obj_reporte = self.env['mntc.acum.cost.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.acum.cost.indicator'].search([('id', '!=', False)]).ids

    def get_campaigns(self):
        obj_reporte = self.env['mntc.campaign.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.campaign.indicator'].search([('id', '!=', False)]).ids

    def get_accomplishment(self):
        obj_reporte = self.env['mntc.accomplishment.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.accomplishment.indicator'].search([('id', '!=', False)]).ids

    def get_week_schedule(self):
        obj_reporte = self.env['mntc.week.schedule.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.week.schedule.indicator'].search([('id', '!=', False)]).ids

    def get_weekly_work(self):
        obj_reporte = self.env['mntc.weekly.work.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.weekly.work.indicator'].search([('id', '!=', False)]).ids

    def get_main_urgency(self):
        obj_reporte = self.env['mntc.main.urgency.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.main.urgency.indicator'].search([('id', '!=', False)]).ids

    def get_draft_requests(self):
        obj_reporte = self.env['mntc.draft.requests.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.draft.requests.indicator'].search([('id', '!=', False)]).ids

    def get_pending_workorder(self):
        obj_reporte = self.env['mntc.pending.workorder.indicator']
        obj_reporte.init(self.env.context)
        return self.env['mntc.pending.workorder.indicator'].search([('id', '!=', False)]).ids


    name = fields.Char(string='Reporte', required=True)
    indicators_respuestos_ids = fields.Many2many('mntc.respuestos.indicators', string='Indicadores',default=get_indicators_respuestos, readonly=True)
    indicators_working_staff_ids = fields.Many2many('mntc.working.staff', string='Indicadores personal laborando',default=get_indicators_working_staff, readonly=True)
    indicators_absenteeism_ids = fields.Many2many('mntc.absenteeism.indicator', string='Indicadores ausentismos',default=get_indicators_absenteeism, readonly=True)
    indicators_security_ids = fields.Many2many('mntc.security.working.indicator', string='Indicadores seguridad', default=get_indicators_security, readonly=True)
    indicators_events_ids = fields.Many2many('mntc.events.indicator', string='Indicadores eventos', default=get_indicators_events, readonly=True)
    indicators_ten_days_garage_ids = fields.Many2many('mntc.days.garage.vehicle.ind', string='Indicador 10 días taller', default=get_ten_days_garage_vehicle, readonly=True)
    indicators_acum_costs = fields.Many2many('mntc.acum.cost.indicator', string='Costos Acumulados', default=get_acum_costs, readonly=True)
    indicators_campaigns = fields.Many2many('mntc.campaign.indicator', string='Campañas',default=get_campaigns, readonly=True)
    indicators_accomplishment = fields.Many2many('mntc.accomplishment.indicator', string='Cumplimiento', default=get_accomplishment,readonly=True)
    indicators_week_schedule = fields.Many2many('mntc.week.schedule.indicator', string='Programación Semana', default=get_week_schedule, readonly=True)
    indicators_weekly_work = fields.Many2many('mntc.weekly.work.indicator', string='Trabajo de la Semana', default=get_weekly_work, readonly=True)
    indicators_main_urgency = fields.Many2many('mntc.main.urgency.indicator', string='Causa principal urgencias', default=get_main_urgency, readonly=True)
    indicators_draft_requests = fields.Many2many('mntc.draft.requests.indicator', string='Solicitudes en borrador', default=get_draft_requests, readonly=True)
    indicators_pending_workorder = fields.Many2many('mntc.pending.workorder.indicator', string='Órdenes de trabajo pendientes', default=get_pending_workorder, readonly=True)
    counter_reports = fields.Integer(compute='compute_counter_reports', string='Reporte Generado')

    def compute_counter_reports(self):
        #count = self.env['mntc.indicators.dashboard'].search_count([('id', '!=', False)])
        self.counter_reports = 1

    def return_action_to_open(self):
        res = {
            'name': 'Reportes',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mntc.indicators.dashboard',
            'target': 'current',
            'domain': "[('id','in',[" + str(self._ids[0]) + "])]"
        }
        return res

class mntc_respuestos_indicators(models.Model):
    _name = "mntc.respuestos.indicators"
    _description = "Indicadores de los respuestos"
    _auto = False

    servicio = fields.Char(string='Servicio', readonly=True)
    sucursal = fields.Char(string='Sucursal', readonly=True)
    total_equipos = fields.Integer(string='Equipos Total', readonly=True)
    dias_equipos_taller = fields.Integer(string='Días Equipos en Taller', readonly=True)
    equipos_soporte = fields.Integer(string='Equipos Soporte', readonly=True)
    disponibilidad = fields.Float(string='Disponibilidad', readonly=True)
    km_semana = fields.Integer(string='KM Semana', readonly=True)
    num_varadas = fields.Integer(string='# Varadas', readonly=True)
    num_urgencias = fields.Integer(string='# Urgencias', readonly=True)
    rutinas_atrasadas = fields.Integer(string='# Rutinas Atrasadas', readonly=True)
    mkbf_entradas = fields.Float(string='MKBF Entradas', readonly=True)
    mttr_entradas = fields.Float(string='MTTR Entradas', readonly=True)
    costo_repuesto = fields.Float(string='Costo Repuesto', readonly=True)
    costo_campania = fields.Float(string='Costo Campaña', readonly=True)
    costo_total = fields.Float(string='Costo Total', readonly=True)
    cpk = fields.Float(string='CPK', readonly=True)

    @api.model
    def _query(self,filter_context):
        num_urgencias = 0
        # round(cast((km_semana / cant_entradas) + (dias_equipos_taller / cant_entradas) + costo_repuesto + costo_campania as numeric), 2) else
        # round(cast(((km_semana / cant_entradas) + (dias_equipos_taller / cant_entradas) + costo_repuesto + costo_campania) / num_urgencias as numeric), 2) end as cpk
        query = f'''
            select row_number() over(order by servicio) as id, servicio, sucursal, total_equipos, round(cast(dias_equipos_taller as numeric), 2) as dias_equipos_taller, equipos_soporte, 
                    round(cast((((total_equipos * date_part('days', '{filter_context.get('date_end', '1900-01-01')}'::timestamp - '{filter_context.get('date_start', '1900-01-01')}'::timestamp)
                    )-dias_equipos_taller)/((total_equipos* date_part('days', '{filter_context.get('date_end', '1900-01-01')}'::timestamp - '{filter_context.get('date_start', '1900-01-01')}'::timestamp)
                    ))*100) as numeric), 2) as disponibilidad,
                    km_semana, num_varadas, num_urgencias, 0 as rutinas_atrasadas, round(cast((km_semana/cant_entradas) as numeric), 2)  as mkbf_entradas,
                    round(cast((duracion_entradas_h/cant_entradas) as numeric), 2) as mttr_entradas, round(cast(costo_repuesto as numeric), 2) as costo_repuesto, costo_campania, 
                    round(cast((km_semana/cant_entradas) + (dias_equipos_taller/cant_entradas) + costo_repuesto + costo_campania as numeric), 2) as costo_total, 
                    case when km_semana = 0 then 0 else round(cast(costo_repuesto / km_semana as numeric), 2) end as cpk                    
            from 
            (
                select B.total_equipos, A.servicio, sucursal, coalesce(sum(dias_taller)/24, 0) as dias_equipos_taller, 0 as equipos_soporte, sum(km_recorrido) as km_semana, 
                        sum(urgencia) as num_urgencias, sum(cant_entradas) as cant_entradas, sum(cant_tareas) as cant_tareas, sum(duracion_tareas) as duracion_tareas,
                        sum(costo_repuesto) as costo_repuesto, sum(cant_orden_t) as cant_orden_t, sum(costo_repuesto_camp) as costo_campania, sum(num_varadas) as num_varadas,
                        sum(dias_taller) as duracion_entradas_h
                from 
                (
                    select A.id, D."name" as servicio, F."name" as sucursal, dias_taller, km_recorrido, urgencia, cant_entradas, sum(cant_tareas) as cant_tareas,
                            sum(duracion_tareas) as duracion_tareas, sum(costo_repuesto) as costo_repuesto, sum(cant_orden_t) as cant_orden_t,
                            coalesce(sum(costo_repuesto_camp), 0) as costo_repuesto_camp, coalesce(sum(num_varadas), 0) as num_varadas
                    from fleet_vehicle A
                    inner join mntc_workorder B on A.id = B.vehicle_id and B.state != 'canceled' and B.start_date >= '{filter_context.get('date_start', '1900-01-01')}' and B.start_date <= '{filter_context.get('date_end', '1900-01-01')}'
                    inner join mntc_tasks C on C.workorder_id = B.id  
                    inner join mntc_services_type D on C.service_type_id = D.id
                    inner join mntc_garage E on B.garage_id = E.id 
                    inner join zue_res_branch F on E.branch_id = F.id	
                    left join
                    (
                        select sum(date_part('hour', case when AA.outgoing_date isnull then CURRENT_DATE else AA.outgoing_date end - AA.incoming_date)) as dias_taller, AB.id,
                                count(AA.id) as cant_entradas
                        from mntc_io AA
                        inner join fleet_vehicle AB on AA.vehicle_id = AB.id 
                        where AA.incoming_date >= '{filter_context.get('date_start', '1900-01-01')}' and AA.incoming_date <= '{filter_context.get('date_end', '1900-01-01')}'
                        group by AB.id 
                    ) G on A.id = G.id
                    left join
                    (
                        select max(AB.value) - min(AB.value) as km_recorrido, AA.id 
                        from fleet_vehicle AA
                        inner join fleet_vehicle_odometer AB on AA.id = AB.vehicle_id
                        where AB."date" >= '{filter_context.get('date_start', '1900-01-01')}' and AB."date" <= '{filter_context.get('date_end', '1900-01-01')}'
                        group by AA.id 
                    ) H on A.id = H.id
                    left join
                    (
                        select sum(case when AA.origin_state = 'in_progress' then 1 else 0 end) as urgencia, AB.id 
                        from mntc_workorder AA
                        inner join fleet_vehicle AB on AA.vehicle_id = AB.id
                        where AA.start_date >= '{filter_context.get('date_start', '1900-01-01')}' and AA.start_date <= '{filter_context.get('date_end', '1900-01-01')}'
                        group by AB.id 
                    ) I on A.id = I.id	
                    left join
                    (
                        select AB.id, count(AA.id) as cant_tareas,
                                date_part('hour', sum(case when AA.end_executed_date isnull then CURRENT_DATE else AA.end_executed_date end - AA.start_executed_date)) as duracion_tareas
                        from mntc_tasks AA
                        inner join mntc_workorder AB on AA.workorder_id = AB.id 
                        group by AB.id 
                    ) J on B.id = J.id	
                    left join 
                    (
                        select A.id, sum(abs(coalesce(E.value,0))) as costo_repuesto, 1 as cant_orden_t
                        from mntc_workorder A
                        inner join mntc_tasks B on B.workorder_id = A.id 
                        left join mntc_repuestos C on C.tasks_id = B.id 
                        left join stock_move D on C.move_line_id = D.id 
                        left join stock_valuation_layer E on E.stock_move_id = D.id
                        group by A.id
                    ) K on B.id = K.id
                    left join
                    (
                        select A.id, sum(abs(coalesce(E.value,0))) as costo_repuesto_camp
                        from mntc_workorder A
                        inner join mntc_tasks B on B.workorder_id = A.id 
                        inner join mntc_request F on A.request_id = F.id and F.classification1 = 2
                        left join mntc_repuestos C on C.tasks_id = B.id 
                        left join stock_move D on C.move_line_id = D.id 
                        left join stock_valuation_layer E on E.stock_move_id = D.id
                        group by A.id
                    ) L on B.id = L.id	
                    left join
                    (
                        select A.id, 1 as num_varadas
                        from mntc_workorder A
                        inner join mntc_request B on A.request_id = B.id and B.priority_id = 'priority_1'
                        group by A.id
                    ) M on B.id = M.id	
                    where F."name" = '{filter_context.get('branch_id', '')}'
                    group by A.id, D."name", F."name", dias_taller, km_recorrido, urgencia, cant_entradas
                ) A
                inner join 
                (
                    select count(id) as total_equipos, servicio 
                    from 
                    (
                        select A.id, B."name" as servicio 
                        from fleet_vehicle A
                        inner join mntc_services_type B on A.service_type_id = B.id 
                    ) a
                    group by servicio     	
                ) B on A.servicio = B.servicio
                group by A.servicio, sucursal, B.total_equipos
            ) main 
            order by servicio 
        '''

        return query

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_working_staff(models.Model):
    _name = "mntc.working.staff"
    _description = "Indicador personal laborando"
    _auto = False

    num_tecnicos = fields.Integer(string='# Técnicos', readonly=True)
    num_tecnicos_programa = fields.Integer(string='# Técnicos Programados', readonly=True)
    horas_semana = fields.Integer(string='Horas Semana', readonly=True)
    horas_programa = fields.Integer(string='Horas Programadas', readonly=True)
    horas_disponibles = fields.Integer(string='Horas Totales Disponibles', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by periodo) as id, periodo,
                    sum(num_tecnicos) as num_tecnicos, sum(num_tecnicos_programa) as num_tecnicos_programa, 
                    sum(horas_semana) as horas_semana, sum(horas_programa) as horas_programa,
                    sum(horas_programa) - sum(horas_semana) as horas_disponibles
            from 
            (
                select count(A.id) as num_tecnicos, 0 as num_tecnicos_programa, sum(A.spent_time) as horas_semana, 0 as horas_programa, '1' as periodo
                from mntc_executed_workforce_type_rh A
                inner join mntc_tasks B on B.id = A.task_id 
                inner join mntc_garage E on B.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id	
                where B.start_programmed_date >= '{filter_context.get('date_start', '1900-01-01')}' and B.start_programmed_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}'
                union all
                select 0 as num_tecnicos, count(A.id) as num_tecnicos_programa, 0 as horas_semana, sum(A.programmed_time) as horas_programa, '1' as periodo
                from mntc_workforce_type_rh A
                inner join mntc_tasks B on B.activity_id = A.task_id 
                inner join mntc_garage E on B.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id	
                where B.start_programmed_date >= '{filter_context.get('date_start', '1900-01-01')}' and B.start_programmed_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}'
            ) main
            group by periodo
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_absenteeism_indicator(models.Model):
    _name = "mntc.absenteeism.indicator"
    _description = "Indicador ausentismos"
    _auto = False

    ficha = fields.Char(string='Ficha', readonly=True)
    tecnico = fields.Char(string='Técnico', readonly=True)
    motivo = fields.Char(string='Motivo', readonly=True)
    horas_perdidas = fields.Char(string='Horas Perdidas Semana', readonly=True)

    @api.model
    def _query(self,filter_context):
        return '''
            select row_number() over(order by id) as id, '' as ficha, '' as tecnico, '' as motivo, '' as horas_perdidas
            from mntc_workorder A 
            where 1=2
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_security_working_indicator(models.Model):
    _name = "mntc.security.working.indicator"
    _description = "Indicador seguridad, accidentes-incidentes"
    _auto = False

    ficha = fields.Char(string='Ficha', readonly=True)
    tecnico = fields.Char(string='Técnico', readonly=True)
    descripcion_evento = fields.Char(string='Descripción del evento', readonly=True)
    horas_perdidas = fields.Char(string='Horas Perdidas Semana', readonly=True)
    horas_perdidas_acum = fields.Char(string='Horas Perdidas Acumuladas', readonly=True)

    @api.model
    def _query(self,filter_context):
        return '''
            select row_number() over(order by id) as id, '' as ficha, '' as tecnico, '' as descripcion_evento, 
                    '' as horas_perdidas, '' as horas_perdidas_acum
            from mntc_workorder A 
            where 1=2
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_events_indicator(models.Model):
    _name = "mntc.events.indicator"
    _description = "Indicador eventos mayores"
    _auto = False

    sucursal = fields.Char(string='Sucursal', readonly=True)
    movil = fields.Char(string='Móvil', readonly=True)
    evento = fields.Char(string='Evento', readonly=True)
    parte = fields.Char(string='Parte', readonly=True)
    falla = fields.Char(string='Falla', readonly=True)
    causa = fields.Char(string='Causa', readonly=True)
    accion = fields.Char(string='Acción', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by F."name") as id,
                    F."name" as sucursal, B.movil_nro as movil, C.process_description_programm as evento,
                    G."name" as parte, H."name" as falla, I."name" as causa, J."name" as accion
            from mntc_workorder  A
            inner join fleet_vehicle B on B.id = A.vehicle_id
            inner join mntc_tasks C on C.workorder_id = A.id
            inner join mntc_garage E on A.garage_id = E.id
            inner join zue_res_branch F on E.branch_id = F.id
            inner join mntc_component G on C.component_id = G.id
            inner join mntc_spare_part_type H on C.spare_part_type_id = H.id
            inner join mntc_causes I on C.cause_id = I.id
            inner join mntc_action_taken J on C.action_taken_id = J.id
            where A.state != 'canceled' and A.origin_state = 'in_progress' and A.start_date >= '{filter_context.get('date_start', '1900-01-01')}' and and A.start_date <= '{filter_context.get('date_end', '1900-01-01')}'
                    and F."name" = '{filter_context.get('branch_id', '')}'
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_events_indicator(models.Model):
    _name = "mntc.events.indicator"
    _description = "Indicador eventos mayores"
    _auto = False

    sucursal = fields.Char(string='Sucursal', readonly=True)
    movil = fields.Char(string='Móvil', readonly=True)
    evento = fields.Char(string='Evento', readonly=True)
    parte = fields.Char(string='Parte', readonly=True)
    falla = fields.Char(string='Falla', readonly=True)
    causa = fields.Char(string='Causa', readonly=True)
    accion = fields.Char(string='Acción', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by F."name") as id,
                    F."name" as sucursal, B.movil_nro as movil, C.process_description_programm as evento,
                    G."name" as parte, H."name" as falla, I."name" as causa, J."name" as accion
            from mntc_workorder  A
            inner join fleet_vehicle B on B.id = A.vehicle_id
            inner join mntc_tasks C on C.workorder_id = A.id
            inner join mntc_garage E on A.garage_id = E.id
            inner join zue_res_branch F on E.branch_id = F.id
            inner join mntc_component G on C.component_id = G.id
            inner join mntc_spare_part_type H on C.spare_part_type_id = H.id
            inner join mntc_causes I on C.cause_id = I.id
            inner join mntc_action_taken J on C.action_taken_id = J.id
            where A.state != 'canceled' and A.origin_state = 'in_progress' and A.start_date >= '{filter_context.get('date_start', '1900-01-01')}' and A.start_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                    and F."name" = '{filter_context.get('branch_id', '')}'
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_days_garage_vehicle_ind(models.Model):
    _name = "mntc.days.garage.vehicle.ind"
    _description = "Indicador vehiculos con 10 dias en taller"
    _auto = False

    sucursal = fields.Char(string='Sucursal', readonly=True)
    movil = fields.Char(string='Móvil', readonly=True)
    entrada = fields.Char(string='Entrada', readonly=True)
    ingreso = fields.Datetime(string='Ingreso', readonly=True)
    nro_dias = fields.Char(string='# Días', readonly=True)
    estado = fields.Char(string='Estado', readonly=True)
    fet = fields.Char(string='Fecha Estimada Salida', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by movil) as id, *
            from
            (
                select D."name" as sucursal, B.movil_nro as movil, A."number" as entrada, 
                        case when A.state = 'in' then 'Ingreso' when A.state = 'out' then 'Salida' when A.state = 'programmed' then 'Programada' end as estado, 
                        A.incoming_date as ingreso, case when A.state != 'out' then A.scheduled_outgoing_date else A.outgoing_date end as fet,
                        date_part('day', case when A.outgoing_date isnull then CURRENT_DATE else A.outgoing_date end - A.incoming_date) as nro_dias
                from mntc_io A
                inner join fleet_vehicle B on A.vehicle_id = B.id
                inner join mntc_garage C on a.garage_id = C.id 
                inner join zue_res_branch D on C.branch_id = D.id
                where a.state != 'canceled' and a.incoming_date >= '{filter_context.get('date_start', '1900-01-01')}' and a.incoming_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and D."name" = '{filter_context.get('branch_id', '')}' 
                order by B.movil_nro 
            ) main
            where nro_dias > 10 
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_acum_cost_indicator(models.Model):
    _name = "mntc.acum.cost.indicator"
    _description = "Indicador acumulado de costos"
    _auto = False

    costo_acum_ano = fields.Float(string='COSTO ACOMULADO AÑO', readonly=True)
    costo_acum_mes = fields.Float(string='COSTO ACUMULADO MES', readonly=True)
    presupuesto_acum_ano = fields.Float(string='PRESUPUESTO ACUMULADO AÑO', readonly=True)
    presupuesto_acum_mes = fields.Float(string='PRESUPUESTO ACUMULADO MES', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by id) as id,
                    sum(round(cast(costo_acum_ano as numeric), 2)) as costo_acum_ano, sum(round(cast(costo_acum_mes as numeric), 2)) as costo_acum_mes, 
		            0 as presupuesto_acum_ano, 0 as presupuesto_acum_mes
            from 
            (
                select 1 as id, sum(A.workorder_cost + A.workforce_cost_pro + A.workforce_cost_pro_supplier) as costo_acum_ano, 0 as costo_acum_mes
                from mntc_workorder A
                inner join mntc_garage E on A.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id
                where A.create_date <= '{filter_context.get('date_end', '1900-01-01')}' and F."name" = '{filter_context.get('branch_id', '')}' 
                group by extract(year from A.create_date)
                union all
                select 1 as id, 0 as costo_acum_ano, sum(A.workorder_cost + A.workforce_cost_pro + A.workforce_cost_pro_supplier)as costo_acum_mes
                from mntc_workorder A
                inner join mntc_garage E on A.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id
                where A.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and A.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                         and F."name" = '{filter_context.get('branch_id', '')}' 
                group by extract(year from A.create_date)
            ) main
            group by id 
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_campaign_indicator(models.Model):
    _name = "mntc.campaign.indicator"
    _description = "Indicador de campaña"
    _auto = False

    total_ejecutado = fields.Float(string='Total ejecutado', readonly=True)
    total_x_ejecutar = fields.Float(string='Total por ejecutar', readonly=True)
    ejeutado_semana = fields.Float(string='Ejecutado semana', readonly=True)
    pendientes = fields.Float(string='Pendientes', readonly=True)
    fet = fields.Datetime(string='FET', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by id) as id, sum(total_ejecutado) as total_ejecutado, sum(total_x_ejecutar) as total_x_ejecutar, 
                    sum(ejeutado_semana) as ejeutado_semana, sum(total_x_ejecutar-ejeutado_semana) as pendientes, max(fet) as fet
            from
            (
                select 1 as id, count(mt.id) as total_ejecutado, 0 as total_x_ejecutar, 0 as ejeutado_semana, Min(mt.end_programmed_date) as fet
                from mntc_tasks mt
                inner join mntc_garage E on mt.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id 
                where state = 'ended' and mt.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mt.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                union all
                select 1 as id, 0 as total_ejecutado, count(mt.id) as total_x_ejecutar, 0 as ejeutado_semana, Min(mt.end_programmed_date) as fet
                from mntc_tasks mt
                inner join mntc_garage E on mt.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where state = 'started' and mt.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mt.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                union all
                select 1 as id, 0 as total_ejecutado, 0 as total_x_ejecutar, count(mt.id) as ejeutado_semana, Min(mt.end_programmed_date) as fet 
                from mntc_tasks mt
                inner join mntc_workorder mw on mt.workorder_id = mw.id
                inner join mntc_garage E on mt.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mt.state = 'started' and mw.state = 'programmed' and mt.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mt.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                union all
                select 1 as id, 0 as total_ejecutado, 0 as total_x_ejecutar, 0 as ejeutado_semana, Max(mt.end_programmed_date) as fet 
                from mntc_tasks mt
                inner join mntc_garage E on mt.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mt.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mt.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
            ) main 
            group by id
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))


class mntc_accomplishment_indicator(models.Model):
    _name = "mntc.accomplishment.indicator"
    _description = "Indicador de cumplimiento de la programación"
    _auto = False

    tipo_ot = fields.Char(string='Tipo', readonly=True)
    equipos_programados = fields.Integer(string='Programados', readonly=True)
    equipos_ejecutados = fields.Integer(string='Ejecutados', readonly=True)
    tareas_programadas = fields.Integer(string='Tareas programadas', readonly=True)
    tareas_ejecutadas = fields.Integer(string='Tareas ejecutadas', readonly=True)
    cumplimiento = fields.Float(string='Cumplimiento', readonly=True)
    horas_planeadas = fields.Integer(string='Hrs planeadas', readonly=True)
    horas_ejecutadas = fields.Integer(string='Hrs ejecutadas', readonly=True)
    cumplimiento_hora = fields.Float(string='Cumplimiento Hrs', readonly=True)
    mttr_tarea = fields.Float(string='MTTR Tarea', readonly=True)


    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by A.type_mntc) as id, 
                    case when A.type_mntc = 'type_mntc_1' then 'Preventivo' 
                    when A.type_mntc = 'type_mntc_2' then 'Correctivo' 
                    when A.type_mntc = 'type_mntc_3' then 'Predictivo' 
                    when A.type_mntc = 'type_mntc_4' then 'Mejorativo' end as tipo_ot,
                    B.equipos_programados, C.equipos_ejecutados, D.tareas_programadas, E.tareas_ejecutadas, 
                    round(cast(C.equipos_ejecutados as numeric) / cast(B.equipos_programados as numeric) * 100, 2)  as cumplimiento,
                    F.horas_planeadas, G.horas_ejecutadas, round(cast(H.mttr_tarea as numeric), 2) as mttr_tarea,
                    round(cast(G.horas_ejecutadas as numeric) / cast(F.horas_planeadas as numeric) * 100, 2) as cumplimiento_hora
            from 
            (
                select type_mntc 
                from mntc_workorder mw2 
                group by type_mntc 
            ) A
            inner join 
            (
                -- equipos programados
                select count(fv.id) as equipos_programados, mw.type_mntc 
                from fleet_vehicle fv 
                inner join mntc_workorder mw on fv.id= mw.vehicle_id 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('programmed', 'in_progress', 'ended') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) B on A.type_mntc = B.type_mntc
            inner join 
            (
                -- equipos ejecutados
                select count(fv.id) as equipos_ejecutados, mw.type_mntc 
                from fleet_vehicle fv 
                inner join mntc_workorder mw on fv.id= mw.vehicle_id 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('ended') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) C on A.type_mntc = C.type_mntc
            inner join 
            (
                -- tareas programadas
                select count(mt.id) as tareas_programadas, mw.type_mntc 
                from mntc_tasks mt 
                inner join mntc_workorder mw on mt.workorder_id = mw.id 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('programmed', 'in_progress', 'ended') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) D on A.type_mntc = D.type_mntc
            inner join 
            (
                -- tareas ejecutadas
                select count(mt.id) as tareas_ejecutadas, mw.type_mntc 
                from mntc_tasks mt 
                inner join mntc_workorder mw on mt.workorder_id = mw.id 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('ended') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) E on A.type_mntc = E.type_mntc
            inner join 
            (
                -- horas planeadas
                select sum(date_part('hour', mw.end_programmed_date - mw.start_programmed_date)) as horas_planeadas, mw.type_mntc 
                from mntc_workorder mw 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('programmed', 'in_progress', 'ended') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) F on A.type_mntc = F.type_mntc
            inner join 
            (
                -- horas ejecutadas
                select sum(date_part('hour', mw.end_date - mw.start_date)) as horas_ejecutadas, mw.type_mntc 
                from mntc_workorder mw 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('ended') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) G on A.type_mntc = G.type_mntc
            inner join 
            (
                -- mttr tarea
                select sum(date_part('hour', mw.end_date - mw.start_date))/count(mt.id) as mttr_tarea, mw.type_mntc 
                from mntc_tasks mt 
                inner join mntc_workorder mw on mt.workorder_id = mw.id 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) H on A.type_mntc = H.type_mntc
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_week_schedule_indicator(models.Model):
    _name = "mntc.week.schedule.indicator"
    _description = "Indicador de cumplimiento de la programación"
    _auto = False

    tipo = fields.Char(string='Tipo', readonly=True)
    equipos_programados = fields.Integer(string='Equipos programados', readonly=True)
    tareas_programadas = fields.Integer(string='Tareas programadas', readonly=True)
    horas_planeadas = fields.Integer(string='Hrs planeadas', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by A.type_mntc) as id, 
                    case when A.type_mntc = 'type_mntc_1' then 'Preventivo' 
                    when A.type_mntc = 'type_mntc_2' then 'Correctivo' 
                    when A.type_mntc = 'type_mntc_3' then 'Predictivo' 
                    when A.type_mntc = 'type_mntc_4' then 'Mejorativo' end as tipo,
                    B.equipos_programados, D.tareas_programadas, F.horas_planeadas
            from 
            (
                select type_mntc 
                from mntc_workorder mw2 
                group by type_mntc 
            ) A
            inner join 
            (
                -- equipos programados
                select count(fv.id) as equipos_programados, mw.type_mntc 
                from fleet_vehicle fv 
                inner join mntc_workorder mw on fv.id= mw.vehicle_id 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('programmed', 'in_progress') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) B on A.type_mntc = B.type_mntc
            inner join 
            (
                -- tareas programadas
                select count(mt.id) as tareas_programadas, mw.type_mntc 
                from mntc_tasks mt 
                inner join mntc_workorder mw on mt.workorder_id = mw.id 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('programmed', 'in_progress') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) D on A.type_mntc = D.type_mntc
            inner join 
            (
                -- horas planeadas
                select sum(date_part('hour', mw.end_programmed_date - mw.start_programmed_date)) as horas_planeadas, mw.type_mntc 
                from mntc_workorder mw 
                inner join mntc_garage E on mw.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id  
                where mw.state in ('programmed', 'in_progress') and mw.type_mntc is not null 
                        and mw.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and mw.create_date <= '{filter_context.get('date_end', '1900-01-01')}' 
                        and F."name" = '{filter_context.get('branch_id', '')}' 
                group by mw.type_mntc
            ) F on A.type_mntc = F.type_mntc
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_weekly_work_indicator(models.Model):
    _name = "mntc.weekly.work.indicator"
    _description = "Indicador de trabajo de la semana no programado"
    _auto = False

    prioridad = fields.Char(string='Tipo', readonly=True)
    equipos = fields.Integer(string='Equipos', readonly=True)
    cant_tareas = fields.Integer(string='Tareas', readonly=True)
    horas_empleado = fields.Float(string='Hrs empleado', readonly=True)
    horas_contratista = fields.Float(string='Hrs contratista', readonly=True)
    mttr_tarea = fields.Float(string='MTTR tarea', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
            select row_number() over(order by A.priority) as id, case when A.priority = 'priority_1' then 'Emergencia' else 'Urgencia' end as prioridad, 		
                    round(cast(B.horas_contratista as numeric), 2) as horas_contratista, round(cast(B.horas_empleado as numeric), 2) as horas_empleado,
                    B.equipos, B.cant_tareas, round(cast(B.horas_empleado / B.cant_tareas as numeric), 2) as mttr_tarea
            from 
            (
                select 'priority_1' as priority 
                union all 
                select 'priority_2' as priority 
            ) A
            inner join 
            (
                -- emergencia
                select count(A.id) as equipos, sum(B.cant_tareas) as cant_tareas, sum(horas_contratista) as horas_contratista,
                        sum(horas_empleado) as horas_empleado, 'priority_1' as priority 
                from mntc_workorder A
                inner join mntc_garage E on A.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id
                inner join 
                ( 
                    select count(A.id) as cant_tareas, B.id 
                    from mntc_tasks A
                    inner join mntc_workorder B on A.workorder_id = B.id
                    inner join mntc_garage E on A.garage_id = E.id 
                    inner join zue_res_branch F on E.branch_id = F.id
                    where B.priority = 'priority_1' and F."name" = '{filter_context.get('branch_id', '')}' and A.create_date between '{filter_context.get('date_start', '1900-01-01')}' and '{filter_context.get('date_end', '1900-01-01')}'
                    group by B.id 
                ) B on A.id = B.id 
                inner join
                (
                    select sum(case when C.res_partner_id isnull then 0 else C.spent_time end) as horas_contratista, 
                            sum(case when C.res_partner_id isnull then C.spent_time else 0 end) as horas_empleado,
                            B.id
                    from mntc_tasks A
                    inner join mntc_workorder B on A.workorder_id = B.id 
                    inner join mntc_executed_workforce_type_rh C on A.id = C.task_id 
                    inner join mntc_garage E on B.garage_id = E.id 
                    inner join zue_res_branch F on E.branch_id = F.id
                    where B.priority = 'priority_1' and F."name" = '{filter_context.get('branch_id', '')}' and A.create_date between '{filter_context.get('date_start', '1900-01-01')}' and '{filter_context.get('date_end', '1900-01-01')}'
                    group by B.id
                ) C on A.id = C.id 
                where A.priority = 'priority_1' and F."name" = '{filter_context.get('branch_id', '')}' and A.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and A.create_date <= '{filter_context.get('date_end', '1900-01-01')}'
                union all
                -- urgencia
                select count(A.id) as equipos, sum(B.cant_tareas) as cant_tareas, sum(horas_contratista) as horas_contratista,
                        sum(horas_empleado) as horas_empleado, 'priority_2' as priority 
                from mntc_workorder A
                inner join mntc_garage E on A.garage_id = E.id 
                inner join zue_res_branch F on E.branch_id = F.id
                inner join 
                ( 
                    select count(A.id) as cant_tareas, B.id 
                    from mntc_tasks A
                    inner join mntc_workorder B on A.workorder_id = B.id
                    inner join mntc_garage E on A.garage_id = E.id 
                    inner join zue_res_branch F on E.branch_id = F.id
                    where B.priority = 'priority_2' and F."name" = '{filter_context.get('branch_id', '')}' and A.create_date between '{filter_context.get('date_start', '1900-01-01')}' and '{filter_context.get('date_end', '1900-01-01')}'
                    group by B.id 
                ) B on A.id = B.id 
                inner join
                (
                    select sum(case when C.res_partner_id isnull then 0 else C.spent_time end) as horas_contratista, 
                            sum(case when C.res_partner_id isnull then C.spent_time else 0 end) as horas_empleado,
                            B.id
                    from mntc_tasks A
                    inner join mntc_workorder B on A.workorder_id = B.id 
                    inner join mntc_executed_workforce_type_rh C on A.id = C.task_id 
                    inner join mntc_garage E on B.garage_id = E.id 
                    inner join zue_res_branch F on E.branch_id = F.id
                    where B.priority = 'priority_2' and F."name" = '{filter_context.get('branch_id', '')}' and A.create_date between '{filter_context.get('date_start', '1900-01-01')}' and '{filter_context.get('date_end', '1900-01-01')}'
                    group by B.id
                ) C on A.id = C.id 
                where A.priority = 'priority_2' and F."name" = '{filter_context.get('branch_id', '')}' and A.create_date >= '{filter_context.get('date_start', '1900-01-01')}' and A.create_date <= '{filter_context.get('date_end', '1900-01-01')}'
            ) B on A.priority = B.priority 
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))


class mntc_main_urgency_indicator(models.Model):
    _name = "mntc.main.urgency.indicator"
    _description = "Indicador de causas principales de urgencias"
    _auto = False

    num_tareas = fields.Integer(string='# Tareas', readonly=True)
    servicio = fields.Char(string='Servicio', readonly=True)
    sistema = fields.Char(string='Sistema', readonly=True)
    componente = fields.Char(string='Componente', readonly=True)
    parte = fields.Char(string='Parte', readonly=True)
    falla = fields.Char(string='Falla', readonly=True)
    accion = fields.Char(string='Acción', readonly=True)
    horas_hombre = fields.Integer(string='HH', readonly=True)
    costo = fields.Float(string='Costo', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
                select row_number() over(order by sucursal) as id, num_tareas, sucursal, servicio, 
                        sistema, componente, parte, falla, accion, horas_hombre, costo 
                from 
                (
                    select count(A.id) as num_tareas, J."name" as sucursal, H."name" as servicio, B."name" as sistema, 
                            C."name" as componente, D."name" as parte, E."name" as falla, F."name" as accion, 
                            sum(A.spent_time) as horas_hombre, sum(A.program_cost) as costo
                    from mntc_tasks A
                    left join mntc_vehicle_system B on A.system_id = B.id 
                    left join mntc_component C on A.component_id = C.id 
                    left join mntc_spare_part_type D on A.spare_part_type_id = D.id 
                    left join mntc_causes E on A.cause_id = E.id 
                    left join mntc_action_taken F on A.action_taken_id = F.id 
                    left join mntc_services_type H on A.service_type_id = H.id 
                    inner join mntc_workorder G on A.workorder_id = G.id and G.priority = 'priority_2'
                    inner join mntc_garage I on G.garage_id = I.id 
                    inner join zue_res_branch J on I.branch_id = J.id 
                    where J.name = '{filter_context.get('branch_id', '')}'
                            and A.create_date between '{filter_context.get('date_start', '1900-01-01')}' and '{filter_context.get('date_end', '1900-01-01')}'
                    group by J."name", H."name", B."name", C."name", D."name", E."name", F."name"
                    having count(A.id) > 1 
                ) main
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_draft_requests_indicator(models.Model):
    _name = "mntc.draft.requests.indicator"
    _description = "Indicador de solicitudes en borrador"
    _auto = False

    prioridad = fields.Char(string='Prioridad', readonly=True)
    metodo_d = fields.Char(string='Método de detección', readonly=True)
    cantidad = fields.Integer(string='Cantidad', readonly=True)
    observacion = fields.Char(string='Observación', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
                select row_number() over(order by prioridad) as id, prioridad, metodo_d, cantidad, observacion 
                from 
                (
                    select case when A.priority_id = 'priority_1' then 'EMERGENCIA'
                            when A.priority_id = 'priority_2' then 'URGENCIA'
                            when A.priority_id = 'priority_3' then 'PROGRAMADO' 
                            else 'NO DEFINIDO' end as prioridad, 
                            B."name" as metodo_d, count(A.id) as cantidad,
                            A.cancel_osbservation as observacion
                    from mntc_request A 
                    left join mntc_detection_methods B on A.detection_method = B.id
                    left join mntc_garage C on A.garage_id = C.id 
                    inner join zue_res_branch D on C.branch_id = D.id 
                    where state = 'draft' and date_part('days', now() - request_date) > 20  
                            and A.request_date between '{filter_context.get('date_start', '1900-01-01')}' and '{filter_context.get('date_end', '1900-01-01')}'
                            and D."name" = '{filter_context.get('branch_id', '')}'
                    group by A.priority_id, B."name", A.cancel_osbservation 
                ) main
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))

class mntc_pending_workorder_indicator(models.Model):
    _name = "mntc.pending.workorder.indicator"
    _description = "Indicador de solicitudes en borrador"
    _auto = False

    estado = fields.Char(string='Estado', readonly=True)
    cantidad = fields.Integer(string='Cantidad', readonly=True)
    horas_hombre = fields.Integer(string='HH', readonly=True)
    observacion = fields.Char(string='Observación', readonly=True)

    @api.model
    def _query(self,filter_context):
        return f'''
                select row_number() over(order by cantidad) as id, estado, cantidad , horas_hombre, observacion 
                from 
                (
                    select case when A.state = 'planeacion' then 'PLANEACIÓN'
                            when A.state = 'waiting_parts' then 'REPUESTO'
                            when A.state = 'programmed' then 'PROGRAMADA'
                            when A.state = 'in_progress' then 'EJECUCIÓN' end as estado,  
                            count(A.id) as cantidad, sum(spent_time) as horas_hombre, observation as observacion
                    from mntc_workorder A 
                    left join mntc_garage B on A.garage_id = B.id 
                    inner join zue_res_branch C on B.branch_id = C.id 
                    where state in ('planeacion', 'waiting_parts', 'programmed', 'in_progress')
                            and  date_part('days', now() - A.approved_date) > 20  
                            and A.approved_date between '{filter_context.get('date_start', '1900-01-01')}' and '{filter_context.get('date_end', '1900-01-01')}'
                            and C."name" = '{filter_context.get('branch_id', '')}'
                    group by A.state, A.observation 
                ) main
        '''

    def init(self,filter_context={}):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s 
                )
            ''' % (
            self._table, self._query(filter_context)
        ))
