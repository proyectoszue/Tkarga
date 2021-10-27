from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError 


class mntc_resumen_repuestos(models.TransientModel):
    _name = 'mntc.resumen.repuestos' 
    _description = 'Resumen de los repuestos por orden de trabajo'

    producto = fields.Many2one('product.template','Referencia', required=True, domain=[('esRepuesto', '=', True)])
    uom_id = fields.Many2one(string='Unidad de medida', store=False, readonly=True, related='producto.uom_id')
    product_uom_qty = fields.Float('Demanda')
    reserved_availability = fields.Float('Reservado')
    quantity_done = fields.Float('Terminado')
    qty_available = fields.Float('Existencia a la fecha')
    workorder_id = fields.Many2one('mntc.workorder', string='Órden de trabajo') 
    task_id = fields.Many2one('mntc.tasks', string='Tarea')

class mntc_resumen_servicios(models.TransientModel):
    _name = 'mntc.resumen.servicios'
    _description = 'Resumen de los servicios por orden de trabajo'

    producto = fields.Many2one('product.template','Referencia', required=True, domain=[('esRepuesto', '=', True)])
    name = fields.Char('Descripción')
    product_qty = fields.Float('Cantidad')
    price_unit = fields.Float('Precio unitario')
    taxes_id = fields.Many2many('account.tax', string='Impuestos')
    price_subtotal = fields.Float('Subtotal')
    res_partner_id = fields.Many2one('res.partner', string='Proveedor')
    workorder_id = fields.Many2one('mntc.workorder', string='Órden de trabajo')
    task_id = fields.Many2one('mntc.tasks', string='Tarea')


class mntc_repuestos(models.Model):
    _name = 'mntc.repuestos'
    _description = 'Referencias que son repuestos'

    producto = fields.Many2one('product.template','Referencia', required=True, domain=[('esRepuesto', '=', True)])
    cantidad = fields.Integer('Cantidad')
    actividad = fields.Many2one('mntc.activity', 'Actividad')
    uom_id = fields.Many2one(string='Unidad de medida', store=False, readonly=True, related='producto.uom_id')
    type = fields.Selection(string='Tipo de producto', related='producto.type')
    tasks_id = fields.Many2one('mntc.tasks', 'Tareas')
    standard_price = fields.Float('Costo unitario', compute='get_standard_price',store= True)
    estimated_price = fields.Float('Costo estimado', related='producto.standard_price')
    qty_done = fields.Float('Cantidad recibida', compute='get_stock_picking')
    qty_available = fields.Float('Cantidad disponible', compute='get_stock_quant')
    move_line_id = fields.Many2one('stock.move', 'Producto con solicitud de cotización', default=None)
    # stock_picking_id = fields.Many2one('stock.picking', 'Solicitud de cotización', default=None)

    @api.onchange('producto')
    def producto_onchange(self):
        self.get_stock_quant()
 
    @api.depends('tasks_id')
    def get_standard_price(self):
        for record in self:
            if record.move_line_id.id and record.producto.product_variant_id.id and record.tasks_id.workorder_id.assigned_company_id.id:
                query = '''
                select a.value 
                from stock_valuation_layer a
                where a.company_id = %s and a.product_id = %s and a.stock_move_id = %s 
                limit 1
                ''' % (record.tasks_id.workorder_id.assigned_company_id.id, record.producto.product_variant_id.id, record.move_line_id.id)

                self.env.cr.execute(query)

                cn_cost_value = self.env.cr.fetchone()
            
                if not cn_cost_value:
                    record.standard_price= 0
                else:
                    record.standard_price = abs(cn_cost_value[0]) / record.cantidad
            else:
                record.standard_price= 0           

    def get_stock_picking(self):
        for record in self:
            if record.move_line_id:
                stock_move_ids = self.env['stock.move'].search([('id', '=', record.move_line_id.id)])
                
                if not stock_move_ids:
                    record.qty_done = 0
                else:
                    record.qty_done = stock_move_ids.quantity_done 
            else:
                record.qty_done = 0

    def get_stock_quant(self):
        for record in self:  
            stock_destino = 0
            qty_available = 0
            name = record.tasks_id.workorder_id.garage_id.stock_location_id.complete_name
            assigned_company = record.tasks_id.workorder_id.assigned_company_id.id

            if assigned_company and name:
                query = '''
                    select a.id
                    from stock_location a
                    where a.complete_name = '%s' and a.company_id = %s 
                    limit 1
                ''' % (name,assigned_company)

                self.env.cr.execute(query)

                obj_stock = self.env.cr.fetchone()
                if obj_stock:
                    stock_destino = obj_stock[0]

                if stock_destino and record.producto.product_variant_id.id:
                    query = '''
                        select a.quantity
                        from stock_quant a
                        where a.product_id = '%s' and a.company_id = %s and a.location_id = %s 
                        limit 1
                    ''' % (record.producto.product_variant_id.id,assigned_company,stock_destino)

                    self.env.cr.execute(query)

                    stock_picking_ids = self.env.cr.fetchone()
                    if stock_picking_ids:
                        qty_available = stock_picking_ids[0]
                        
                    if not qty_available:
                        record.qty_available = 0
                    else:
                        record.qty_available = qty_available
                else:
                    record.qty_available = 0
            else:
                record.qty_available = 0

    

