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

    sql_constraints = [
        ('name', 'UNIQUE (name)', 'Ya existe un registro con este nombre!')
    ]

    @api.model
    def connection_requests(self,*args):
        for obj_ws in self:
            name = ''
            value = ''
            count_parameter = 0
            
            if not obj_ws.active:
                raise ValidationError(_("El servicio web con el nombre " + obj_ws.name + " no se encuentra activo.")) 
                
            url = ''
            url_parameters = ''
            final_url = ''

            if not obj_ws:
                raise ValidationError(_("No se ha configurado un servicio web con el nombre " + obj_ws.name)) 
            else:
                if obj_ws.server_url:
                    url =obj_ws.server_url
                else:
                    raise ValidationError(_("No se ha configurado una URL para el servicio web con el nombre " + obj_ws.name)) 

                headers = {
                    'content-type': "application/json",
                    'cache-control': "no-cache"
                }

                if obj_ws.username:
                    headers["username"] = obj_ws.username

                if obj_ws.password:
                    headers["password"] = obj_ws.password

                if obj_ws.postman_token:
                    headers["postman-token"] = obj_ws.postman_token

                if obj_ws.authorization:
                    headers["authorization"] = obj_ws.authorization

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

                response = requests.request(obj_ws.method, final_url, headers=headers)

                if response.status_code == 404:
                    raise ValidationError(_("Error! No se encontró el método configurado en el servicio web " + obj_ws.name))
                
                if response:
                    return response.json()
                else:
                    raise ValidationError(_("Error! El servicio web no retorno un valor válido."))
