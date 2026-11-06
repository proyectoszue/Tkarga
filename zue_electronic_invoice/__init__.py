# -*- coding: utf-8 -*-

from . import controllers
from . import models

from odoo.tools.convert import convert_file


# Parametrización de fábrica: solo en instalaciones nuevas, para no duplicar la de bases que ya la tienen configurada.
def post_init_hook(env):
    for filename in ('zue_account_tax_type_data', 'zue_responsibilities_rut_data', 'product_category_data', 'product_template_data', 'zue_request_ws_data',
                     'fe_payments_options_data', 'zue_xml_generator_data_nom_elect', 'zue_xml_generator_data_elect_invo', 'zue_xml_generator_data_doc_sop'):
        convert_file(env, 'zue_electronic_invoice', f'data/{filename}.xml', {}, mode='init', noupdate=True)