class mntc_servicios(models.Model):
    _name = 'mntc.servicios'
    _description = 'Referencias que son servicios'

    producto = fields.Many2one('product.template','Referencia', required=True, domain=[('type', '=', 'service'),('categ_id', '=', 23)])
    cantidad = fields.Integer('Cantidad')
    actividad = fields.Many2one('mntc.activity', 'Actividad')
    uom_id = fields.Many2one(string='Unidad de medida', store=True, readonly=True, related='producto.uom_id')
    type = fields.Selection(string='Tipo de producto', related='producto.type')
    tasks_id = fields.Many2one('mntc.tasks', 'Tareas')
    # company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.user.company_id)
    res_partner_id = fields.Many2one('res.partner', string='Proveedor', domain="[('x_type_thirdparty.id','=',3)]")
    description = fields.Text('Descripción')
    price_unit = fields.Float('Precio unitario')
    taxes_id = fields.Many2many('account.tax', domain="[('type_tax_use', '=', 'purchase')]", string="Impuestos", store=True)#many2manytag,('company_id', '=', parent.company_id)
    order_line_id = fields.Many2one('purchase.order.line', 'Servicio con órden de compra', default=None)

    quantity_order = fields.Float(related='order_line_id.product_qty')
    price_unit_order = fields.Float(related='order_line_id.price_unit')
    taxes_id_order = fields.Many2many(related='order_line_id.taxes_id')

    @api.model
    def _getCompanyId(self):
        return [('company_id', '=', self.env.user.company_id)]

class mntc_product_family(models.Model):
    _name = 'mntc.product.family'
    _description = 'Familia de productos'

    code = fields.Char(string='Código', size=2, required=True)
    name = fields.Char(string='Nombre', required=True)

class stock_valuation_layer(models.Model):
    _inherit = "stock.valuation.layer"

    family_id = fields.Many2one(related='product_id.product_tmpl_id.family_id', store=True)
    brand_id = fields.Many2one(related='product_id.product_tmpl_id.brand_id', store=True)
    vehiculo_linea_id = fields.Many2one(related='product_id.product_tmpl_id.vehiculo_linea_id', store=True)
    codigo_fabrica = fields.Char(related='product_id.product_tmpl_id.codigo_fabrica', store=True)
    rotation_type = fields.Selection(related='product_id.product_tmpl_id.rotation_type', store=True)

class ProductProduct(models.Model):
    _inherit = "product.product"

    family_id = fields.Many2one(related='product_tmpl_id.family_id', store=True)
    brand_id = fields.Many2one(related='product_tmpl_id.brand_id', store=True)
    vehiculo_linea_id = fields.Many2one(related='product_tmpl_id.vehiculo_linea_id', store=True)
    codigo_fabrica = fields.Char(related='product_tmpl_id.codigo_fabrica', store=True)
    rotation_type = fields.Selection(related='product_tmpl_id.rotation_type', store=True)

