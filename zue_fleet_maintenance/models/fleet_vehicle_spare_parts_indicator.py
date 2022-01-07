from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import base64
import io
import xlsxwriter

class mntc_vehicle_spare_parts_wizard(models.TransientModel):
    _name = 'mntc.vehicle.spare.parts.wizard'
    _description = 'Vista lista del informe de repuestos del vehículo'

    referencia = fields.Char('Referencia')
    scheduled_date = fields.Date('Fecha Programada')
    doc_origen = fields.Char('Doc. Origen')
    movil_nro = fields.Char('Móvil')
    placa_nro = fields.Char('Placa')
    producto = fields.Char('Producto')
    assigned_company = fields.Char('Compañia Asignada')
    initial_demand = fields.Integer('Demanda Inicial')
    reserved_availability = fields.Integer('Reservado')
    qty_done = fields.Integer('Hecho')
    a_mano = fields.Integer('Cantidad a Mano')
    state = fields.Char('Estado')
    AMTUR_BOGOExistencias = fields.Integer('AMTUR_BOGOExistencias')
    AMTUR_CARTExistencias = fields.Integer('AMTUR_CARTExistencias')
    AMTUR_GALBExistencias = fields.Integer('AMTUR_GALBExistencias')
    AMTUR_GFONExistencias = fields.Integer('AMTUR_GFONExistencias')
    AMTUR_GRIOExistencias = fields.Integer('AMTUR_GRIOExistencias')
    AMTUR_MONTExistencias = fields.Integer('AMTUR_MONTExistencias')
    GEAT_BOGOExistencias = fields.Integer('GEAT_BOGOExistencias')
    GEAT_CARTExistencias = fields.Integer('GEAT_CARTExistencias')
    GEAT_GALBExistencias = fields.Integer('GEAT_GALBExistencias')
    GEAT_GFONExistencias = fields.Integer('GEAT_GFONExistencias')
    GEAT_GRIOExistencias = fields.Integer('GEAT_GRIOExistencias')
    GEAT_MONTExistencias = fields.Integer('GEAT_MONTExistencias')
    UT_BOGOExistencias = fields.Integer('UT_BOGOExistencias')
    UT_CARTExistencias = fields.Integer('UT_CARTExistencias')
    UT_GALBExistencias = fields.Integer('UT_GALBExistencias')
    UT_GFONExistencias = fields.Integer('UT_GFONExistencias')
    UT_GRIOExistencias = fields.Integer('UT_GRIOExistencias')
    UT_MONTExistencias = fields.Integer('UT_MONTExistencias')

    def program_catalog(self):
        for record in self:
            view_tree = self.env['ir.ui.view'].search([('name', '=', 'mntc.workorder.tree.view')]).id
            view_form = self.env['ir.ui.view'].search([('name', '=', 'mntc.workorder.form.view')]).id
            view_graph = self.env['ir.ui.view'].search([('name', '=', 'mntc.workorder.graph')]).id
            window = {
                'name': 'Órden de trabajo',
                'view_mode': 'tree,form,graph',
                'views': [[view_tree, 'tree'], [view_form, 'form'], [view_graph, 'graph']],
                'res_model': 'mntc.workorder',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

            workorder_str = ','.join(map(str, workorder_lst))
            window['domain'] = "[('id','in',[" + workorder_str + "])]"

        return window

    def load_list(self):
        query = ''
        query = """select referencia, scheduled_date, doc_origen, movil_nro, placa_nro, producto, 
                            assigned_company, initial_demand, reserved_availability, qty_done, sum(a_mano) as a_mano, state,
                            sum(a_mano) filter (where ubicacion='AMTUR_BOGOExistencias') as AMTUR_BOGOExistencias,
                            sum(a_mano) filter (where ubicacion='AMTUR_CARTExistencias') as AMTUR_CARTExistencias,
                            sum(a_mano) filter (where ubicacion='AMTUR_GALBExistencias') as AMTUR_GALBExistencias,
                            sum(a_mano) filter (where ubicacion='AMTUR_GFONExistencias') as AMTUR_GFONExistencias,
                            sum(a_mano) filter (where ubicacion='AMTUR_GRIOExistencias') as AMTUR_GRIOExistencias,
                            sum(a_mano) filter (where ubicacion='AMTUR_MONTExistencias') as AMTUR_MONTExistencias,
                            sum(a_mano) filter (where ubicacion='GEAT_BOGOExistencias') as GEAT_BOGOExistencias,
                            sum(a_mano) filter (where ubicacion='GEAT_CARTExistencias') as GEAT_CARTExistencias,
                            sum(a_mano) filter (where ubicacion='GEAT_GALBExistencias') as GEAT_GALBExistencias,
                            sum(a_mano) filter (where ubicacion='GEAT_GFONExistencias') as GEAT_GFONExistencias,
                            sum(a_mano) filter (where ubicacion='GEAT_GRIOExistencias') as GEAT_GRIOExistencias,
                            sum(a_mano) filter (where ubicacion='GEAT_MONTExistencias') as GEAT_MONTExistencias,
                            sum(a_mano) filter (where ubicacion='UT_BOGOExistencias') as UT_BOGOExistencias,
                            sum(a_mano) filter (where ubicacion='UT_CARTExistencias') as UT_CARTExistencias,
                            sum(a_mano) filter (where ubicacion='UT_GALBExistencias') as UT_GALBExistencias,
                            sum(a_mano) filter (where ubicacion='UT_GFONExistencias') as UT_GFONExistencias,
                            sum(a_mano) filter (where ubicacion='UT_GRIOExistencias') as UT_GRIOExistencias,
                            sum(a_mano) filter (where ubicacion='UT_MONTExistencias') as UT_MONTExistencias
                    from 
                    (
                        select A."name" as referencia, scheduled_date, B."number" as doc_origen, C.movil_nro, C.placa_nro,
                                E."name" as producto, ZA.state, k."name" as assigned_company, ZA.product_uom_qty as initial_demand, 
                                J.product_qty as reserved_availability, J.qty_done, replace(replace(I.x_business_name, ' ', '_'), '.', '') || '_' ||
                                replace(replace(replace(replace(replace(replace(H.complete_name, ' - ', '_'), '/', ''), '(', ''), ')', ''), ' ', '_'), ':', '') as ubicacion, 
                                ZA.company_id, sum(F.quantity) as a_mano
                        from stock_move ZA
                        left join stock_picking A on ZA.picking_id = A.id 
                        left join mntc_workorder B on A.workorder_id = B.id 
                        left join fleet_vehicle C on B.vehicle_id = C.id 
                        inner join product_product D on ZA.product_id = D.id 
                        inner join product_template E on D.product_tmpl_id = E.id 
                        inner join stock_quant F on D.id = F.product_id 
                        inner join res_company G on ZA.company_id = G.id 
                        inner join stock_location H on F.location_id = H.id and substring(H.complete_name, 1, 17) not in ('Virtual Locations', 'Partner Locations') 
                        inner join res_partner I on G.partner_id = I.id 
                        left join stock_move_line J on ZA.id = J.move_id 
                        left join res_company K on C.assigned_company_id = K.id 
                        where A.workorder_id notnull and ZA.state not in ('done', 'cancel') 
                        group by A."name", scheduled_date, B."number", C.movil_nro, C.placa_nro, E."name", 
                                ZA.state, k."name", ZA.product_uom_qty, J.product_qty, J.qty_done, I.x_business_name, 
                                H.complete_name, ZA.company_id
                        order by A."name"
                    ) AS a
                    group by referencia, scheduled_date, doc_origen, movil_nro, placa_nro, producto, 
                            assigned_company, initial_demand, reserved_availability, qty_done, state 
                    order by referencia 
                """

        self._cr.execute(query)
        _res = self._cr.dictfetchall()
        to_create = []

        for rows in _res:
            vals = {
                'referencia': rows['referencia'],
                'scheduled_date': rows['scheduled_date'],
                'doc_origen': rows['doc_origen'],
                'movil_nro': rows['movil_nro'],
                'placa_nro': rows['placa_nro'],
                'producto': rows['producto'],
                'assigned_company': rows['assigned_company'],
                'initial_demand': rows['initial_demand'],
                'reserved_availability': rows['reserved_availability'],
                'qty_done': rows['qty_done'],
                'a_mano': rows['a_mano'],
                'state': rows['state'],
                'AMTUR_BOGOExistencias': rows['amtur_bogoexistencias'],
                'AMTUR_CARTExistencias': rows['amtur_cartexistencias'],
                'AMTUR_GALBExistencias': rows['amtur_galbexistencias'],
                'AMTUR_GFONExistencias': rows['amtur_gfonexistencias'],
                'AMTUR_GRIOExistencias': rows['amtur_grioexistencias'],
                'AMTUR_MONTExistencias': rows['amtur_montexistencias'],
                'GEAT_BOGOExistencias': rows['geat_bogoexistencias'],
                'GEAT_CARTExistencias': rows['geat_cartexistencias'],
                'GEAT_GALBExistencias': rows['geat_galbexistencias'],
                'GEAT_GFONExistencias': rows['geat_gfonexistencias'],
                'GEAT_GRIOExistencias': rows['geat_grioexistencias'],
                'GEAT_MONTExistencias': rows['geat_montexistencias'],
                'UT_BOGOExistencias': rows['ut_bogoexistencias'],
                'UT_CARTExistencias': rows['ut_cartexistencias'],
                'UT_GALBExistencias': rows['ut_galbexistencias'],
                'UT_GFONExistencias': rows['ut_gfonexistencias'],
                'UT_GRIOExistencias': rows['ut_grioexistencias'],
                'UT_MONTExistencias': rows['ut_montexistencias']
            }
            to_create.append(vals)

        created_wo = self.create(to_create)
        return True


class mntc_vehicle_spare_parts_indicator(models.TransientModel):
    _name = 'mntc.vehicle.spare.parts.indicator'
    _description = 'Generador del informe de repuestos del vehículo'

    company_id = fields.Many2one('res.company', 'Compañia')
    excel_file = fields.Binary('Excel Valores base file')
    excel_file_name = fields.Char('Excel Valores base filename')

    def open_program_wizard(self):
        program_wizard_pool = self.env['mntc.vehicle.spare.parts.wizard']
        for program in program_wizard_pool.search([('create_uid', '=', self.env.uid)]):
            program[0].unlink()

        program_wizard_pool.load_list()

        view_tree_id = self.env['ir.ui.view'].search([('name', '=', 'mntc.vehicle.spare.parts.wizard.tree')])
        view_form_id = self.env['ir.ui.view'].search([('name', '=', 'mntc.vehicle.spare.parts.wizard.form')])

        res = {
            'name': 'Asistente rango de programación',
            'view_mode': 'tree',
            'views': [[view_tree_id.id, 'tree'], [view_form_id.id, 'form']],
            'res_model': 'mntc.vehicle.spare.parts.wizard',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('create_uid', '=', self.env.uid)],
        }
        return res

    def get_query(self):
        tmp_company = 0
        columns = ''

        if self.company_id:
            tmp_company = self.company_id.id

            if tmp_company == 1:
                columns = """Select referencia, scheduled_date, doc_origen, marca, modelo, movil_nro, placa_nro, producto, default_code, 
                                assigned_company, initial_demand, reserved_availability, qty_done, a_mano, state,
                                AMTUR_BOGOExistencias, AMTUR_CARTExistencias, AMTUR_GALBExistencias, AMTUR_GFONExistencias,
                                AMTUR_GRIOExistencias, AMTUR_MONTExistencias """
            elif tmp_company == 3:
                columns = """Select referencia, scheduled_date, doc_origen, marca, modelo, movil_nro, placa_nro, producto, default_code,
                                assigned_company, initial_demand, reserved_availability, qty_done, a_mano, state,
                                GEAT_BOGOExistencias, GEAT_CARTExistencias, GEAT_GALBExistencias, GEAT_GFONExistencias,
                                GEAT_GRIOExistencias, GEAT_MONTExistencias """
            elif tmp_company == 4:
                columns = """Select referencia, scheduled_date, doc_origen, marca, modelo, movil_nro, placa_nro, producto, default_code,
                                assigned_company, initial_demand, reserved_availability, qty_done, a_mano, state,
                                UT_BOGOExistencias, UT_CARTExistencias, UT_GALBExistencias, UT_GFONExistencias, 
                                UT_GRIOExistencias, UT_MONTExistencias """
        else:
            columns = """Select * """

        if tmp_company:
            filter_company = """ and ZA.company_id = %s"""%(tmp_company)
        else:
            filter_company = """ and 1 = 1 """

        query = columns + """from
                    (
                        select referencia, scheduled_date, doc_origen, marca, modelo, movil_nro, placa_nro, producto, default_code, 
                                assigned_company, initial_demand, reserved_availability, qty_done, sum(a_mano) as a_mano, state,
                                sum(a_mano) filter (where ubicacion='AMTUR_BOGOExistencias') as AMTUR_BOGOExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_CARTExistencias') as AMTUR_CARTExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_GALBExistencias') as AMTUR_GALBExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_GFONExistencias') as AMTUR_GFONExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_GRIOExistencias') as AMTUR_GRIOExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_MONTExistencias') as AMTUR_MONTExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_BOGOExistencias') as GEAT_BOGOExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_CARTExistencias') as GEAT_CARTExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_GALBExistencias') as GEAT_GALBExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_GFONExistencias') as GEAT_GFONExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_GRIOExistencias') as GEAT_GRIOExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_MONTExistencias') as GEAT_MONTExistencias,
                                sum(a_mano) filter (where ubicacion='UT_BOGOExistencias') as UT_BOGOExistencias,
                                sum(a_mano) filter (where ubicacion='UT_CARTExistencias') as UT_CARTExistencias,
                                sum(a_mano) filter (where ubicacion='UT_GALBExistencias') as UT_GALBExistencias,
                                sum(a_mano) filter (where ubicacion='UT_GFONExistencias') as UT_GFONExistencias,
                                sum(a_mano) filter (where ubicacion='UT_GRIOExistencias') as UT_GRIOExistencias,
                                sum(a_mano) filter (where ubicacion='UT_MONTExistencias') as UT_MONTExistencias,
                                sum(a_mano) filter (where ubicacion isnull) as UBICACION_NULA
                        from 
                        (
                            select A."name" as referencia, scheduled_date, B."number" as doc_origen, L."name" as modelo, M."name" as marca, C.movil_nro, C.placa_nro,
                                    E."name" as producto, E.default_code, ZA.state, k."name" as assigned_company, ZA.product_uom_qty as initial_demand, 
                                    J.product_qty as reserved_availability, J.qty_done, replace(replace(I.x_business_name, ' ', '_'), '.', '') || '_' ||
                                    replace(replace(replace(replace(replace(replace(H.complete_name, ' - ', '_'), '/', ''), '(', ''), ')', ''), ' ', '_'), ':', '') as ubicacion, 
                                    ZA.company_id, sum(F.quantity) as a_mano
                            from stock_move ZA
                            left join stock_picking A on ZA.picking_id = A.id 
                            left join mntc_workorder B on A.workorder_id = B.id 
                            left join fleet_vehicle C on B.vehicle_id = C.id 
                            inner join product_product D on ZA.product_id = D.id 
                            inner join product_template E on D.product_tmpl_id = E.id 
                            left join stock_quant F on D.id = F.product_id 
                            inner join res_company G on F.company_id = G.id 
                            left join stock_location H on F.location_id = H.id  
                            inner join res_partner I on G.partner_id = I.id 
                            left join stock_move_line J on ZA.id = J.move_id 
                            left join res_company K on C.assigned_company_id = K.id 
                            inner join fleet_vehicle_model L on C.model_id = L.id 
                            inner join fleet_vehicle_model_brand M on L.brand_id = M.id 
                            where ZA.state not in ('done', 'cancel') """ + filter_company + """ 
                                    and (H.complete_name isnull or substring(H.complete_name, 1, 17) not in ('Virtual Locations', 'Partner Locations'))
                            group by A."name", scheduled_date, B."number", L."name", M."name", C.movil_nro, C.placa_nro, E."name", E.default_code, 
                                    ZA.state, k."name", ZA.product_uom_qty, J.product_qty, J.qty_done, I.x_business_name, 
                                    H.complete_name, ZA.company_id
                            order by A."name"
                        ) AS a
                        group by referencia, scheduled_date, doc_origen, marca, modelo, movil_nro, placa_nro, producto, default_code, 
                                assigned_company, initial_demand, reserved_availability, qty_done, state 
                    ) A
                    order by A.referencia 
                """
        return query

    def get_query_proy(self):
        tmp_company = 0
        columns = ''

        if self.company_id:
            tmp_company = self.company_id.id

            if tmp_company == 1:
                columns = """Select producto, default_code, solicitado, reference, proyectado, a_mano, fecha_inicial, fecha_final,  
                                AMTUR_BOGOExistencias, AMTUR_CARTExistencias, AMTUR_GALBExistencias, AMTUR_GFONExistencias,
                                AMTUR_GRIOExistencias, AMTUR_MONTExistencias """
            elif tmp_company == 3:
                columns = """Select producto, default_code, solicitado, reference, proyectado, a_mano, fecha_inicial, fecha_final,  
                                GEAT_BOGOExistencias, GEAT_CARTExistencias, GEAT_GALBExistencias, GEAT_GFONExistencias,
                                GEAT_GRIOExistencias, GEAT_MONTExistencias """
            elif tmp_company == 4:
                columns = """Select producto, default_code, solicitado, reference, proyectado, a_mano, fecha_inicial, fecha_final,  
                                UT_BOGOExistencias, UT_CARTExistencias, UT_GALBExistencias, UT_GFONExistencias, 
                                UT_GRIOExistencias, UT_MONTExistencias """
        else:
            columns = """Select * """

        if tmp_company:
            filter_company = """ and A.company_id = %s"""%(tmp_company)
            filter_company_stock = """ and G.company_id = %s"""%(tmp_company)
        else:
            filter_company = """ and 1 = 1 """
            filter_company_stock = """ and G.company_id notnull """


        query = columns + """from
                    (
                        select producto, default_code, product_qty as solicitado, reference, sum(proyectado) as proyectado, 
                                coalesce(a_mano, 0) as a_mano, fecha_inicial, fecha_final, 		
                                sum(proyectado) filter (where ubicacion='AMTUR_BOGOExistencias') as AMTUR_BOGOExistencias,
                                sum(proyectado) filter (where ubicacion='AMTUR_CARTExistencias') as AMTUR_CARTExistencias,
                                sum(proyectado) filter (where ubicacion='AMTUR_GALBExistencias') as AMTUR_GALBExistencias,
                                sum(proyectado) filter (where ubicacion='AMTUR_GFONExistencias') as AMTUR_GFONExistencias,
                                sum(proyectado) filter (where ubicacion='AMTUR_GRIOExistencias') as AMTUR_GRIOExistencias,
                                sum(proyectado) filter (where ubicacion='AMTUR_MONTExistencias') as AMTUR_MONTExistencias,
                                sum(proyectado) filter (where ubicacion='AMTUR_Partner_LocationsCustomers') as AMTUR_Partner_LocationsCustomers,
                                sum(proyectado) filter (where ubicacion='AMTUR_Partner_LocationsVendors') as AMTUR_Partner_LocationsVendors,
                                sum(proyectado) filter (where ubicacion='GEAT_BOGOExistencias') as GEAT_BOGOExistencias,
                                sum(proyectado) filter (where ubicacion='GEAT_CARTExistencias') as GEAT_CARTExistencias,
                                sum(proyectado) filter (where ubicacion='GEAT_GALBExistencias') as GEAT_GALBExistencias,
                                sum(proyectado) filter (where ubicacion='GEAT_GFONExistencias') as GEAT_GFONExistencias,
                                sum(proyectado) filter (where ubicacion='GEAT_GRIOExistencias') as GEAT_GRIOExistencias,
                                sum(proyectado) filter (where ubicacion='GEAT_MONTExistencias') as GEAT_MONTExistencias,
                                sum(proyectado) filter (where ubicacion='GEAT_Partner_LocationsCustomers') as GEAT_Partner_LocationsCustomers,
                                sum(proyectado) filter (where ubicacion='GEAT_Partner_LocationsVendors') as GEAT_Partner_LocationsVendors,
                                sum(proyectado) filter (where ubicacion='UT_BOGOExistencias') as UT_BOGOExistencias,
                                sum(proyectado) filter (where ubicacion='UT_CARTExistencias') as UT_CARTExistencias,
                                sum(proyectado) filter (where ubicacion='UT_GALBExistencias') as UT_GALBExistencias,
                                sum(proyectado) filter (where ubicacion='UT_GFONExistencias') as UT_GFONExistencias,
                                sum(proyectado) filter (where ubicacion='UT_GRIOExistencias') as UT_GRIOExistencias,
                                sum(proyectado) filter (where ubicacion='UT_MONTExistencias') as UT_MONTExistencias,
                                sum(proyectado) filter (where ubicacion='UT_Partner_LocationsCustomers') as UT_Partner_LocationsCustomers,
                                sum(proyectado) filter (where ubicacion='UT_Partner_LocationsVendors') as UT_Partner_LocationsVendors
                        from 
                        (
                            select F."name" as producto, F.default_code, D.proyectado, sum(G.quantity) as a_mano, D.fecha_inicial,
                                    D.fecha_final, D.ubicacion, A.reference, A.product_qty 
                            from stock_move A
                            inner join stock_picking B on A.picking_id = B.id 
                            left join mntc_workorder C on B.workorder_id = C.id 
                            inner join 
                            (
                                select A.product_id, A.product_qty as proyectado, min(A."date") as fecha_inicial, max(A."date") as fecha_final, 
                                        replace(replace(I.x_business_name, ' ', '_'), '.', '') || '_' ||
                                        replace(replace(replace(replace(replace(replace(C.complete_name, ' - ', '_'), '/', ''), '(', ''), ')', ''), ' ', '_'), ':', '') as ubicacion
                                from report_stock_quantity A 
                                inner join stock_warehouse B on A.warehouse_id = B.id
                                inner join stock_location C on B.lot_stock_id = C.id 
                                inner join res_company G on A.company_id = G.id 
                                inner join res_partner I on G.partner_id = I.id 
                                where A."date" > now() """ + filter_company + """ 
                                group  by A.product_id, A.product_qty, I.x_business_name, C.complete_name 
                            ) D on D.product_id = A.product_id 
                            inner join product_product E on A.product_id = E.id 
                            inner join product_template F on E.product_tmpl_id = F.id 
                            left join stock_quant G on A.product_id = G.product_id and G.quantity > 0 """ + filter_company_stock + """ 
                            where A.state not in ('draft', 'done', 'cancel') """ + filter_company + """ 
                            group by F."name", F.default_code, D.proyectado, D.fecha_inicial, D.fecha_final, D.ubicacion, A.reference, A.product_qty 
                        ) main
                        group by producto, default_code, fecha_inicial, fecha_final, reference, product_qty, a_mano
                    ) A
                    order by A.producto 
                """
        return query

    def export_excel(self):
        query_a_mano, query_proy = '', ''

        query_a_mano = self.get_query()
        query_proy = self.get_query_proy()

        # Generar EXCEL
        filename = 'Reporte de seguimiento vehículos en espera.xlsx'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})

        tmp_company = 0
        if self.company_id:
            tmp_company = self.company_id.id
            # Amtur
            if tmp_company == 1:
                columns = ['Referencia', 'Fecha Programada', 'Doc. Origen', 'Marca', 'Modelo', 'Movil', 'Placa', 'Producto', 'Referencia Interna',
                           'Compañia Asignada', 'Demanda Inicial', 'Reservado', 'Hecho', 'Cantidad a Mano', 'Estado',
                           'AMTUR_BOGOExistencias', 'AMTUR_CARTExistencias', 'AMTUR_GALBExistencias',
                           'AMTUR_GFONExistencias', 'AMTUR_GRIOExistencias', 'AMTUR_MONTExistencias']

                columns_proy = ['Producto', 'Referencia Interna', 'Solicitado', 'Referencia', 'Proyectado', 'A mano', 'Fecha Inicial', 'Fecha Final',
                               'AMTUR_BOGOExistencias', 'AMTUR_CARTExistencias', 'AMTUR_GALBExistencias',
                               'AMTUR_GFONExistencias', 'AMTUR_GRIOExistencias', 'AMTUR_MONTExistencias']
            # GEAT
            elif tmp_company == 3:
                columns = ['Referencia', 'Fecha Programada', 'Doc. Origen', 'Marca', 'Modelo', 'Movil', 'Placa', 'Producto', 'Referencia Interna',
                           'Compañia Asignada', 'Demanda Inicial', 'Reservado', 'Hecho', 'Cantidad a Mano', 'Estado',
                           'GEAT_BOGOExistencias', 'GEAT_CARTExistencias', 'GEAT_GALBExistencias', 'GEAT_GFONExistencias',
                           'GEAT_GRIOExistencias', 'GEAT_MONTExistencias']

                columns_proy = ['Producto', 'Referencia Interna', 'Solicitado', 'Referencia', 'Proyectado', 'A mano', 'Fecha Inicial', 'Fecha Final',
                               'GEAT_BOGOExistencias', 'GEAT_CARTExistencias', 'GEAT_GALBExistencias',
                               'GEAT_GFONExistencias',
                               'GEAT_GRIOExistencias', 'GEAT_MONTExistencias']
            # UT
            elif tmp_company == 4:
                columns = ['Referencia', 'Fecha Programada', 'Doc. Origen', 'Marca', 'Modelo', 'Movil', 'Placa', 'Producto', 'Referencia Interna',
                           'Compañia Asignada', 'Demanda Inicial', 'Reservado', 'Hecho', 'Cantidad a Mano', 'Estado',
                           'UT_BOGOExistencias', 'UT_CARTExistencias', 'UT_GALBExistencias', 'UT_GFONExistencias',
                           'UT_GRIOExistencias', 'UT_MONTExistencias']

                columns_proy = ['Producto', 'Referencia Interna', 'Solicitado', 'Referencia', 'Proyectado', 'A mano', 'Fecha Inicial', 'Fecha Final',
                               'UT_BOGOExistencias', 'UT_CARTExistencias', 'UT_GALBExistencias', 'UT_GFONExistencias',
                               'UT_GRIOExistencias', 'UT_MONTExistencias']
        else:
            columns = ['Referencia', 'Fecha Programada', 'Doc. Origen', 'Marca', 'Modelo', 'Movil', 'Placa', 'Producto', 'Referencia Interna',
                       'Compañia Asignada', 'Demanda Inicial', 'Reservado', 'Hecho', 'Cantidad a Mano', 'Estado',
                       'AMTUR_BOGOExistencias', 'AMTUR_CARTExistencias', 'AMTUR_GALBExistencias',
                       'AMTUR_GFONExistencias', 'AMTUR_GRIOExistencias', 'AMTUR_MONTExistencias',
                       'AMTUR_Partner_LocationsCustomers', 'AMTUR_Partner_LocationsVendors',
                       'GEAT_BOGOExistencias', 'GEAT_CARTExistencias', 'GEAT_GALBExistencias', 'GEAT_GFONExistencias',
                       'GEAT_GRIOExistencias', 'GEAT_MONTExistencias', 'GEAT_Partner_LocationsCustomers',
                       'GEAT_Partner_LocationsVendors', 'UT_BOGOExistencias', 'UT_CARTExistencias', 'UT_GALBExistencias',
                       'UT_GFONExistencias', 'UT_GRIOExistencias', 'UT_MONTExistencias']

            columns_proy = ['Producto', 'Referencia Interna', 'Solicitado', 'Referencia', 'Proyectado', 'A mano', 'Fecha Inicial', 'Fecha Final',
                           'AMTUR_BOGOExistencias', 'AMTUR_CARTExistencias', 'AMTUR_GALBExistencias',
                           'AMTUR_GFONExistencias', 'AMTUR_GRIOExistencias', 'AMTUR_MONTExistencias',
                           'AMTUR_Partner_LocationsCustomers', 'AMTUR_Partner_LocationsVendors',
                           'GEAT_BOGOExistencias', 'GEAT_CARTExistencias', 'GEAT_GALBExistencias', 'GEAT_GFONExistencias',
                           'GEAT_GRIOExistencias', 'GEAT_MONTExistencias', 'GEAT_Partner_LocationsCustomers',
                           'GEAT_Partner_LocationsVendors', 'UT_BOGOExistencias', 'UT_CARTExistencias',
                           'UT_GALBExistencias',
                           'UT_GFONExistencias', 'UT_GRIOExistencias', 'UT_MONTExistencias']

        # A mano
        sheet_a_mano = book.add_worksheet('CANTIDAD A MANO')
        aument_columns = 0

        for columns in columns:
            sheet_a_mano.write(0, aument_columns, columns)
            aument_columns = aument_columns + 1

        self._cr.execute(query_a_mano)
        result_query = self._cr.dictfetchall()
        aument_columns = 0
        aument_rows = 1
        for query in result_query:
            for row in query.values():
                sheet_a_mano.write(aument_rows, aument_columns, row)
                aument_columns = aument_columns + 1
            aument_rows = aument_rows + 1
            aument_columns = 0

        # Proyectado
        sheet_proyectado = book.add_worksheet('PROYECTADO')
        aument_columns = 0

        for columns in columns_proy:
            sheet_proyectado.write(0, aument_columns, columns)
            aument_columns = aument_columns + 1

        self._cr.execute(query_proy)
        result_query = self._cr.dictfetchall()
        aument_columns = 0
        aument_rows = 1
        for query in result_query:
            for row in query.values():
                sheet_proyectado.write(aument_rows, aument_columns, row)
                aument_columns = aument_columns + 1
            aument_rows = aument_rows + 1
            aument_columns = 0

        book.close()
        self.write({
            'excel_file': base64.encodestring(stream.getvalue()),
            'excel_file_name': filename,
        })

        action = {
            'name': 'Export Seguimiento de vehiculos',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=mntc.vehicle.spare.parts.indicator&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action