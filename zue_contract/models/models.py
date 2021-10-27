from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from datetime import datetime,timedelta

class cntr_contract_encab(models.Model):
    _name = 'cntr.contract.encab'
    _description = 'Encabezado de la tabla de contratos'

    name = fields.Char('Nombre')
    customer_id = fields.Many2one('res.partner', 'Cliente', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta analítica', required=True)
    branch_id = fields.Many2one('zue.res.branch', 'Sucursal', required=True)
    start_date = fields.Date('Fecha de inicio', required=True)
    end_date = fields.Date('Fecha de finalización', required=True)
    description = fields.Text('Objeto del contrato')
    contract_interface_id = fields.Many2one('cntr.contract.logirastreo',string='Contrato asociado Logirastreo')
    last_execution_date = fields.Date('Última consulta servicios', compute='get_last_execution_date', store=True)
    contract_participation_id = fields.One2many('cntr.contract.participation', 'contract_encab_id', 'Participación del contrato', ondelete='cascade')
    contract_service_id = fields.One2many('cntr.contract.service', 'contract_encab_id', 'Servicios del contrato', ondelete='cascade')
    contract_service_detail_id = fields.One2many('cntr.contract.service.detail', 'contract_encab_id', string='Detalle servicios del contrato', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cntr.contract.encab.seq') or '/'
            
        obj_contract = super(cntr_contract_encab, self).create(vals)
            
        return obj_contract
    
    @api.depends('contract_service_detail_id')
    def get_last_execution_date(self):
        last_execution_date = self.env['cntr.contract.service.detail'].search([('contract_encab_id','=',self.id)],order='date desc', limit=1).date

        if not last_execution_date:
            date = datetime.today().date()
            first_day_of_month = date.replace(day=1)

            self.last_execution_date = first_day_of_month
        else:
            self.last_execution_date = last_execution_date 

    def get_contracts_logirastreo(self):
        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'get_contracts_logirastreo')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'get_contracts_logirastreo'"))

        obj_services = obj_ws.connection_requests()

        contracts_to_create = []
        if 'contratos' in obj_services:            
            for rows in obj_services['contratos']:
                for contract in rows:
                    if contract['id_contrato']:
                        obj_contract = self.env['cntr.contract.logirastreo'].search([('id_logirastreo', '=', contract['id_contrato'])])
                        if not obj_contract:
                            contract_vals = {
                                'id_logirastreo': contract['id_contrato'],
                                'code': contract['documentoContratante'],
                                'name': contract['nombreContratante'],
                            }
                            contracts_to_create.append(contract_vals)
            
            if contracts_to_create:
                self.env['cntr.contract.logirastreo'].create(contracts_to_create)

            return True


    def get_contract_services(self):
        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'get_contract_services')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'get_contract_services'"))

        if not self.contract_interface_id:
            raise ValidationError(_("Error! No ha especificado el ID del contrato de logirastreo a consultar.")) 

        start_date = self.last_execution_date
        end_date = datetime.today().date() + timedelta(days=1)

        if start_date + timedelta(days=1) == end_date:
            raise ValidationError(_("Error! El proceso ya ha sido ejecutado para esta fecha.")) 

        obj_contract_services = obj_ws.connection_requests(start_date,end_date,self.contract_interface_id.id_logirastreo)
        
        services_to_create = []
        if 'servicios' in obj_contract_services:
            name = self.name + ' del ' + str(start_date) + ' al ' + str(end_date)
            
            for rows in obj_contract_services['servicios']:
                for services in rows:
                    if services['inicioProgramado']:
                        date_r = datetime.strptime(services['inicioProgramado'], '%Y-%m-%d %H:%M:%S')
                    else:
                        date_r = None
                    
                    if services['inicioReal']:
                        start_d = datetime.strptime(services['inicioReal'], '%Y-%m-%d %H:%M:%S')
                    else:
                        start_d = None

                    if services['fin']:
                        end_d = datetime.strptime(services['fin'], '%Y-%m-%d %H:%M:%S')
                    else:
                        end_d = None

                    service_vals = {
                        'name': name,
                        'contract_encab_id': self.id,
                        'date': date_r,
                        'contract_id': services['idContrato'],
                        'service_id': '',
                        'vehicle_id': services['vehiculo'],
                        'driver_id': services['cedulaConductor'],
                        'customer_id': services['nombreContratante'],
                        'route': services['ruta'],
                        'turn': '',
                        'start_date': start_d,
                        'end_date': end_d,
                        'programmed_distance': services['kilometrosProgramados'],
                        'real_distance': services['kilometrosRecorridos'],
                        'passengers': 0,
                        'branch_id': services['sucursal'],
                        'trip_id': services['idViaje'],
                    }
                    services_to_create.append(service_vals)

            self.env['cntr.contract.service.detail'].create(services_to_create)
        else:
           raise ValidationError(_("No se encontraron datos a la fecha actual.")) 

