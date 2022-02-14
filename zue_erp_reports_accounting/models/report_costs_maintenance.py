# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class costs_maintenance_report(models.Model):
    _name = "costs.maintenance.report"
    _description = "Informe Costo y Gasto de Mantenimiento"
    _auto = False
    _order = 'empresa,diario'

    empresa  = fields.Char(string='Empresa', readonly=True)
    fecha = fields.Datetime(string='Fecha', readonly=True)
    diario = fields.Char(string='Diario', readonly=True)
    asiento_contable  = fields.Char(string='Asiento Contable', readonly=True)
    grupo_de_cuenta  = fields.Char(string='Grupo de cuenta', readonly=True)
    cuenta_financiera  = fields.Char(string='Cuenta financiera', readonly=True)
    asociado  = fields.Char(string='Asociado', readonly=True)
    referencia  = fields.Char(string='Referencia', readonly=True)
    descripcion  = fields.Char(string='Descripción', readonly=True)
    cuenta_analitica  = fields.Char(string='Cuenta Analitica', readonly=True)
    debe  = fields.Float(string='Debe', readonly=True)
    haber  = fields.Float(string='Haber', readonly=True)
    vehiculo  = fields.Char(string='Vehículo', default=0.0, readonly=True)
    # vehiculo_promedio_diario = fields.Char(string='Vehículo promedio diario', readonly=True)
    vehiculo_ano_modelo  = fields.Float(string='Vehículo año modelo', readonly=True)
    vehiculo_linea  = fields.Float(string='Vehículo línea ', readonly=True)
    vehiculo_sucursal_destino  = fields.Char(string='Vehículo sucursal destino', readonly=True)
    vehiculo_servicios = fields.Char(string='Vehículo servicio', readonly=True)
    vehiculo_compania_asignada  = fields.Char(string='Vehículo compañia asignada', readonly=True)
    vehiculo_propietario = fields.Char(string='Vehículo propietario', readonly=True)
    producto = fields.Char(string='Producto', readonly=True)
    referencia_producto  = fields.Char(string='Producto Referencia', readonly=True)
    producto_familia = fields.Char(string='Producto Familia', readonly=True)
    producto_sistema  = fields.Char(string='Producto Sistema', default=0.0, readonly=True)
    producto_marca  = fields.Char(string='Producto Marca', readonly=True)
    producto_linea  = fields.Char(string='Producto Línea', readonly=True)

    @api.model
    def _query(self):
        return '''
       select row_number() over(order by c.name,b.move_name) as id,
            coalesce(c.name,'') as empresa, coalesce(b."date",'1900-01-01') as fecha, coalesce(d.name,'') as diario,
            coalesce(b.move_name,'') as asiento_contable, 
            coalesce(f.name,'-') ||' / '|| coalesce(f.code_prefix ,'-') as grupo_de_cuenta,
            coalesce(e.code,'-') ||' / '|| coalesce(e.name,'-') as cuenta_financiera,
            coalesce(g.vat || ' - ' || g.display_name ,'-') as asociado, coalesce(a."ref",'-') as referencia, 
            coalesce(b."name",'')  as descripcion,
            coalesce(i.code,'-') ||' / '|| coalesce(i.name,'-')  as cuenta_analitica, b.debit as debe, b.credit as haber,
            coalesce(concat(coalesce(modelbrand.name,''), '/' , coalesce(model.name,''),'/',coalesce(bb.placa_nro,''),'/',coalesce(bb.movil_nro,'')),'') as vehiculo, 
            coalesce(bb.modelo,'') as vehiculo_ano_modelo, coalesce(bb.vehiculo_linea,0) as vehiculo_linea,
            coalesce(k."name",'') as vehiculo_sucursal_destino, coalesce(j.name,'') as vehiculo_servicios,  coalesce(l.name,'') as vehiculo_compania_asignada,
            coalesce(m.vat || ' - ' || m.display_name ,'-') as vehiculo_propietario,
            coalesce(pt."name",'') as producto, coalesce(pt.default_code,'') as referencia_producto,
            coalesce(mpf."name",'') as producto_familia,coalesce(mvs."name",'') as producto_sistema,
            coalesce(fvmb."name",'') as producto_marca,coalesce(vl."name",'') as producto_linea
        From account_move a
            inner join account_move_line b on a.id = b.move_id
            inner join res_company c on a.company_id = c.id 
            inner join account_journal d on d.id = a.journal_id 
            left join account_account e on b.account_id = e.id  
            left join account_group f on e.group_id = f.id
            left join res_partner g on g.id = b.partner_id
            left join account_analytic_account i on b.analytic_account_id = i.id
            --Vehiculo
            left join ir_property as ip on ip."name" = 'account_analytic_id' and ip.value_reference = 'account.analytic.account,'||i.id
            left join fleet_vehicle as bb on ip.res_id = 'fleet.vehicle,'||bb.id
            left join fleet_vehicle_model as model on bb.model_id = model.id 
            left join fleet_vehicle_model_brand as modelbrand  on bb.brand_id = modelbrand.id 
            left join mntc_services_type as j on j.id = bb.service_type_id
            left join zue_res_branch as k on k.id = bb.branch_id
            left join res_company as l on l.id = bb.assigned_company_id 
            left join res_partner m on bb.owner_id = m.id
            --Inventario
            left join stock_move as sm on a.stock_move_id = sm.id 
            --left join stock_move_line as sml on sm.id = sml.move_id 
            left join product_product as pp on sm.product_id = pp.id 
            left join product_template as pt on pp.product_tmpl_id = pt.id
            left join mntc_product_family as mpf on pt.family_id = mpf.id 
            left join mntc_vehicle_system as mvs on pt.system_id = mvs.id 
            left join fleet_vehicle_model_brand as fvmb on pt.brand_id = fvmb.id 
            left join vehiculos_lineas as vl on pt.vehiculo_linea_id = vl.id
        WHERE  B.parent_state = 'posted' and e.is_account_maintenance = true  
            order by c.name,b.move_name   
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