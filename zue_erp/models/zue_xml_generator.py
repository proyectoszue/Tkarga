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
    name_parent = fields.Char('Nombre Tag - Padre')
    code_python = fields.Text(string='Código')
    code_validation_python = fields.Text(string='Código Validación')

class zue_xml_generator_header(models.Model):
    _name = 'zue.xml.generator.header'
    _description = 'Definición XML'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Identificador',required=True)
    description = fields.Text(string='Descripción')  
    details_ids = fields.One2many('zue.xml.generator.details', 'xml_generator_id', string='Estructura del XML (Tags)', ondelete='cascade')

    sql_constraints = [
        ('name', 'UNIQUE (code)', 'Ya existe un registro con este identificador!')
    ]   


    def xml_generator(self,o):

        #Recorre estructura para armar el XML
        tag_initial = ''
        for item in sorted(self.details_ids, key=lambda x: x.sequence):
            val = ''
            validation = True
            if item.sequence == 1:
                tag_initial = item.name

            #Crear item
            if item.name.find('&') == -1:
                create_element = f"{item.name} = etree.Element('{item.name}')"
                exec(create_element)

            #Ejecutar código Python
            if item.code_python and item.is_parent == False:
                try:
                    ldict = {'o':o}
                    exec(item.code_python,ldict)
                    val = ldict.get('val')
                    cont = 0

                    if item.code_validation_python:
                        exec(item.code_validation_python, ldict)
                        validation = ldict.get('validation')

                    if validation == True:
                        if type(val) is list:
                            for i in val:
                                cont += 1
                                asigne_element = f"{item.name.replace('&',str(cont))} = etree.Element('{item.name.replace('&',str(cont))}')"
                                exec(asigne_element)
                                val = str(i)
                                asigne_element = f"{item.name.replace('&',str(cont))}.text = val"
                                exec(asigne_element)
                                if item.name_parent:
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
                                assignee_parent = f"{item.name_parent}.append({item.name})"
                                exec(assignee_parent)
                except Exception as e:
                    raise UserError(_('Error al ejecutar el código python del item %s, %s') % (item.name, e))  
            else:
                if item.name_parent:
                    assignee_parent = f"{item.name_parent}.append({item.name})"
                    exec(assignee_parent)

            tree_str = f"xml = etree.tostring({tag_initial})"
            exec(tree_str)

        xml_full_tags = etree.fromstring(eval("xml"))
        #Remover tags vacios
        for element in xml_full_tags.xpath(".//*[not(node())]"):
            element.getparent().remove(element)
        #Retornar XML Final
        xml_finally = etree.tostring(xml_full_tags, pretty_print=True)
        return xml_finally