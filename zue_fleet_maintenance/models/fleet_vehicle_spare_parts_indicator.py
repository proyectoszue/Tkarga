from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import base64
import io
import xlsxwriter

class mntc_vehicle_spare_parts_indicator(models.TransientModel):
    _name = 'mntc.vehicle.spare.parts.indicator'
    _description = 'Generador del informe de repuestos del vehículo'

    company_id = fields.Many2one('res.company', 'Compañia')
    excel_file = fields.Binary('Excel Valores base file')
    excel_file_name = fields.Char('Excel Valores base filename')

    def get_query(self):
        tmp_company = 0
        columns = ''

        if self.company_id:
            tmp_company = self.company_id.id

            if tmp_company == 1:
                columns = """Select referencia, scheduled_date, doc_origen, movil_nro, placa_nro, producto,
                                reserved_availability, qty_done, state,
                                AMTUR_BOGOExistencias, AMTUR_CARTExistencias, AMTUR_GALBExistencias, AMTUR_GFONExistencias,
                                AMTUR_GRIOExistencias, AMTUR_MONTExistencias, AMTUR_Partner_LocationsCustomers, 
                                AMTUR_Partner_LocationsVendors """
            elif tmp_company == 3:
                columns = """Select referencia, scheduled_date, doc_origen, movil_nro, placa_nro, producto,
                                reserved_availability, qty_done, state,
                                GEAT_BOGOExistencias, GEAT_CARTExistencias, GEAT_GALBExistencias, GEAT_GFONExistencias,
                                GEAT_GRIOExistencias, GEAT_MONTExistencias, GEAT_Partner_LocationsCustomers, 
                                GEAT_Partner_LocationsVendors """
            elif tmp_company == 4:
                columns = """Select referencia, scheduled_date, doc_origen, movil_nro, placa_nro, producto,
                                reserved_availability, qty_done, state,
                                UT_BOGOExistencias, UT_CARTExistencias, UT_GALBExistencias, UT_GFONExistencias, UT_GRIOExistencias,
                                UT_MONTExistencias, UT_Partner_LocationsCustomers, UT_Partner_LocationsVendors """
        else:
            columns = """Select * """

        if tmp_company:
            filter_company = """ and ZA.company_id = %s"""%(tmp_company)
        else:
            filter_company = """ and 1 = 1 """

        query = columns + """from
                    (
                        select referencia, scheduled_date, doc_origen, movil_nro, placa_nro, producto, 
                                reserved_availability, qty_done, state,
                                sum(a_mano) filter (where ubicacion='AMTUR_BOGOExistencias') as AMTUR_BOGOExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_CARTExistencias') as AMTUR_CARTExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_GALBExistencias') as AMTUR_GALBExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_GFONExistencias') as AMTUR_GFONExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_GRIOExistencias') as AMTUR_GRIOExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_MONTExistencias') as AMTUR_MONTExistencias,
                                sum(a_mano) filter (where ubicacion='AMTUR_Partner_LocationsCustomers') as AMTUR_Partner_LocationsCustomers,
                                sum(a_mano) filter (where ubicacion='AMTUR_Partner_LocationsVendors') as AMTUR_Partner_LocationsVendors,
                                sum(a_mano) filter (where ubicacion='GEAT_BOGOExistencias') as GEAT_BOGOExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_CARTExistencias') as GEAT_CARTExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_GALBExistencias') as GEAT_GALBExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_GFONExistencias') as GEAT_GFONExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_GRIOExistencias') as GEAT_GRIOExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_MONTExistencias') as GEAT_MONTExistencias,
                                sum(a_mano) filter (where ubicacion='GEAT_Partner_LocationsCustomers') as GEAT_Partner_LocationsCustomers,
                                sum(a_mano) filter (where ubicacion='GEAT_Partner_LocationsVendors') as GEAT_Partner_LocationsVendors,
                                sum(a_mano) filter (where ubicacion='UT_BOGOExistencias') as UT_BOGOExistencias,
                                sum(a_mano) filter (where ubicacion='UT_CARTExistencias') as UT_CARTExistencias,
                                sum(a_mano) filter (where ubicacion='UT_GALBExistencias') as UT_GALBExistencias,
                                sum(a_mano) filter (where ubicacion='UT_GFONExistencias') as UT_GFONExistencias,
                                sum(a_mano) filter (where ubicacion='UT_GRIOExistencias') as UT_GRIOExistencias,
                                sum(a_mano) filter (where ubicacion='UT_MONTExistencias') as UT_MONTExistencias,
                                sum(a_mano) filter (where ubicacion='UT_Partner_LocationsCustomers') as UT_Partner_LocationsCustomers,
                                sum(a_mano) filter (where ubicacion='UT_Partner_LocationsVendors') as UT_Partner_LocationsVendors
                        from 
                        (
                            select A."name" as referencia, scheduled_date, B."number" as doc_origen, C.movil_nro, C.placa_nro,
                                    E."name" as producto, ZA.state, J.product_qty as reserved_availability, J.qty_done,  
                                    replace(replace(I.x_business_name, ' ', '_'), '.', '') || '_' ||
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
                            inner join stock_location H on F.location_id = H.id and substring(H.complete_name, 1, 17) != 'Virtual Locations' 
                            inner join res_partner I on G.partner_id = I.id 
                            left join stock_move_line J on ZA.id = J.move_id 
                            where A.workorder_id notnull and ZA.state not in ('done', 'cancel') """ + filter_company + """ 
                            group by A."name", scheduled_date, B."number", C.movil_nro, C.placa_nro, E."name", 
                                    ZA.state, J.product_qty, J.qty_done, I.x_business_name, H.complete_name, ZA.company_id
                            order by A."name"
                        ) AS a
                        group by referencia, scheduled_date, doc_origen, movil_nro, placa_nro, producto, reserved_availability, qty_done, state 
                    ) A
                    order by A.referencia 
                """
        return query

    def export_excel(self):
        query_a_mano = ''

        query_a_mano = self.get_query()

        # Generar EXCEL
        filename = 'Reporte de seguimiento vehículos en espera.xlsx'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})

        tmp_company = 0
        if self.company_id:
            tmp_company = self.company_id.id

            if tmp_company == 1:
                columns = ['Referencia', 'Fecha Programada', 'Doc. Origen', 'Movil', 'Placa', 'Producto',
                           'Reservado', 'Hecho', 'Estado', 'AMTUR_BOGOExistencias',
                           'AMTUR_CARTExistencias', 'AMTUR_GALBExistencias', 'AMTUR_GFONExistencias', 'AMTUR_GRIOExistencias',
                           'AMTUR_MONTExistencias', 'AMTUR_Partner_LocationsCustomers', 'AMTUR_Partner_LocationsVendors']
            elif tmp_company == 3:
                columns = ['Referencia', 'Fecha Programada', 'Doc. Origen', 'Movil', 'Placa', 'Producto',
                           'Reservado', 'Hecho', 'Estado',
                           'GEAT_BOGOExistencias', 'GEAT_CARTExistencias', 'GEAT_GALBExistencias', 'GEAT_GFONExistencias',
                           'GEAT_GRIOExistencias', 'GEAT_MONTExistencias', 'GEAT_Partner_LocationsCustomers',
                           'GEAT_Partner_LocationsVendors']
            elif tmp_company == 4:
                columns = ['Referencia', 'Fecha Programada', 'Doc. Origen', 'Movil', 'Placa', 'Producto',
                           'Reservado', 'Hecho', 'Estado',
                           'UT_BOGOExistencias', 'UT_CARTExistencias', 'UT_GALBExistencias', 'UT_GFONExistencias',
                           'UT_GRIOExistencias', 'UT_MONTExistencias', 'UT_Partner_LocationsCustomers',
                           'UT_Partner_LocationsVendors']
        else:
            columns = ['Referencia', 'Fecha Programada', 'Doc. Origen', 'Movil', 'Placa', 'Producto',
                       'Reservado', 'Hecho', 'Estado', 'AMTUR_BOGOExistencias',
                       'AMTUR_CARTExistencias', 'AMTUR_GALBExistencias', 'AMTUR_GFONExistencias', 'AMTUR_GRIOExistencias',
                       'AMTUR_MONTExistencias', 'AMTUR_Partner_LocationsCustomers', 'AMTUR_Partner_LocationsVendors',
                       'GEAT_BOGOExistencias', 'GEAT_CARTExistencias', 'GEAT_GALBExistencias', 'GEAT_GFONExistencias',
                       'GEAT_GRIOExistencias', 'GEAT_MONTExistencias', 'GEAT_Partner_LocationsCustomers',
                       'GEAT_Partner_LocationsVendors', 'UT_BOGOExistencias', 'UT_CARTExistencias', 'UT_GALBExistencias',
                       'UT_GFONExistencias', 'UT_GRIOExistencias', 'UT_MONTExistencias', 'UT_Partner_LocationsCustomers',
                        'UT_Partner_LocationsVendors']
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