from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval

from lxml import etree

class zue_xml_generator_details(models.Model):
    _name = 'zue.xml.generator.details'
    _description = 'Estructura del XML (Tags)'
    _order = "sequence"

    xml_generator_id = fields.Many2one('zue.xml.generator.header', 'XML', required=True, ondelete='cascade')
    name = fields.Char('Nombre Tag', required=True)
    sequence = fields.Integer(string='Secuencia', required=True)
    is_parent = fields.Boolean(string='Es Padre')
    is_for = fields.Boolean(string='Es For')
    internal_for = fields.Char('For Interno')
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


    def xml_generator(self,o):
        #Recorre estructura para armar el XML
        tag_initial = ''
        last_sequence = 0
        first_tag = ''
        old_tag = ''

        for item in sorted(self.details_ids, key=lambda x: x.sequence):
            val = ''
            for_item = ''
            validation = True
            ldict = {'o': o}

            item_attributes_code_python = f",{item.attributes_code_python}" if item.attributes_code_python else ""
            if item.code_validation_python and item_attributes_code_python != "":
                exec(item.code_validation_python, ldict)
                validation = ldict.get('validation')
                if validation == False:
                    item_attributes_code_python = ""

            if item.sequence == 1:
                tag_initial = item.name
                old_tag = tag_initial
                if item.code_validation_python:
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
                    exec(create_element)

            # Ejecutar código Python
            if item.code_python and item.is_parent == False:
                try:
                    if item.code_validation_python:
                        exec(item.code_validation_python, ldict)
                        validation = ldict.get('validation')

                    if validation == False:
                        continue

                    ldict = {'o':o}
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
                    raise UserError(_('Error al ejecutar el código python del item %s, %s') % (item.name, e))
            else:
                if item.name_parent:
                    if item.name_parent == old_tag and first_tag!='':
                        assignee_parent = f"{first_tag}.append({item.name})"
                    else:
                        assignee_parent = f"{item.name_parent}.append({item.name})"

                    exec(assignee_parent)

                if item.code_python and item.is_for:
                    ldict = {'o': o}
                    exec(item.code_python, ldict)
                    # val = ldict.get('val')
                    for_item = ldict.get('for_item')

                    max_rows = len(for_item)
                    actual_sequence = item.sequence

                    for i in range(max_rows):
                        break_for = False
                        for second_item in sorted(self.details_ids.filtered(lambda x: x.sequence >= actual_sequence), key=lambda x: x.sequence):
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

                                    ldict = {'o': o}
                                    exec(to_execute, ldict)
                                    val = ldict.get('val')
                                    internal_max_rows = len(val)

                                    to_validate = ''
                                    if internal_max_rows > 0:
                                        for j in range(internal_max_rows):
                                            break_for = True
                                            for third_item in sorted(self.details_ids.filtered(lambda x: x.sequence >= internal_sequence), key=lambda x: x.sequence):
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

                                                            exec(to_validate, ldict)
                                                            validation = ldict.get('validation')

                                                            if validation == False:
                                                                continue

                                                        create_element = f"{third_item.name} = etree.Element('{third_item.name}'{item_attributes_code_python})"
                                                        exec(create_element)

                                                    if third_item.code_python and third_item.is_parent == False:
                                                        ldict = {'o': o}
                                                        if third_item.code_python == 'index':
                                                            val = str(i + 1)
                                                        else:
                                                            to_execute = third_item.code_python

                                                            if 'index_i' in third_item.code_python:
                                                                to_execute = to_execute.replace('index_i', str(i))
                                                            if 'index_j' in third_item.code_python:
                                                                to_execute = to_execute.replace('index_j', str(j))

                                                            exec(to_execute, ldict)
                                                            val = ldict.get('val')
                                                        cont = 0

                                                        if third_item.code_validation_python:
                                                            to_validate = third_item.code_validation_python

                                                            if 'index_i' in to_validate:
                                                                to_validate = to_validate.replace('index_i', str(i))
                                                            if 'index_j' in to_validate:
                                                                to_validate = to_validate.replace('index_j', str(j))

                                                            exec(to_validate, ldict)
                                                            validation = ldict.get('validation')

                                                        if validation == True:
                                                            if type(val) is list:
                                                                for i in val:
                                                                    cont += 1
                                                                    asigne_element = f"{third_item.name.replace('&', str(cont))} = etree.Element('{third_item.name.replace('&', str(cont))}'{item_attributes_code_python})"
                                                                    exec(asigne_element)
                                                                    val = str(i)
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
                                            create_element = f"{second_item.name} = etree.Element('{second_item.name}'{item_attributes_code_python})"
                                            exec(create_element)

                                            if second_item.name_parent == old_tag:
                                                assignee_parent = f"{first_tag}.append({second_item.name})"
                                            else:
                                                assignee_parent = f"{first_tag}.append({second_item.name})"

                                            exec(assignee_parent)
                                else:
                                    if second_item.name.find('&') == -1:
                                        create_element = f"{second_item.name} = etree.Element('{second_item.name}'{item_attributes_code_python})"
                                        exec(create_element)

                                    if second_item.code_python and second_item.is_parent == False:
                                        ldict = {'o': o,
                                                 'for_item': for_item}

                                        if second_item.code_python == 'index':
                                            val = str(i + 1)
                                        elif 'index_i' in second_item.code_python:
                                            to_execute = second_item.code_python.replace('index_i', str(i))
                                            exec(to_execute, ldict)
                                            val = ldict.get('val')
                                            for_item = ldict.get('for_item')
                                        else:
                                            if 'val =' in second_item.code_python:
                                                to_execute = second_item.code_python
                                            else:
                                                to_execute = item.code_python.replace('for_item =', 'val =') + '[' + str(i) + '].' + second_item.code_python
                                            exec(to_execute, ldict)

                                            val = ldict.get('val')
                                        cont = 0

                                        if second_item.code_validation_python:
                                            exec(second_item.code_validation_python, ldict)
                                            validation = ldict.get('validation')
                                        else:
                                            validation = True

                                        if validation:
                                            if type(val) is list:
                                                for i in val:
                                                    cont += 1
                                                    asigne_element = f"{second_item.name.replace('&', str(cont))} = etree.Element('{second_item.name.replace('&', str(cont))}'{item_attributes_code_python})"
                                                    exec(asigne_element)
                                                    val = str(i)
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
            exec(tree_str)

        xml_full_tags = etree.fromstring(eval("xml"))
        #Remover tags vacios se verifica 3 veces
        for v in range(1,3):
            for element in xml_full_tags.xpath(".//*[not(node())]"):
                if element.attrib == {}:
                    element.getparent().remove(element)
        #Retornar XML Final
        xml_finally = etree.tostring(xml_full_tags, pretty_print=True)
        return xml_finally