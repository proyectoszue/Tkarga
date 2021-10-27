from odoo import models, fields, api, _ 
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class mntc_spare_part_x_task(models.Model):
    _name = 'mntc.spare.part.x.task'
    _rec_name = 'product_product_id'
    _description = 'Parte que fálla por tarea'

    spare_part_type_id = fields.Many2one('mntc.spare.part.type', string='Parte que falla', domain=lambda self:self._get_spare_type())
    qty_used = fields.Float(string='Quantity used', required=True)
    expected_qty = fields.Float(string='Expected quantity')
    uom = fields.Many2one('product.uom', string='Unit of Measure',domain="[('category_id', '=', uom_related)]")
    uom_related = fields.Many2one('product.uom.categ',string='related')
    spare_parts_cost = fields.Float(string='Spare Cost')
    unit_price = fields.Float(string='Unit price')
    task_id = fields.Many2one('mntc.tasks', string='Task')
    stock_picking_mc_id = fields.Many2one('stock.picking.multicompany', string='Stock picking id')
    purchase_requisition_mc_id = fields.Many2one('purchase.requisition.multicompany', string='Purchase requisition id')
    spare_part_line = fields.Boolean(string='Spare part line')
    product_product_id = fields.Many2one('product.product', string='Product product id', required=True)
    product_internal_reference = fields.Char('Product Internal Reference')
    spare_x_catalog_id = fields.Many2one('mntc.spare.x.catalog', string='Spare x catalog id')
    product_qty_available = fields.Float(string='Qty available')
    product_virtual_available = fields.Float(string='Virtual available')
    multicompany_quantity = fields.Boolean(string='Multicompany quantity')
    qty_returned = fields.Float(string='Quantity returned')
    stock_returned_mc_id = fields.Many2one('stock.picking.multicompany', string='Stock returned id')


    def _get_spare_type(self):
        domain = []

        context = self._context.copy()

        vehicle_id = self._context.get('vehicle_id') or False
        vehicle_obj = self.env['fleet.vehicle'].browse(vehicle_id)
        catalog_id = vehicle_obj.catalog_id.id
        catalog_obj = self.env['mntc.catalog'].browse(catalog_id)
        spare_parts = []
        if catalog_obj.routines_ids:
            for spare in catalog_obj.spare_x_catalog_ids:

                spare_parts.append(spare.spare_type_id.id)
            domain = "[('id','in'," + str(spare_parts) + ")]"
        else:
            domain = "[('id','<',0)]"
        return domain

    def _get_catalog_id(self):

        context = self._context.copy()

        vehicle_id = self._context.get('vehicle_id') or False
        vehicle_obj = self.env['fleet.vehicle'].browse(vehicle_id)
        catalog_id = vehicle_obj.catalog_id.id
        return catalog_id

    
    @api.onchange('multicompany_quantity')
    def on_change_multicompany(self):
        total_qty = 0
        total_qty_vir = 0
        total_qty_ali = 0
        total_qty_ali_vir = 0
        total_qty_ut = 0
        total_qty_ut_vir = 0
        total_qty_amtur = 0
        total_qty_amtur_vir = 0
        companies = ['ALIANZA', 'UT','AMTUR']
        base_alianza = self.env['ir.config_parameter'].get_param('database.alianza',default='AlianzaT')
        base_ut = self.env['ir.config_parameter'].get_param('database.ut',default='Union_Temporal')
        task_id = self._context.get('task_id') or False
        task_obj = self.env['mntc.tasks'].browse(task_id)

        for company in companies:
            if company == 'ALIANZA':
                registry = RegistryManager.get(base_alianza)
                cr = registry.cursor()
                env = api.Environment(cr, self.env.uid, {})
                if self.product_product_id:
                    product_ali = False
                    if self.product_product_id.default_code:        
                        product_ali = env['product.product'].search([('default_code','=',self.product_product_id.default_code)])                     

                    if not product_ali:
                        product_ali = env['product.product'].search([('name','=',self.product_product_id.name)]) 

                    if len(product_ali) > 1:
                        raise ValidationError(_('Error in internal reference or name'+": "+"There is more than one product with this internal reference or with this name in database Alianza T"))

                    res_branch_ali = env['zue.res.branch'].search([('name','=', task_obj.workorder_id.garage_id.branch_id.name)])
                    stock_warehouse_search_ali = env['stock.warehouse'].search([('branch_id','=', res_branch_ali.id)])
                    location_parent_ali = stock_warehouse_search_ali.lot_stock_id
                    location_ali = env['stock.location'].search([('location_id','=',location_parent_ali.location_id.id),('name','=',task_obj.workorder_id.garage_id.stock_location_id.name)])
                    stock_quant_search_ali = env['stock.quant'].search([('product_id','=',product_ali.id),('location_id','=', location_ali.id)]) 
                    total_qty_ali = 0
                    for quant in stock_quant_search_ali:
                        total_qty_ali += quant.qty
                    
                    total_qty_ali_vir += product_ali.virtual_available

                    cr.close()
            elif company == 'UT':
                registry = RegistryManager.get(base_ut)
                cr = registry.cursor()
                env = api.Environment(cr, self.env.uid, {})

                if self.product_product_id:
                    if self.product_product_id.default_code:               
                        product_ut = env['product.product'].search([('default_code','=',self.product_product_id.default_code)]) 
                    else:
                        product_ut = env['product.product'].search([('name','=',self.product_product_id.name)]) 

                    if len(product_ut) > 1:
                        raise ValidationError(_('Error in internal reference or name'+": "+"There is more than one product with this internal reference or with this name in database UT"))
                    res_branch_ut = env['zue.res.branch'].search([('name','=', task_obj.workorder_id.garage_id.branch_id.name)])
                    stock_warehouse_search_ut = env['stock.warehouse'].search([('branch_id','=', res_branch_ut.id)])
                    location_parent_ut = stock_warehouse_search_ut.lot_stock_id
                    location_ut = env['stock.location'].search([('location_id','=',location_parent_ut.location_id.id),('name','=',task_obj.workorder_id.garage_id.stock_location_id.name)])
                    stock_quant_search_ut = env['stock.quant'].search([('product_id','=',product_ut.id),('location_id','=', location_ut.id)])  
                    total_qty_ut = 0
                    for quant in stock_quant_search_ut:
                        total_qty_ut += quant.qty
                    
                    total_qty_ut_vir += product_ut.virtual_available
                    
                    cr.close()
            elif company == 'AMTUR':

                if self.product_product_id:
                    location = task_obj.workorder_id.garage_id.stock_location_id
                    stock_quant_pool = self.env['stock.quant']
                    stock_quant_search = stock_quant_pool.search([('product_id','=',self.product_product_id.id),('location_id','=', location.id)])  
                    total_qty_amtur = 0
                    for quant in stock_quant_search:
                        total_qty_amtur += quant.qty    
                    
                    total_qty_amtur_vir += self.product_product_id.virtual_available

        if self.multicompany_quantity:
            total_qty = total_qty_ali + total_qty_ut + total_qty_amtur        
            total_qty_vir = total_qty_ali_vir + total_qty_ut_vir + total_qty_amtur_vir  
            self.product_qty_available = total_qty
            self.product_virtual_available = total_qty_vir
        else:
            if task_obj.workorder_id.vehicle_id.in_the_charge_of.name == 'GRUPO EMPRESARIAL ALIANZA T SAS':
                self.product_qty_available = total_qty_ali
                self.product_virtual_available = total_qty_ali_vir
            elif task_obj.workorder_id.vehicle_id.in_the_charge_of.name == 'UT - GEAT - AMTUR - COOMOEPAL 2014':
                self.product_qty_available = total_qty_ut
                self.product_virtual_available = total_qty_ut_vir
            elif task_obj.workorder_id.vehicle_id.in_the_charge_of.name == 'AMTUR S.A.S':
                self.product_qty_available = total_qty_amtur
                self.product_virtual_available = total_qty_amtur_vir
    
    @api.onchange('qty_used')
    def on_change_qty_used(self):        
        self.spare_parts_cost = self.unit_price * (self.qty_used - self.qty_returned)
    
    @api.onchange('qty_returned')
    def on_change_qty_returned(self):        
        self.spare_parts_cost = self.unit_price * (self.qty_used - self.qty_returned)
         
    @api.onchange('product_product_id')
    def on_change_product(self):
        base_alianza = self.env['ir.config_parameter'].get_param('database.alianza',default='AlianzaT')
        base_ut = self.env['ir.config_parameter'].get_param('database.ut',default='Union_Temporal')
        task_id = self._context.get('task_id') or False
        task_obj = self.env['mntc.tasks'].browse(task_id)
        
        if self.product_product_id:
            self.uom = self.product_product_id.uom_id
            self.uom_related = self.product_product_id.uom_id.category_id

        catalog_obj = task_obj.workorder_id.vehicle_id.catalog_id
        for product in catalog_obj.spare_x_catalog_ids:
            if product.product_product_id == self.product_product_id:
                self.expected_qty = product.expected_qty
                break
            else:
                self.expected_qty = 0

        self.unit_price = self.product_product_id.standard_price or 0.0    

        if task_obj.workorder_id.garage_id.branch_id:
            total_qty = 0
            total_qty_vir = 0
            total_qty_ali = 0
            total_qty_ali_vir = 0
            total_qty_ut = 0
            total_qty_ut_vir = 0
            total_qty_amtur = 0
            total_qty_amtur_vir = 0
            companies = ['ALIANZA', 'UT','AMTUR']
            
            for company in companies:
                if company == 'ALIANZA':
                    registry = RegistryManager.get(base_alianza)
                    cr = registry.cursor()
                    env = api.Environment(cr, self.env.uid, {})

                    if self.product_product_id:
                        if self.product_product_id.default_code:               
                            product_ali = env['product.product'].search([('default_code','=',self.product_product_id.default_code)]) 
                        else:
                            product_ali = env['product.product'].search([('name','=',self.product_product_id.name)]) 

                        if len(product_ali) > 1:
                            raise ValidationError(_('Error in internal reference or name'+": "+"There is more than one product with this internal reference or with this name in database Alianza T"))
                                        
                        res_branch_ali = env['zue.res.branch'].search([('name','=', task_obj.workorder_id.garage_id.branch_id.name)])
                        stock_warehouse_search_ali = env['stock.warehouse'].search([('branch_id','=', res_branch_ali.id)])
                        location_parent_ali = stock_warehouse_search_ali.lot_stock_id
                        location_ali = env['stock.location'].search([('location_id','=',location_parent_ali.location_id.id),('name','=',task_obj.workorder_id.garage_id.stock_location_id.name)])
                        stock_quant_search_ali = env['stock.quant'].search([('product_id','=',product_ali.id),('location_id','=', location_ali.id)]) 
                        total_qty_ali = 0
                        for quant in stock_quant_search_ali:
                            total_qty_ali += quant.qty
                        
                        total_qty_ali_vir += product_ali.virtual_available

                        cr.close()
                elif company == 'UT':
                    registry = RegistryManager.get(base_ut)
                    cr = registry.cursor()
                    env = api.Environment(cr, self.env.uid, {})

                    
                    if self.product_product_id:
                        if self.product_product_id.default_code:               
                            product_ut = env['product.product'].search([('default_code','=',self.product_product_id.default_code)]) 
                        else:
                            product_ut = env['product.product'].search([('name','=',self.product_product_id.name)]) 

                        if len(product_ut) > 1:
                            raise ValidationError(_('Error in internal reference or name'+": "+"There is more than one product with this internal reference or with this name in database Union Temporal"))                 
                        res_branch_ut = env['zue.res.branch'].search([('name','=', task_obj.workorder_id.garage_id.branch_id.name)])
                        stock_warehouse_search_ut = env['stock.warehouse'].search([('branch_id','=', res_branch_ut.id)])
                        location_parent_ut = stock_warehouse_search_ut.lot_stock_id
                        location_ut = env['stock.location'].search([('location_id','=',location_parent_ut.location_id.id),('name','=',task_obj.workorder_id.garage_id.stock_location_id.name)])
                        stock_quant_search_ut = env['stock.quant'].search([('product_id','=',product_ut.id),('location_id','=', location_ut.id)]) 
                        total_qty_ut = 0
                        for quant in stock_quant_search_ut:
                            total_qty_ut += quant.qty
                        
                        total_qty_ut_vir += product_ut.virtual_available
                        
                        cr.close()
                elif company == 'AMTUR':
                    if self.product_product_id:
                        location = task_obj.workorder_id.garage_id.stock_location_id
                        stock_quant_pool = self.env['stock.quant']              
                        stock_quant_search = stock_quant_pool.search([('product_id','=',self.product_product_id.id),('location_id','=', location.id)]) 
                        total_qty_amtur = 0
                        for quant in stock_quant_search:
                            total_qty_amtur += quant.qty    
                        
                        
                        total_qty_amtur_vir += self.product_product_id.virtual_available

            if self.multicompany_quantity:
                total_qty = total_qty_ali + total_qty_ut + total_qty_amtur        
                total_qty_vir = total_qty_ali_vir + total_qty_ut_vir + total_qty_amtur_vir  
                self.product_qty_available = total_qty
                self.product_virtual_available = total_qty_vir
            else:
                if task_obj.workorder_id.vehicle_id.in_the_charge_of.name == 'GRUPO EMPRESARIAL ALIANZA T SAS':
                    self.product_qty_available = total_qty_ali
                    self.product_virtual_available = total_qty_ali_vir
                elif task_obj.workorder_id.vehicle_id.in_the_charge_of.name == 'UT - GEAT - AMTUR - COOMOEPAL 2014':
                    self.product_qty_available = total_qty_ut
                    self.product_virtual_available = total_qty_ut_vir
                elif task_obj.workorder_id.vehicle_id.in_the_charge_of.name == 'AMTUR S.A.S':
                    self.product_qty_available = total_qty_amtur
                    self.product_virtual_available = total_qty_amtur_vir

    @api.onchange('spare_part_line','spare_part_type_id')
    def onchange_domain_product_template(self):
        task_id = self._context.get('task_id') or False
        task_obj = self.env['mntc.tasks'].browse(task_id)
        res = {}
        if self.spare_part_line:
            catalog_id = task_obj.workorder_id.vehicle_id.catalog_id
            product_objs = [type_part for type_part in catalog_id.spare_x_catalog_ids]
            product_ids = []
            for product in product_objs:
                if product.spare_type_id == self.spare_part_type_id:
                    product_ids.append(product.product_product_id.id)
            res['domain'] = {'product_product_id':[('id','in',product_ids)]}
            return res
        else:
            res['domain'] = {'product_product_id': []}
            return res

    @api.onchange('product_internal_reference')
    def product_internal_reference_onchange(self):
        if self.product_internal_reference:
            product_id = self.env['product.product'].search([('default_code', '=', self.product_internal_reference)])
            if product_id:
                if self.product_product_id:
                    if product_id.id != self.product_product_id.id:
                        self.product_product_id = product_id.id
                else:
                    self.product_product_id = product_id
            else:
                self.product_product_id = False
                raise ValidationError(_('Error in internal reference'+": "+"Doesn't exist a product with the specificated internal reference."))

    @api.onchange('product_product_id')
    def product_product_onchange(self):
        if self.product_product_id:
            if self.product_internal_reference != self.product_product_id.default_code:
                self.product_internal_reference = self.product_product_id.default_code
        else:
            self.product_internal_reference = False

    @api.model
    def create(self, vals):
        context = self.env.context
        if 'active_model' in context.keys() and context['active_model'] == 'mntc.tasks' and 'active_id' in context.keys():
            vals['task_id'] = context['active_id']
        elif 'task_id' not in vals.keys() :
            raise ValidationError(_("Error in creation"+": "+"The record hasn't a task assigned"))

        task_id = self._context.get('task_id') or False
        task_obj = self.env['mntc.tasks'].browse(task_id)
        
        if task_obj:
            if task_obj.workorder_id.state in ['ended','canceled']:
                raise ValidationError(_("Error in creation"+": "+"The Work order is Finished or Canceled, you can't create!"))

        return super(mntc_spare_part_x_task, self).create(vals)
    
    def remove_spare(self):
        for remove_spare in self:
            if not remove_spare.stock_picking_mc_id and not remove_spare.purchase_requisition_mc_id:
                remove_spare.unlink()
            else :
                raise ValidationError(_("Error"+": "+"It cannot be deleted because it has a delivery note or purchase request"))
        return True

    def write(self, vals):
        task_id = self._context.get('task_id') or False
        task_obj = self.env['mntc.tasks'].browse(task_id)
        
        if task_obj:
            if task_obj.workorder_id.state in ['ended','canceled']:
                raise ValidationError(_("Writing error"+": "+"The Work order is Finished or Canceled, you can't modify anything!"))
        
        return super(mntc_spare_part_x_task, self).write(vals)
    
    def intelligent_search_internal_reference(self):
        context = self.env.context.copy()
        context['task_id'] = self.id
        if not self.product_internal_reference:
            raise ValidationError(_("Error Intelligent Search"+": "+"You can't execute Intelligent Search without Internal Reference"))
        regular_expr = ""
        internal_reference = [x for x in self.product_internal_reference]
        counter = 0
        for character in internal_reference:
            if character == '_':
                if counter == 0:
                    regular_expr += "^"
                regular_expr += "."
                if counter == len(internal_reference)-1:
                    regular_expr += "$"
            elif character == '%':
                if counter != 0 and counter != len(internal_reference)-1:
                    raise ValidationError(_("Error Character"+": "+"The character '*' only must be used at start or end of the internal reference."))
                else:
                    regular_expr += "."
            else:
                if counter == 0:
                    regular_expr += "^"
                regular_expr += character
                if counter == len(internal_reference)-1:
                    regular_expr += "$"
            counter += 1
        if regular_expr:
            query ="SELECT id FROM product_product WHERE default_code ~ '" + regular_expr + "';"
            self.env.cr.execute(query)
            ids_fetch = self.env.cr.fetchall()
            product_templates_ids = [x[0] for x in ids_fetch]
            view_id = self.env.ref('big_fleet_maintenance.spare_part_product_template_tree_view').id
            return {
                'name': _('Product Templates For Spare Parts'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'product.product',
                'domain': "[('id','in', %s)]" % product_templates_ids,
                'view_id': view_id,
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

class product_uom_categ(models.Model):
    _name = 'product.uom.categ'
    _description = 'Product uom categ'
    
    name = fields.Char('Name', required=True)

class product_uom(models.Model):
    _name = 'product.uom'
    _description = 'Product Unit of Measure'

    name = fields.Char('Unit of Measure', required=True, translate=True)
    category_id = fields.Many2one('product.uom.categ', 'Product Category', required=True, ondelete='cascade')
    factor = fields.Float('Ratio', required=True,digits=(12, 12))
    factor_inv = fields.Integer(compute='_factor_inv', string='Bigger Ratio', required=True)
    rounding = fields.Float('Rounding Precision', required=True)
    active = fields.Boolean('Active')
    uom_type = fields.Selection([('bigger','Bigger than the reference Unit of Measure'),
                                      ('reference','Reference Unit of Measure for this category'),
                                      ('smaller','Smaller than the reference Unit of Measure')],'Type', required=1)
    
    # _sql_constraints = [
    #     ('factor_gt_zero', 'CHECK (factor!=0)', 'The conversion ratio for a unit of measure cannot be 0!')
    # ]

    def _compute_factor_inv(self, factor):
        return factor and (1.0 / factor) or 0.0

    def _factor_inv(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for uom in self.browse(cursor, user, ids, context=context):
            res[uom.id] = self._compute_factor_inv(uom.factor)
        return res

    def _factor_inv_write(self, cursor, user, id, name, value, arg, context=None):
        return self.write(cursor, user, id, {'factor': self._compute_factor_inv(value)}, context=context)

    def name_create(self, cr, uid, name, context=None):
        """ The UoM category and factor are required, so we'll have to add temporary values
            for imported UoMs """
        uom_categ = self.pool.get('product.uom.categ')
        categ_misc = 'Unsorted/Imported Units'
        categ_id = uom_categ.search(cr, uid, [('name', '=', categ_misc)])
        if categ_id:
            categ_id = categ_id[0]
        else:
            categ_id, _ = uom_categ.name_create(cr, uid, categ_misc)
        uom_id = self.create(cr, uid, {self._rec_name: name,
                                       'category_id': categ_id,
                                       'factor': 1})
        return self.name_get(cr, uid, [uom_id], context=context)[0]

    # def create(self, cr, uid, data, context=None):
    #     if 'factor_inv' in data:
    #         if data['factor_inv'] != 1:
    #             data['factor'] = self._compute_factor_inv(data['factor_inv'])
    #         del(data['factor_inv'])
    #     return super(product_uom, self).create(cr, uid, data, context)

    def _compute_qty(self, cr, uid, from_uom_id, qty, to_uom_id=False, round=True):
        if not from_uom_id or not qty or not to_uom_id:
            return qty
        uoms = self.browse(cr, uid, [from_uom_id, to_uom_id])
        if uoms[0].id == from_uom_id:
            from_unit, to_unit = uoms[0], uoms[-1]
        else:
            from_unit, to_unit = uoms[-1], uoms[0]
        return self._compute_qty_obj(cr, uid, from_unit, qty, to_unit, round=round)

    def _compute_qty_obj(self, cr, uid, from_unit, qty, to_unit, round=True, context=None):
        if context is None:
            context = {}
        if from_unit.category_id.id != to_unit.category_id.id:
            if context.get('raise-exception', True):
                raise ValidationError(_('Conversion from Product UoM to Default UoM is not possible as they both belong to different Category!.'))
            else:
                return qty
        amount = float_round(qty/from_unit.factor, precision_rounding=from_unit.rounding)
        if to_unit:
            amount = amount * to_unit.factor
            if round:
                amount = ceiling(amount, to_unit.rounding)
        return amount

    def _compute_price(self, cr, uid, from_uom_id, price, to_uom_id=False):
        if not from_uom_id or not price or not to_uom_id:
            return price
        from_unit, to_unit = self.browse(cr, uid, [from_uom_id, to_uom_id])
        if from_unit.category_id.id != to_unit.category_id.id:
            return price
        amount = price * from_unit.factor
        if to_uom_id:
            amount = amount / to_unit.factor
        return amount

    def onchange_type(self, cursor, user, ids, value):
        if value == 'reference':
            return {'value': {'factor': 1, 'factor_inv': 1}}
        return {}

    # def write(self, cr, uid, ids, vals, context=None):
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     if 'category_id' in vals:
    #         for uom in self.browse(cr, uid, ids, context=context):
    #             if uom.category_id.id != vals['category_id']:
    #                 raise ValidationError(_("Cannot change the category of existing Unit of Measure."))
    #     return super(product_uom, self).write(cr, uid, ids, vals, context=context)