class cntr_contract_participation(models.Model):
    _name = 'cntr.contract.participation'
    _description = 'Detalle de la tabla de contratos'

    contract_encab_id = fields.Many2one('cntr.contract.encab', 'Encabezado del contrato')
    partner_id = fields.Many2one('res.partner', 'Socio', required=True)
    participation_percent = fields.Float('% Participación', required=True)

class cntr_contract_service(models.Model):
    _name = 'cntr.contract.service'
    _description = 'Servicios de los contratos'

    contract_encab_id = fields.Many2one('cntr.contract.encab', 'Encabezado del contrato')
    service_type_id = fields.Many2one('mntc.services.type', 'Servicio', required=True)
    billing_uom_id = fields.Many2one('cntr.contract.billing.uom', 'Unidad de facturación', required=True)
    unit_rate = fields.Float('Tarifa unitaria', required=True)
    periodicity_id = fields.Many2one('cntr.contract.periodicity', 'Periodicidad', required=True)
    product_id = fields.Many2one('product.template','Referencia', required=True, domain=[('type', '=', 'service')])

class cntr_contract_billing_uom(models.Model):
    _name = 'cntr.contract.billing.uom'
    _description = 'Unidad de medida de facturación de los contratos'

    name = fields.Char(string='Nombre', required=True)
    range_id = fields.One2many('cntr.contract.ranges.uom', 'billing_uom_id', 'Rango')

class cntr_contract_ranges_uom(models.Model):
    _name = 'cntr.contract.ranges.uom'
    _description = 'Rangos para las unidades de medida'

    billing_uom_id = fields.Many2one('cntr.contract.billing.uom', 'Unidad Medida Facturación')
    min_value = fields.Integer('Mínimo', required=True)
    max_value = fields.Integer('Máximo', required=True)

class cntr_contract_periodicity(models.Model):
    _name = 'cntr.contract.periodicity'
    _description = 'Periodicidad de los contratos'

    name = fields.Char(string='Nombre', required=True)

class cntr_contract_service_detail(models.Model):
    _name = 'cntr.contract.service.detail'
    _description = 'Servicios por contrato'

    name = fields.Char(string='Nombre', required=True)
    contract_encab_id = fields.Many2one('cntr.contract.encab', 'Encabezado del contrato')
    date = fields.Date('Inicio Programado')
    contract_id = fields.Char('Contrato')
    service_id = fields.Char('Servicio')
    vehicle_id = fields.Char('Vehículo')
    driver_id = fields.Char('Conductor')
    customer_id = fields.Char('Cliente')
    route = fields.Char('Ruta')
    turn = fields.Char('Turno')
    start_date = fields.Datetime('Fecha inicial')
    end_date = fields.Datetime('Fecha final')
    programmed_distance = fields.Integer('Distancia programada')
    real_distance = fields.Integer('Distancia recorrida')
    passengers = fields.Integer('Pasajeros')
    branch_id = fields.Char('Sucursal')
    trip_id = fields.Integer('Id de viaje') 

class cntr_contract_logirastreo(models.Model):
    _name = 'cntr.contract.logirastreo'
    _description = 'Contratos de logirastreo'

    id_logirastreo = fields.Integer(string='Id logirastreo', required=True)
    code = fields.Char(string='Documento contratante', required=True)
    name = fields.Char(string='Nombre contratante', required=True)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} | {}".format(record.code, record.name)))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        contract_interface_id = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(contract_interface_id).name_get()


        