class product_template(models.Model):
    _inherit = 'product.template'

    esRepuesto = fields.Boolean('Es repuesto', track_visibility='onchange')
    default_code = fields.Char('Internal Reference', track_visibility='onchange')
    family_id = fields.Many2one('mntc.product.family','Familia', track_visibility='onchange')
    system_id = fields.Many2one('mntc.vehicle.system','Sistema', track_visibility='onchange')
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Marca del vehículo', track_visibility='onchange')
    vehiculo_linea_id = fields.Many2one('vehiculos.lineas', string='Vehículo linea',domain="[('marca','=',brand_id)]", track_visibility='onchange')
    codigo_fabrica = fields.Char('Código de fábrica', track_visibility='onchange')
    rotation_type = fields.Selection([('a','A'),('b','B'),('c','C'),('n','No Aplica')], default='n', string='Tipo de Reabastecimiento')
    sequence_number = fields.Integer('sequence')
    help_categ = fields.Boolean("help categ")
    @api.model
    def create(self, vals):
        obj_product = super(product_template, self).create(vals)
        obj_product.create_default_code(sequence=True)
        return obj_product

    def write(self, vals):
        update_code = False

        if 'esRepuesto' in vals.keys():
            if vals["esRepuesto"]: 
                update_code = True
        
        if 'family_id' in vals.keys():
            update_code = True
        
        if 'brand_id' in vals.keys():
            update_code = True

        if 'vehiculo_linea_id' in vals.keys():
            update_code = True
        
        if 'system_id'  in vals.keys():
            update_code = True

        obj_product = super(product_template, self).write(vals)

        if update_code:
            obj_to_exec = self.env['product.template'].search([('id', '=', self.id)])
            default_code = obj_to_exec.create_default_code(sequence=False)
            self.default_code = default_code
        
        return obj_product
        
    @api.onchange('brand_id')
    def on_change_brand(self):
        if self.brand_id:
            self.system_id = False
            self.vehiculo_linea_id = False

    @api.onchange('vehiculo_linea_id')
    def on_change_linea(self):
        if self.vehiculo_linea_id:
            self.system_id = False

    def create_default_code(self,sequence=None):
        product_template = self
        default_code = ''
        if product_template.esRepuesto:
            # Familia
            if product_template.family_id.code:
                if len(product_template.family_id.code) < 2:
                    default_code += '0'+ product_template.family_id.code    
                else:
                    default_code += product_template.family_id.code
            else:
                raise UserError(_("Error!. No ha configurado una familia para el código de referencia"))
            # Marca
            if product_template.brand_id.code_reference:
                if len(product_template.brand_id.code_reference) < 2:
                    default_code += '0'+ product_template.brand_id.code_reference    
                else:
                    default_code += product_template.brand_id.code_reference
            else:
                raise UserError(_("Error!. No ha configurado un código para la marca seleccionada"))

            # Linea
            if product_template.vehiculo_linea_id.code_reference:
                if len(product_template.vehiculo_linea_id.code_reference) < 2:
                    default_code += '0'+ product_template.vehiculo_linea_id.code_reference    
                else:
                    default_code += product_template.vehiculo_linea_id.code_reference
            else:
                raise UserError(_("Error!. No ha configurado una línea de vehículo para el código de referencia"))

            # Sistema
            if product_template.system_id.initials:
                if len(product_template.system_id.initials) < 2:
                    default_code += '0'+ product_template.system_id.initials    
                else:
                    default_code += product_template.system_id.initials
            else:
                raise UserError(_("Error!.  No ha configurado un sistema para el código de referencia"))

            self.env.cr.execute('select max(sequence_number) from product_template p where "esRepuesto" = True')

            number_returned = self.env.cr.fetchone()
            if number_returned[0] == None:
                new_number = 1
            else:    
                new_number = number_returned[0] + 1

            if new_number > 9999:
                default_code += str(new_number) 
            elif new_number > 999:
                default_code += '0'+ str(new_number) 
            elif new_number > 99:
                default_code += '00'+ str(new_number) 
            elif new_number > 9:
                default_code += '000'+ str(new_number)
            else:
                default_code += '0000'+ str(new_number)         
            
            if sequence:
                product_template.write({'sequence_number':new_number,'default_code':default_code})
            else:
                return default_code
        else:
            return ''


class stok_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    store_id = fields.Many2one('zue.res.branch', 'Sucursal')

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Órdenes de entrega'

    x_mntc_origin = fields.Many2one('mntc.workorder', 'Documento Origen')
    fleet_id = fields.Many2one('fleet.vehicle','Vehículo')
    workorder_id = fields.Many2one('mntc.workorder', string='Órden de trabajo')
    branch_id = fields.Many2one(related='picking_type_id.warehouse_id.store_id')

class stock_picking_type(models.Model):
    _inherit = 'stock.picking.type'
    _description = 'Resumen de inventario'

    branch_id = fields.Many2one(related='warehouse_id.store_id')

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    workorder_id = fields.Many2one('mntc.workorder', string='Órden de trabajo')
    branch_id = fields.Many2one('zue.res.branch', 'Sucursal')

    def button_confirm(self):
        for order in self:            
            attachment = self.env['ir.attachment'].search([('res_model', '=', 'purchase.order'),('res_id','=',order.id)])    
            if not attachment:    
                raise ValidationError(_('Es obligatorio agregar un adjunto, por favor verificar.'))
        return super(purchase_order, self).button_confirm()    



    