from odoo import api,fields,models,_
import requests
from odoo.exceptions import ValidationError 

class zue_request_parameters_ws(models.Model):
    _name = 'zue.request.parameters.ws'
    _description = 'Parámetros del servicio web'

    parameter_name = fields.Char('Nombre')
    parameter_value = fields.Char('Valor')
    ws_id = fields.Many2one('zue.request.ws', 'Id Servicio web')

class zue_request_ws(models.Model):
    _name = 'zue.request.ws'
    _description = 'Configuración del servicio web'

    name = fields.Char(string='Nombre', required=True)
    username = fields.Char(string='Username')
    password = fields.Char(string='Password')
    server_url = fields.Char(string='Url')
    active = fields.Boolean(string='Activo', default=True)
    method = fields.Selection([('GET', "GET"),('POST', "POST"),('PUT', "PUT"),('DELETE', "DELETE")], "Método")
    postman_token = fields.Char(string='Postman-token')
    authorization = fields.Char(string='Authorization')
    parameters_id = fields.One2many('zue.request.parameters.ws', 'ws_id', string='Parámetros')
    body = fields.Text('Body')
    content_type = fields.Char(string='Content-Type', default='application/json')

    sql_constraints = [
        ('name', 'UNIQUE (name)', 'Ya existe un registro con este nombre!')
    ]

    def ejecutar_ws_test(self):
        obj_prueba = None
        for record in self:
            obj_prueba = record.connection_requests('enviofacturacionelectronicaamtur@alianzatsa.com','2021-10-28T16:06:42.975-05:00')

        if obj_prueba:
            raise ValidationError(_(obj_prueba))
        else:
            return True

    @api.model
    def connection_requests(self, *args):
        for obj_ws in self:
            name = ''
            value = ''
            data_body = ''
            count_parameter = 0
            
            if not obj_ws.active:
                raise ValidationError(_("El servicio web con el nombre " + obj_ws.name + " no se encuentra activo.")) 
                
            url = ''
            url_parameters, aut_user, aut_pass = '', '', ''
            final_url = ''

            if not obj_ws:
                raise ValidationError(_("No se ha configurado un servicio web con el nombre " + obj_ws.name)) 
            else:
                if obj_ws.server_url:
                    url =obj_ws.server_url
                else:
                    raise ValidationError(_("No se ha configurado una URL para el servicio web con el nombre " + obj_ws.name)) 

                if obj_ws.content_type:
                    headers = {
                        'content-type': obj_ws.content_type,
                        'cache-control': "no-cache"
                    }
                else:
                    headers = {
                        'content-type': 'application/json',
                        'cache-control': "no-cache"
                    }

                if obj_ws.username:
                    aut_user = obj_ws.username

                if obj_ws.password:
                    aut_pass = obj_ws.password

                if obj_ws.postman_token:
                    headers["postman-token"] = obj_ws.postman_token

                if obj_ws.authorization:
                    headers["authorization"] = obj_ws.authorization

                # Se leen los parametros ZUE_PARAMETER en el body y se asocian en base a la grilla
                if args:
                    string = obj_ws.body
                    pos_i, pos_f, i = 0, 0, 1
                    stringF = ''

                    while i != 99:
                        tmp_string = ''
                        if pos_i > 0:
                            string_a = string[pos_i:]
                        else:
                            if not string:
                                string_a = ''
                            else:
                                string_a = string
                        pos_f = string_a.find('ZUE_PARAMETER')
                        if pos_f < 0:
                            i = 99
                            stringF += string_a
                        else:
                            pos_f = pos_f + 13

                            tmp_string = string_a[:pos_f]

                            pos_i += pos_f

                            tmp_string = tmp_string.replace('ZUE_PARAMETER', str(args[count_parameter]))
                            count_parameter += 1

                            stringF += tmp_string
                    data_body = stringF

                if len(args) > count_parameter:
                    for parameters in obj_ws.parameters_id:
                        name = parameters.parameter_name
                        value = parameters.parameter_value

                        if value == 'ZUE_PARAMETER':
                            value = str(args[count_parameter])
                            count_parameter += 1


                        if not url_parameters:
                            url_parameters = '?'
                            url_parameters += name + '=' + value
                        else:
                            url_parameters += '&' + name + '=' + value

                if url_parameters:
                    final_url = url + url_parameters
                else:
                    final_url = url

                if aut_user and aut_pass:
                    response = requests.request(obj_ws.method, final_url, headers=headers, data=data_body, auth=(aut_user, aut_pass))
                else:
                    response = requests.request(obj_ws.method, final_url, data=data_body, headers=headers)

                if response.status_code == 404:
                    raise ValidationError(_("Error! No se encontró el método configurado en el servicio web " + obj_ws.name))
                
                if response:
                    if obj_ws.name == 'check_vehicle_odometer' or obj_ws.name == 'get_contract_services' or obj_ws.name == 'get_contracts_logirastreo':
                        return response.json()
                    if response.content:
                        return str(response.content)
                    else:
                        return response.json()
                else:
                    raise ValidationError(_("Error! El servicio web no retorno un valor válido."))
