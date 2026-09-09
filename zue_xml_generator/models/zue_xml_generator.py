from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

from datetime import datetime, timedelta

from lxml import etree
import pytz
import re


def _truncate_xml_code_snippet(text, max_len=160):
    if not text:
        return ''
    t = str(text).replace('\n', ' ').strip()
    return t if len(t) <= max_len else '%s...' % t[:max_len]

class zue_xml_generator_details(models.Model):
    _name = 'zue.xml.generator.details'
    _description = 'Estructura del XML (Tags)'
    _order = "sequence"

    xml_generator_id = fields.Many2one('zue.xml.generator.header', 'XML', required=True, ondelete='cascade')
    name = fields.Char('Nombre Tag', required=True)
    sequence = fields.Integer(string='Secuencia', required=True)
    is_parent = fields.Boolean(string='Es Padre')
    is_for = fields.Boolean(string='Es For')
    internal_for = fields.Text('For Interno')
    name_parent = fields.Char('Nombre Tag - Padre')
    attributes_code_python = fields.Text(string='Código Atributos')
    code_python = fields.Text(string='Código Valor')
    code_validation_python = fields.Text(string='Código Validación Valor')

class zue_xml_generator_header(models.Model):
    _name = 'zue.xml.generator.header'
    _description = 'Definición XML'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Identificador',required=True)
    description = fields.Text(string='Descripción')  
    details_ids = fields.One2many('zue.xml.generator.details', 'xml_generator_id', string='Estructura del XML (Tags)')

    sql_constraints = [
        ('name', 'UNIQUE (code)', 'Ya existe un registro con este identificador!')
    ]

    def _format_xml_generator_error(self, xml_err_ctx, item, exc):
        lines = [
            _('Error al generar el XML (definición: "%s").') % (self.name,),
            _('Tag: %s') % xml_err_ctx.get('tag', item.name),
            _('Secuencia: %s') % xml_err_ctx.get('seq', item.sequence),
        ]
        if xml_err_ctx.get('i') is not None:
            lines.append(_('Iteración del for (i): %s') % xml_err_ctx['i'])
        if xml_err_ctx.get('j') is not None:
            lines.append(_('Iteración del for anidado (j): %s') % xml_err_ctx['j'])
        if xml_err_ctx.get('etapa'):
            lines.append(_('Etapa: %s') % xml_err_ctx['etapa'])
        if xml_err_ctx.get('bloque'):
            lines.append(_('Contexto: %s') % xml_err_ctx['bloque'])
        if xml_err_ctx.get('codigo_preview'):
            lines.append(_('Fragmento de código (valor/validación): %s') % xml_err_ctx['codigo_preview'])
        lines.append('')
        lines.append(_('Detalle: %s') % str(exc))
        return '\n'.join(lines)

    def xml_generator(self,o):
        #Recorre estructura para armar el XML
        tag_initial = ''
        last_sequence = 0
        first_tag = ''
        old_tag = ''

        for item in sorted(self.details_ids, key=lambda x: x.sequence):
            xml_err_ctx = {
                'tag': item.name,
                'seq': item.sequence,
                'i': None,
                'j': None,
                'etapa': None,
                'bloque': _('Principal'),
                'codigo_preview': None,
            }
            val = ''
            for_item = ''
            validation = True
            ldict = {'o': o}
            try:
                if item.attributes_code_python and 'not_include_in_for' not in item.attributes_code_python:
                    item_attributes_code_python = f",{item.attributes_code_python}"
                else:
                    item_attributes_code_python = ""

                if '@current_datetime' in item_attributes_code_python:
                    current_datetime_utc = datetime.now(pytz.utc).replace(second=0, microsecond=0)
                    match = re.search(
                        r"@current_datetime\+'(?P<offset>[+-]\d{2}:\d{2})'",
                        item_attributes_code_python,
                    )
                    if not match:
                        raise ValidationError(_(
                            "Si se usa @current_datetime se debe especificar la zona horaria, "
                            "así para Colombia: @current_datetime+'-05:00'"
                        ))
                    timezone_str = match.group('offset')
                    timezone_sign = -1 if timezone_str.startswith('-') else 1
                    timezone_delta = timedelta(
                        hours=timezone_sign * int(timezone_str[1:3]),
                        minutes=timezone_sign * int(timezone_str[4:6]),
                    )
                    formatted_datetime = (current_datetime_utc + timezone_delta).strftime('%Y-%m-%dT%H:%M:%S')
                    item_attributes_code_python = item_attributes_code_python.replace(
                        '@current_datetime', f"'{formatted_datetime}'"
                    )
                if item.code_validation_python and item_attributes_code_python != "":
                    xml_err_ctx.update({
                        'etapa': _('Validación para armar atributos del tag'),
                        'codigo_preview': _truncate_xml_code_snippet(item.code_validation_python),
                    })
                    exec(item.code_validation_python, ldict)
                    validation = ldict.get('validation')
                    if validation == False:
                        item_attributes_code_python = ""

                if item.sequence == 1:
                    tag_initial = item.name
                    old_tag = tag_initial
                    if item.code_validation_python:
                        xml_err_ctx.update({
                            'etapa': _('Validación del tag raíz (sequence=1)'),
                            'codigo_preview': _truncate_xml_code_snippet(item.code_validation_python),
                        })
                        exec(item.code_validation_python, ldict)
                        first_tag = ldict.get('tag')
                        if first_tag:
                            tag_initial = first_tag


                if item.is_for and item.sequence <= last_sequence:
                    continue
                else:
                    # Crear item
                    if item.name.find('&') == -1:
                        #ldict = {'o': o}
                        if item.sequence == 1 and first_tag:
                            create_element = f"{tag_initial} = etree.Element('{tag_initial}'{item_attributes_code_python})"
                        else:
                            create_element = f"{item.name} = etree.Element('{item.name}'{item_attributes_code_python})"
                        xml_err_ctx.update({
                            'etapa': _('Creación del elemento XML (etree.Element)'),
                            'codigo_preview': None,
                        })
                        exec(create_element)

                # Ejecutar código Python
                if item.code_python and item.is_parent == False:
                    try:
                        if item.code_validation_python:
                            xml_err_ctx.update({
                                'etapa': _('Validación antes del código valor'),
                                'codigo_preview': _truncate_xml_code_snippet(item.code_validation_python),
                            })
                            exec(item.code_validation_python, ldict)
                            validation = ldict.get('validation')

                        if validation == False:
                            continue

                        ldict = {'o':o}
                        xml_err_ctx.update({
                            'tag': item.name,
                            'seq': item.sequence,
                            'etapa': _('Ejecución código valor'),
                            'codigo_preview': _truncate_xml_code_snippet(item.code_python),
                        })
                        exec(item.code_python,ldict)
                        val = ldict.get('val')

                        cont = 0

                        if validation == True:
                            if type(val) is list:
                                for i in val:
                                    cont += 1
                                    asigne_element = f"{item.name.replace('&',str(cont))} = etree.Element('{item.name.replace('&',str(cont))}'{item_attributes_code_python})"
                                    exec(asigne_element)
                                    val = str(i)
                                    asigne_element = f"{item.name.replace('&',str(cont))}.text = val"
                                    exec(asigne_element)
                                    if item.name_parent:
                                        if item.name_parent == old_tag and first_tag!='':
                                            assignee_parent = f"{first_tag}.append({item.name.replace('&', str(cont))})"
                                        else:
                                            assignee_parent = f"{item.name_parent}.append({item.name.replace('&',str(cont))})"
                                        exec(assignee_parent)
                            else:
                                if type(val) is float:
                                    val = "{:.2f}".format(val)
                                else:
                                    val = str(val)
                                asigne_element = f"{item.name}.text = val"
                                exec(asigne_element)
                                if item.name_parent:
                                    if item.name_parent == old_tag and first_tag!='':
                                        assignee_parent = f"{first_tag}.append({item.name})"
                                    else:
                                        assignee_parent = f"{item.name_parent}.append({item.name})"

                                    exec(assignee_parent)
                    except Exception as e:
                        raise ValidationError(self._format_xml_generator_error(xml_err_ctx, item, e))
                else:
                    if item.name_parent:
                        if item.name_parent == old_tag and first_tag!='':
                            assignee_parent = f"{first_tag}.append({item.name})"
                        else:
                            assignee_parent = f"{item.name_parent}.append({item.name})"

                        exec(assignee_parent)

                    if item.code_python and item.is_for:
                        ldict = {'o': o}
                        xml_err_ctx.update({
                            'etapa': _('Código que obtiene la lista del for (for_item)'),
                            'codigo_preview': _truncate_xml_code_snippet(item.code_python),
                        })
                        exec(item.code_python, ldict)
                        # val = ldict.get('val')
                        for_item = ldict.get('for_item')

                        if for_item:
                            max_rows = len(for_item)
                        else:
                            max_rows = 0

                        actual_sequence = item.sequence

                        for i in range(max_rows):
                            break_for = False
                            for second_item in sorted(self.details_ids.filtered(lambda x: x.sequence >= actual_sequence), key=lambda x: x.sequence):
                                xml_err_ctx.update({
                                    'tag': second_item.name,
                                    'seq': second_item.sequence,
                                    'i': i,
                                    'j': None,
                                    'bloque': _('Dentro del for (padre: "%s")') % item.name,
                                })
                                if break_for:
                                    break

                                last_sequence = second_item.sequence
                                internal_sequence = second_item.sequence

                                if second_item.sequence < actual_sequence or second_item.is_for == False:
                                    break
                                else:
                                    if second_item.internal_for:
                                        validate_sequence = True
                                        to_execute = second_item.internal_for

                                        if 'index_i' in second_item.internal_for:
                                            to_execute = to_execute.replace('index_i', str(i))

                                        ldict = {
                                            'o': o,
                                            'for_item': for_item,
                                            'index_i': i,
                                        }
                                        xml_err_ctx.update({
                                            'etapa': _('For interno (internal_for)'),
                                            'codigo_preview': _truncate_xml_code_snippet(to_execute),
                                        })
                                        exec(to_execute, ldict)
                                        val = ldict.get('val')
                                        internal_max_rows = len(val)

                                        to_validate = ''
                                        if internal_max_rows > 0:
                                            for j in range(internal_max_rows):
                                                break_for = True
                                                ldict['index_j'] = j
                                                for third_item in sorted(self.details_ids.filtered(lambda x: x.sequence >= internal_sequence), key=lambda x: x.sequence):
                                                    xml_err_ctx.update({
                                                        'tag': third_item.name,
                                                        'seq': third_item.sequence,
                                                        'i': i,
                                                        'j': j,
                                                        'bloque': _('For anidado (segundo nivel "%s", padre for: "%s")') % (second_item.name, item.name),
                                                    })
                                                    if third_item.sequence < internal_sequence or third_item.is_for == False:
                                                        break
                                                    else:
                                                        last_sequence = third_item.sequence
                                                        to_execute = ''

                                                        if third_item.name.find('&') == -1:
                                                            if third_item.code_validation_python:
                                                                to_validate = third_item.code_validation_python

                                                                if 'index_i' in to_validate:
                                                                    to_validate = to_validate.replace('index_i', str(i))
                                                                if 'index_j' in to_validate:
                                                                    to_validate = to_validate.replace('index_j', str(j))

                                                                xml_err_ctx.update({
                                                                    'etapa': _('Validación (tercer nivel)'),
                                                                    'codigo_preview': _truncate_xml_code_snippet(to_validate),
                                                                })
                                                                exec(to_validate, ldict)
                                                                validation = ldict.get('validation')

                                                                if validation == False:
                                                                    continue

                                                            third_item_attributes = f",{third_item.attributes_code_python}" if third_item.attributes_code_python else ""
                                                            third_item_attributes = third_item_attributes.replace(
                                                                'index_i', str(i)
                                                            ).replace('index_j', str(j)).replace('index', str(i + 1))
                                                            create_element = f"{third_item.name} = etree.Element('{third_item.name}'{third_item_attributes})"
                                                            xml_err_ctx.update({
                                                                'etapa': _('Creación elemento (tercer nivel)'),
                                                                'codigo_preview': None,
                                                            })
                                                            exec(create_element)

                                                        if third_item.code_python and third_item.is_parent == False:
                                                            ldict = {
                                                                'o': o,
                                                                'for_item': for_item,
                                                                'index_i': i,
                                                                'index_j': j,
                                                            }
                                                            if third_item.code_python == 'index':
                                                                xml_err_ctx.update({
                                                                    'etapa': _('Código valor literal "index" (tercer nivel)'),
                                                                    'codigo_preview': 'index',
                                                                })
                                                                val = str(i + 1)
                                                            else:
                                                                to_execute = third_item.code_python

                                                                if 'index_i' in third_item.code_python:
                                                                    to_execute = to_execute.replace('index_i', str(i))
                                                                if 'index_j' in third_item.code_python:
                                                                    to_execute = to_execute.replace('index_j', str(j))

                                                                xml_err_ctx.update({
                                                                    'etapa': _('Ejecución código valor (tercer nivel)'),
                                                                    'codigo_preview': _truncate_xml_code_snippet(to_execute),
                                                                })
                                                                exec(to_execute, ldict)
                                                                val = ldict.get('val')
                                                            cont = 0

                                                            if third_item.code_validation_python:
                                                                to_validate = third_item.code_validation_python

                                                                if 'index_i' in to_validate:
                                                                    to_validate = to_validate.replace('index_i', str(i))
                                                                if 'index_j' in to_validate:
                                                                    to_validate = to_validate.replace('index_j', str(j))

                                                                xml_err_ctx.update({
                                                                    'etapa': _('Validación post-valor (tercer nivel)'),
                                                                    'codigo_preview': _truncate_xml_code_snippet(to_validate),
                                                                })
                                                                exec(to_validate, ldict)
                                                                validation = ldict.get('validation')

                                                            if validation == True:
                                                                if type(val) is list:
                                                                    for _xmlgen_v in val:
                                                                        cont += 1
                                                                        third_item_attributes = f",{third_item.attributes_code_python}" if third_item.attributes_code_python else ""
                                                                        third_item_attributes = third_item_attributes.replace(
                                                                            'index_i', str(i)
                                                                        ).replace('index_j', str(j)).replace('index', str(i + 1))
                                                                        asigne_element = f"{third_item.name.replace('&', str(cont))} = etree.Element('{third_item.name.replace('&', str(cont))}'{third_item_attributes})"
                                                                        exec(asigne_element)
                                                                        val = str(_xmlgen_v)
                                                                        asigne_element = f"{third_item.name.replace('&', str(cont))}.text = val"
                                                                        exec(asigne_element)
                                                                        if third_item.name_parent:
                                                                            if third_item.name_parent == old_tag:
                                                                                assignee_parent = f"{first_tag}.append({third_item.name.replace('&', str(cont))})"
                                                                            else:
                                                                                assignee_parent = f"{third_item.name_parent}.append({third_item.name.replace('&', str(cont))})"

                                                                            exec(assignee_parent)
                                                                else:
                                                                    if type(val) is float:
                                                                        val = "{:.2f}".format(val)
                                                                    else:
                                                                        val = str(val)
                                                                    asigne_element = f"{third_item.name}.text = val"
                                                                    exec(asigne_element)
                                                                    if third_item.name_parent:
                                                                        if third_item.name_parent == old_tag:
                                                                            assignee_parent = f"{first_tag}.append({third_item.name})"
                                                                        else:
                                                                            assignee_parent = f"{third_item.name_parent}.append({third_item.name})"

                                                                        exec(assignee_parent)
                                                        else:
                                                            if third_item.name_parent:
                                                                if third_item.name_parent == old_tag:
                                                                    assignee_parent = f"{first_tag}.append({third_item.name})"
                                                                else:
                                                                    assignee_parent = f"{third_item.name_parent}.append({third_item.name})"

                                                                exec(assignee_parent)
                                        else:
                                            if second_item.name_parent:
                                                second_item_attributes = f",{second_item.attributes_code_python}" if second_item.attributes_code_python else ""
                                                second_item_attributes = second_item_attributes.replace(
                                                    'index_i', str(i)
                                                ).replace('index', str(i + 1))
                                                create_element = f"{second_item.name} = etree.Element('{second_item.name}'{second_item_attributes})"
                                                xml_err_ctx.update({
                                                    'etapa': _('Creación elemento (segundo nivel, sin internal_for)'),
                                                    'codigo_preview': _truncate_xml_code_snippet(create_element),
                                                })
                                                exec(create_element)

                                                if second_item.name_parent == old_tag:
                                                    assignee_parent = f"{first_tag}.append({second_item.name})"
                                                else:
                                                    assignee_parent = f"{second_item.name_parent}.append({second_item.name})"

                                                exec(assignee_parent)
                                    else:
                                        if second_item.name.find('&') == -1:
                                            if second_item.attributes_code_python and 'not_include_in_for' in second_item.attributes_code_python:
                                                continue
                                            second_item_attributes = f",{second_item.attributes_code_python}" if second_item.attributes_code_python else ""
                                            second_item_attributes = second_item_attributes.replace(
                                                'index_i', str(i)
                                            ).replace('index', str(i + 1))
                                            create_element = f"{second_item.name} = etree.Element('{second_item.name}'{second_item_attributes})"
                                            xml_err_ctx.update({
                                                'etapa': _('Creación elemento (segundo nivel)'),
                                                'codigo_preview': _truncate_xml_code_snippet(create_element),
                                            })
                                            exec(create_element)

                                        if second_item.code_python and second_item.is_parent == False:
                                            ldict = {
                                                'o': o,
                                                'for_item': for_item,
                                                'index_i': i,
                                                'index_j': 0,
                                            }

                                            if second_item.code_validation_python:
                                                to_validate = second_item.code_validation_python
                                                if 'index_i' in to_validate:
                                                    to_validate = to_validate.replace('index_i', str(i))

                                                xml_err_ctx.update({
                                                    'etapa': _('Validación antes del código valor (segundo nivel)'),
                                                    'codigo_preview': _truncate_xml_code_snippet(to_validate),
                                                })
                                                exec(to_validate, ldict)
                                                validation = ldict.get('validation')
                                            else:
                                                validation = True

                                            if not validation:
                                                continue

                                            if second_item.code_python == 'index':
                                                xml_err_ctx.update({
                                                    'etapa': _('Código valor literal "index" (segundo nivel)'),
                                                    'codigo_preview': 'index',
                                                })
                                                val = str(i + 1)
                                            elif 'index_i' in second_item.code_python:
                                                to_execute = second_item.code_python.replace('index_i', str(i))
                                                xml_err_ctx.update({
                                                    'etapa': _('Ejecución código valor (segundo nivel)'),
                                                    'codigo_preview': _truncate_xml_code_snippet(to_execute),
                                                })
                                                exec(to_execute, ldict)
                                                val = ldict.get('val')
                                                for_item = ldict.get('for_item')
                                            else:
                                                if 'val =' in second_item.code_python:
                                                    to_execute = second_item.code_python
                                                else:
                                                    to_execute = item.code_python.replace('for_item =', 'val =') + '[' + str(i) + '].' + second_item.code_python
                                                xml_err_ctx.update({
                                                    'etapa': _('Ejecución código valor (segundo nivel)'),
                                                    'codigo_preview': _truncate_xml_code_snippet(to_execute),
                                                })
                                                exec(to_execute, ldict)

                                                val = ldict.get('val')
                                            cont = 0

                                            if second_item.code_validation_python:
                                                to_validate = second_item.code_validation_python
                                                if 'index_i' in to_validate:
                                                    to_validate = to_validate.replace('index_i', str(i))

                                                xml_err_ctx.update({
                                                    'etapa': _('Validación post-valor (segundo nivel)'),
                                                    'codigo_preview': _truncate_xml_code_snippet(to_validate),
                                                })
                                                exec(to_validate, ldict)
                                                validation = ldict.get('validation')
                                            else:
                                                validation = True

                                            if validation:
                                                if type(val) is list:
                                                    for _xmlgen_v2 in val:
                                                        cont += 1
                                                        second_item_attributes = f",{second_item.attributes_code_python}" if second_item.attributes_code_python else ""
                                                        second_item_attributes = second_item_attributes.replace(
                                                            'index_i', str(i)
                                                        ).replace('index', str(i + 1))
                                                        asigne_element = f"{second_item.name.replace('&', str(cont))} = etree.Element('{second_item.name.replace('&', str(cont))}'{second_item_attributes})"
                                                        exec(asigne_element)
                                                        val = str(_xmlgen_v2)
                                                        asigne_element = f"{second_item.name.replace('&', str(cont))}.text = val"
                                                        exec(asigne_element)
                                                        if second_item.name_parent:
                                                            if second_item.name_parent == old_tag:
                                                                assignee_parent = f"{first_tag}.append({second_item.name.replace('&', str(cont))})"
                                                            else:
                                                                assignee_parent = f"{second_item.name_parent}.append({second_item.name.replace('&', str(cont))})"

                                                            exec(assignee_parent)
                                                else:
                                                    if type(val) is float:
                                                        val = "{:.2f}".format(val)
                                                    else:
                                                        val = str(val)
                                                    asigne_element = f"{second_item.name}.text = val"
                                                    exec(asigne_element)
                                                    if second_item.name_parent:
                                                        if second_item.name_parent == old_tag:
                                                            assignee_parent = f"{first_tag}.append({second_item.name})"
                                                        else:
                                                            assignee_parent = f"{second_item.name_parent}.append({second_item.name})"

                                                        exec(assignee_parent)
                                        else:
                                            if second_item.name_parent:
                                                if second_item.name_parent == old_tag and first_tag!='':
                                                    assignee_parent = f"{first_tag}.append({second_item.name})"
                                                else:
                                                    assignee_parent = f"{second_item.name_parent}.append({second_item.name})"

                                                exec(assignee_parent)


                tree_str = f"xml = etree.tostring({tag_initial})"
                xml_err_ctx.update({
                    'tag': tag_initial,
                    'etapa': _('Serialización del XML (etree.tostring)'),
                    'bloque': _('Raíz del documento: "%s"') % tag_initial,
                    'codigo_preview': _truncate_xml_code_snippet(tree_str),
                })
                exec(tree_str)
            except Exception as e:
                raise ValidationError(self._format_xml_generator_error(xml_err_ctx, item, e))

        xml_full_tags = etree.fromstring(eval("xml"))
        #Remover tags vacios se verifica 3 veces
        for v in range(1,3):
            for element in xml_full_tags.xpath(".//*[not(node())]"):
                if element.attrib == {}:
                    element.getparent().remove(element)
        #Retornar XML Final
        xml_finally = etree.tostring(xml_full_tags, pretty_print=True)
        return xml_finally
