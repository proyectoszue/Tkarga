from odoo import api, fields, models, _
import requests
from odoo.exceptions import ValidationError
import json
import logging
import time

_logger = logging.getLogger(__name__)

class zue_request_headers_ws(models.Model):
    _name = 'zue.request.headers.ws'
    _description = 'Headers del servicio web'

    key = fields.Char('Llave')
    value = fields.Char('Valor')
    ws_id = fields.Many2one('zue.request.ws', 'Id Servicio web')


class zue_request_parameters_ws(models.Model):
    _name = 'zue.request.parameters.ws'
    _description = 'Parámetros del servicio web'

    parameter_name = fields.Char('Nombre')
    parameter_value = fields.Char('Valor')
    without_name = fields.Boolean('Sin nombre')
    ws_id = fields.Many2one('zue.request.ws', 'Id Servicio web')


class zue_request_ws(models.Model):
    _name = 'zue.request.ws'
    _description = 'Configuración del servicio web'

    name = fields.Char(string='Nombre', required=True)
    username = fields.Char(string='Usuario autenticación básica')
    password = fields.Char(string='Contraseña autenticación básica')
    server_url = fields.Char(string='Url')
    active = fields.Boolean(string='Activo', default=True)
    method = fields.Selection([('GET', "GET"), ('POST', "POST"), ('PUT', "PUT"), ('DELETE', "DELETE")], "Método")
    postman_token = fields.Char(string='Postman-token')
    authorization = fields.Char(string='Authorization')
    parameters_id = fields.One2many('zue.request.parameters.ws', 'ws_id', string='Parámetros')
    headers_ids = fields.One2many('zue.request.headers.ws', 'ws_id', string='Headers')
    body = fields.Text('Body')
    content_type = fields.Char(string='Content-Type')
    use_certificate = fields.Boolean(string='Solicitud con certificado?', default=False)
    cert_path = fields.Char(string='Ruta del certificado')
    key_path = fields.Char(string='Ruta de la llave')
    username_auth_cert = fields.Char(string='Usuario certificado')
    password_auth_cert = fields.Char(string='Contraseña')

    sql_constraints = [
        ('name', 'UNIQUE (name)', 'Ya existe un registro con este nombre!')
    ]

    @api.model
    def connection_requests(self, *args, not_show_errors=0, decode_response=0, response_file=0, return_errors_400=0, body_text='', json_to_dict=False, forced_url=''):
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
            headers = {}

            if not obj_ws:
                raise ValidationError(_("No se ha configurado un servicio web con el nombre " + obj_ws.name))
            else:
                if obj_ws.server_url:
                    url = obj_ws.server_url
                else:
                    raise ValidationError(
                        _("No se ha configurado una URL para el servicio web con el nombre " + obj_ws.name))
                if not obj_ws.headers_ids:
                    if obj_ws.content_type:
                        headers['content-type'] = obj_ws.content_type
                        headers['cache-control'] = "no-cache"
                    else:
                        headers['content-type'] = 'application/json'
                        headers['cache-control'] = "no-cache"

                for header in obj_ws.headers_ids:
                    header_value = header.value
                    if header_value == 'ZUE_PARAMETER' and len(args) > count_parameter:
                        header_value = str(args[count_parameter])
                        count_parameter += 1
                    headers[header.key] = header_value

                if obj_ws.username:
                    aut_user = obj_ws.username

                if obj_ws.password:
                    aut_pass = obj_ws.password

                if obj_ws.postman_token:
                    headers["postman-token"] = obj_ws.postman_token

                if obj_ws.authorization:
                    token_auth = obj_ws.authorization
                    if 'ZUE_PARAMETER' in obj_ws.authorization:
                        token_auth = token_auth.replace('ZUE_PARAMETER', str(args[count_parameter]))
                        count_parameter += 1

                    headers["authorization"] = token_auth

                if body_text and not obj_ws.body:
                    data_body = body_text

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

                    if stringF:
                        data_body = stringF

                if len(args) > count_parameter:
                    param_name = 0
                    for parameters in obj_ws.parameters_id:
                        name = parameters.parameter_name
                        value = parameters.parameter_value

                        if value == 'ZUE_PARAMETER':
                            value = str(args[count_parameter])
                            count_parameter += 1

                        if parameters.without_name:
                            url_parameters += '/' + value
                        else:
                            param_name += 1
                            if not url_parameters or param_name == 1:
                                # url_parameters = '?'
                                url_parameters += '?' + name + '=' + value
                            else:
                                url_parameters += '&' + name + '=' + value

                if forced_url:
                    final_url = forced_url
                elif url_parameters:
                    final_url = url + url_parameters
                else:
                    final_url = url

                if not data_body:
                    data_body = obj_ws.body

                def is_rate_limited(response_obj):
                    response_text = (response_obj.text or '').lower()
                    return (
                        response_obj.status_code == 429
                        or 'rate limit' in response_text
                        or 'too many requests' in response_text
                    )

                def get_retry_wait_seconds(response_obj, retry_number):
                    retry_after = response_obj.headers.get('Retry-After')
                    if retry_after:
                        try:
                            retry_after_seconds = int(retry_after)
                            if retry_after_seconds > 0:
                                return retry_after_seconds
                        except (TypeError, ValueError):
                            pass
                    # Backoff corto para mantener fluidez en Odoo UI
                    return min(1 + retry_number, 4)

                response = None
                max_retries = 3
                retry_number = 0

                while retry_number <= max_retries:
                    if aut_user and aut_pass:
                        response = requests.request(
                            obj_ws.method,
                            final_url,
                            headers=headers,
                            data=data_body,
                            auth=(aut_user, aut_pass),
                        )
                    else:
                        response = requests.request(
                            obj_ws.method,
                            final_url,
                            data=data_body,
                            headers=headers,
                        )

                    if not is_rate_limited(response):
                        break

                    if retry_number == max_retries:
                        break

                    wait_seconds = get_retry_wait_seconds(response, retry_number)
                    _logger.warning(
                        "Rate limit en WS '%s'. Intento %s/%s. Esperando %s segundos.",
                        obj_ws.name,
                        retry_number + 1,
                        max_retries + 1,
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)
                    retry_number += 1

                if response.status_code == 404:
                    if not_show_errors == 0:
                        if response.text:
                            raise ValidationError(_("Error! " + str(response.text)))
                        else:
                            raise ValidationError(_("Error! No se encontró el método configurado en el servicio web " + obj_ws.name))
                    else:
                        return "Error! No se encontró el método configurado en el servicio web " + obj_ws.name

                if response.status_code >= 400 and return_errors_400 == 0:
                    def is_valid_json(text):
                        try:
                            json.loads(text)
                            return True
                        except json.JSONDecodeError:
                            return False

                    if is_valid_json(response.text):
                        response_dict = json.loads(response.text)
                    else:
                        error_msg = response.text.strip()
                        if response.status_code == 429 or 'rate limit' in error_msg.lower() or 'too many requests' in error_msg.lower():
                            return (
                                "Error: el servicio externo alcanzo el limite de peticiones.\n"
                                "Espere unos segundos y vuelva a intentar.\n"
                                "Contenido recibido:\n" + error_msg[:500]
                            )

                        return "Error: el servicio externo devolvió una respuesta no válida.\n" + "Contenido recibido:\n" + error_msg[:500]

                    if "response" in response_dict:
                        raise ValidationError(_("Error en el servicio web: " + str(response_dict["response"])))
                    elif "estado" in response_dict:
                        raise ValidationError(_("Error en el servicio web: " + str(response_dict["estado"])))
                    elif "respuesta" in response_dict:
                        raise ValidationError(_("Error en el servicio web: " + str(response_dict["respuesta"])))
                    elif "msg" in response_dict:
                        raise ValidationError(_("Error en el servicio web: " + str(response_dict["msg"])))
                    elif "message" in response_dict:
                        raise ValidationError(_("Error en el servicio web: " + str(response_dict["message"]) + "\nBody: " + str(data_body)))
                    else:
                        raise ValidationError(_("Error! se presentó un error en el servicio web "))
                else:
                    if response:
                        if response.content:
                            if json_to_dict:
                                try:
                                    return json.loads(response.content)
                                except json.JSONDecodeError:
                                    # El WS devuelve JSON inválido (claves sin comillas o comillas simples)
                                    import re
                                    text = response.content.decode('utf-8', errors='replace')
                                    text = re.sub(r'(?<!["\w])(\w+)(?=\s*:)', r'"\1"', text)
                                    text = text.replace("'", '"')

                                    try:
                                        result = json.loads(text)
                                    except json.JSONDecodeError:
                                        raise ValidationError(_(f'Respuesta inválida del servicio web "{obj_ws.name}": {text[:300]}'))

                                    if not result.get('success', True):
                                        raise ValidationError(_(f'Error en servicio web "{obj_ws.name}": {result.get("msg", "Error desconocido")}'))
                                    return result

                            if response_file:
                                return response.content

                            if decode_response:
                                return response.content.decode('UTF-8')
                            else:
                                return str(response.content, 'UTF-8')
                        else:
                            return response.json()
                    else:
                        if not_show_errors == 0:
                            raise ValidationError(_("Error! El servicio web no retorno un valor válido."))
                        else:
                            return "Error! El servicio web no retorno un valor válido."
