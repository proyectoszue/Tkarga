# -*- coding: utf-8 -*-

from . import models

from odoo.exceptions import UserError
from odoo.tools.convert import convert_file


def _preserve_xmlid(env, name, record):
    data = env['ir.model.data']
    target = data.search([('module', '=', 'zue_electronic_invoice_pos'), ('name', '=', name)], limit=1)
    if target and (target.model != record._name or target.res_id != record.id):
        raise UserError('El identificador POS %s apunta a otro registro; concilie la parametrización antes de instalar.' % name)
    if target:
        target.noupdate = True
    else:
        data.create({'module': 'zue_electronic_invoice_pos', 'name': name, 'model': record._name, 'res_id': record.id, 'noupdate': True})


# Parametrización POS de fábrica: solo al instalar, reutilizando la que ya exista para no duplicarla.
def post_init_hook(env):
    module = 'zue_electronic_invoice_pos'
    for name in ('documentcufepos', 'documentpdfpos', 'documentxmlpos', 'documentStatuspos', 'uploadDocumentpos'):
        services = env['zue.request.ws'].with_context(active_test=False).search([('name', '=', name)])
        if len(services) > 1:
            raise UserError('Hay varios servicios web POS con nombre %s; concílielos antes de instalar el módulo.' % name)
        if services:
            _preserve_xmlid(env, name, services)
    # El modo update respeta noupdate incluso durante la primera instalación del puente.
    convert_file(env, module, 'data/zue_request_ws_data_pos.xml', {}, mode='update', noupdate=True)

    code = 'POSFacElectronica_FacturaTechv2'
    generators = env['zue.xml.generator.header'].search([('code', '=', code)])
    if len(generators) > 1:
        raise UserError('Hay varios generadores XML POS con código %s; concílielos antes de instalar el módulo.' % code)
    if generators:
        # Conservar íntegra la estructura personalizada, sin agregar etiquetas de fábrica.
        _preserve_xmlid(env, code, generators)
        legacy_details = env['ir.model.data'].search([
            ('module', '=', 'zue_electronic_invoice'),
            ('model', '=', 'zue.xml.generator.details'),
            ('res_id', 'in', generators.details_ids.ids),
        ])
        for detail in legacy_details:
            _preserve_xmlid(env, detail.name, env[detail.model].browse(detail.res_id))
    else:
        convert_file(env, module, 'data/zue_xml_generator_data_pos.xml', {}, mode='update', noupdate=True)
