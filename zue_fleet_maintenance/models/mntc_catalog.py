from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class mntc_catalog(models.Model):
    _name = 'mntc.catalog'
    _description = 'Catálogo'

    name = fields.Char(compute="_get_complete_name", string='Name', store=True)
    service_type_id = fields.Many2one('mntc.services.type', string='Service', required=True)
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Marca')
    vehiculo_linea_id = fields.Many2one('vehiculos.lineas', string='    *- ',domain="[('marca','=',brand_id)]")
    routines_ids = fields.Many2many('mntc.routines','mntc_catalog_x_mntc_routines', 'catalog_id', 'routine_id', string='Routines')
    spare_x_catalog_ids = fields.One2many('mntc.spare.x.catalog', 'catalog_id', string='Repuesto x Catalogo')

    @api.depends('service_type_id', 'brand_id', 'vehiculo_linea_id')
    def _get_complete_name(self):
        if self.service_type_id:
            service = self.service_type_id.name.upper()
            names = [service]
            brand = self.brand_id
            vehiculo_linea = self.vehiculo_linea_id
            while brand:
                names.append(brand.name.upper())
                brand = False

            while vehiculo_linea:
                names.append(vehiculo_linea.name.upper())
                vehiculo_linea = False
            self.name = " / ".join(names)
        else:
            self.name = ""

    _sql_constraints = [
        ('name', 'UNIQUE (name)', 'You can not have two catalogs with the same name !')
    ]
    
    @api.model
    def create(self, vals):
        obj_catalogo = super(mntc_catalog, self).create(vals)

        vehicle_object = self.env['fleet.vehicle'].search([('vehiculo_marca.id', '=', obj_catalogo.brand_id.id), ('service_type_id.id', '=', obj_catalogo.service_type_id.id), ('vehiculo_linea.id', '=', obj_catalogo.vehiculo_linea_id.id)])

        for vehicle in vehicle_object:
            vehicle.write({'catalog_id' : obj_catalogo})

        return obj_catalogo

class fleet_vehicle_model_brand(models.Model):
    _inherit = 'fleet.vehicle.model.brand'

    code_reference = fields.Char(string='Code reference', size=2)


class vehiculos_lineas(models.Model):
    _name = 'vehiculos.lineas'
    _description = 'Lineas de vehiculos'
    
    name = fields.Char("Nombre de linea", size=50, required=True)
    marca = fields.Many2one('fleet.vehicle.model.brand','Marca del vehiculo', required=True)
    code_reference = fields.Char(string='Code reference', size=2)


class mntc_spare_x_catalog(models.Model):
    _name = 'mntc.spare.x.catalog'
    _description = 'Partes por catálogo'

    def _get_spare_type_ids(self):
        routines_ids = self._context.get('routines_ids') or False
        routin_ids = []
        domain = []
        if routines_ids:
            for rout_id in routines_ids[0][2]:
                routin_ids.append(rout_id)
        routines_obj = self.env['mntc.routines'].browse(routin_ids)
        spare_type_ids = []
        if routines_obj:
            for spare_type in routines_obj:
                for activities in spare_type.activity_ids:
                    for type in activities.spare_part_type_ids:
                        if type.id not in spare_type_ids:
                            spare_type_ids.append(type.id)
        if spare_type_ids:
            domain = "[('id','in'," + str(spare_type_ids) + ")]"
        else:
            domain = "[('id','<',0)]"

        return domain

    catalog_id = fields.Many2one('mntc.catalog', string='Catalog')
    product_product_id = fields.Many2one('product.product', string='Product')
    spare_type_id = fields.Many2one('mntc.spare.part.type', string='Spare type', domain=lambda self:self._get_spare_type_ids())
    expected_qty = fields.Float(string='Expected quantity')
    uom = fields.Many2one('product.uom', string='Unit of Measure',domain="[('category_id', '=', uom_related)]")
    uom_related = fields.Many2one('product.uom.categ',string='related')

    @api.onchange('product_product_id')
    def on_change_product(self):
        if self.product_product_id:
            self.uom = self.product_product_id.uom_id
            self.uom_related = self.product_product_id.uom_id.category_id


class mntc_spare_part_type(models.Model):
    _name = 'mntc.spare.part.type'
    _description = 'Parte que falla'

    name = fields.Char(string='Name', required=True, size=50)
    component_ids = fields.Many2many('mntc.component', string='Component id', required=True)


      
       


