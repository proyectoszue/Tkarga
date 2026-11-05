from odoo.exceptions import UserError


# Solo identificadores retirados del módulo anterior con un receptor inequívoco.
SPLIT_XMLIDS = {
    'zue_product_configuration': (
        ('zue_autoparts.access_stock_brands', 'access_stock_brands', 'ir.model.access'),
        ('zue_autoparts.access_stock_class', 'access_stock_class', 'ir.model.access'),
        ('zue_autoparts.access_stock_segments', 'access_stock_segments', 'ir.model.access'),
        ('zue_autoparts.access_stock_subsegments', 'access_stock_subsegments', 'ir.model.access'),
        ('zue_autoparts.access_stock_type', 'access_stock_type', 'ir.model.access'),
        ('zue_autoparts.access_zue_attributes_autoparts', 'access_zue_attributes_autoparts', 'ir.model.access'),
        ('zue_autoparts.access_zue_market_research', 'access_zue_market_research', 'ir.model.access'),
        ('zue_autoparts.access_zue_market_research_x_product', 'access_zue_market_research_x_product', 'ir.model.access'),
        ('zue_autoparts.access_zue_product_location', 'access_zue_product_location', 'ir.model.access'),
        ('zue_autoparts.access_zue_settings_autoparts', 'access_zue_settings_autoparts', 'ir.model.access'),
        ('zue_autoparts.access_zue_special_locations', 'access_zue_special_locations', 'ir.model.access'),
        ('zue_autoparts.action_market_research', 'action_market_research', 'ir.actions.act_window'),
        ('zue_autoparts.action_settings_attributes_autoparts', 'action_settings_attributes_autoparts', 'ir.actions.act_window'),
        ('zue_autoparts.action_stock_brands', 'action_stock_brands', 'ir.actions.act_window'),
        ('zue_autoparts.action_stock_class', 'action_stock_class', 'ir.actions.act_window'),
        ('zue_autoparts.action_stock_segments', 'action_stock_segments', 'ir.actions.act_window'),
        ('zue_autoparts.action_stock_subsegments', 'action_stock_subsegments', 'ir.actions.act_window'),
        ('zue_autoparts.action_stock_type', 'action_stock_type', 'ir.actions.act_window'),
        ('zue_autoparts.action_zue_special_locations', 'action_zue_special_locations', 'ir.actions.act_window'),
        ('zue_autoparts.market_research_list', 'market_research_list', 'ir.ui.view'),
        ('zue_autoparts.menu_market_research', 'menu_market_research', 'ir.ui.menu'),
        ('zue_autoparts.menu_master_data', 'menu_master_data', 'ir.ui.menu'),
        ('zue_autoparts.menu_settings_attributes_autoparts', 'menu_settings_attributes_autoparts', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_brands', 'menu_stock_brands', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_class', 'menu_stock_class', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_conf_brands', 'menu_stock_conf_brands', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_division', 'menu_stock_division', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_family', 'menu_stock_family', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_segments', 'menu_stock_segments', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_subsegments', 'menu_stock_subsegments', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_type', 'menu_stock_type', 'ir.ui.menu'),
        ('zue_autoparts.menu_stock_types', 'menu_stock_types', 'ir.ui.menu'),
        ('zue_autoparts.res_country_form_company', 'res_country_form_company', 'ir.ui.view'),
        ('zue_autoparts.settings_attributes_autoparts_form', 'settings_attributes_autoparts_form', 'ir.ui.view'),
        ('zue_autoparts.settings_attributes_autoparts_list', 'settings_attributes_autoparts_list', 'ir.ui.view'),
        ('zue_autoparts.stock_brands_list', 'stock_brands_list', 'ir.ui.view'),
        ('zue_autoparts.stock_brands_search', 'stock_brands_search', 'ir.ui.view'),
        ('zue_autoparts.stock_class_form', 'stock_class_form', 'ir.ui.view'),
        ('zue_autoparts.stock_class_search', 'stock_class_search', 'ir.ui.view'),
        ('zue_autoparts.stock_class_tree', 'stock_class_tree', 'ir.ui.view'),
        ('zue_autoparts.stock_segments_list', 'stock_segments_list', 'ir.ui.view'),
        ('zue_autoparts.stock_segments_search', 'stock_segments_search', 'ir.ui.view'),
        ('zue_autoparts.stock_subsegments_list', 'stock_subsegments_list', 'ir.ui.view'),
        ('zue_autoparts.stock_subsegments_search', 'stock_subsegments_search', 'ir.ui.view'),
        ('zue_autoparts.stock_type_list', 'stock_type_list', 'ir.ui.view'),
        ('zue_autoparts.stock_type_search', 'stock_type_search', 'ir.ui.view'),
        ('zue_autoparts.view_zue_autoparts_form_stock_location', 'view_zue_autoparts_form_stock_location', 'ir.ui.view'),
        ('zue_autoparts.view_zue_autoparts_product_pricelist_form', 'view_zue_autoparts_product_pricelist_form', 'ir.ui.view'),
        ('zue_autoparts.view_zue_autoparts_search_product_template', 'view_zue_autoparts_search_product_template', 'ir.ui.view'),
        ('zue_autoparts.view_zue_product_location_tree', 'view_zue_product_location_tree', 'ir.ui.view'),
        ('zue_autoparts.zue_special_locations_list', 'zue_special_locations_list', 'ir.ui.view'),
        ('zue_autoparts.zue_special_locations_search', 'zue_special_locations_search', 'ir.ui.view'),
        ('zue_imports_account.access_zue_tariffs_imports', 'access_zue_tariffs_imports', 'ir.model.access'),
    ),
    'zue_maintenance': (
        ('zue_customizations_sole.access_zue_areas', 'access_zue_areas', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_failure_causes', 'access_zue_failure_causes', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_failure_origin', 'access_zue_failure_origin', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_maintenance_equipment_category_models', 'access_zue_maintenance_equipment_category_models', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_maintenance_replacement_part_detail', 'access_zue_maintenance_replacement_part_detail', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_maintenance_routines', 'access_zue_maintenance_routines', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_maintenance_routines_detail', 'access_zue_maintenance_routines_detail', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_measurement_value', 'access_zue_measurement_value', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_measurement_value_detail', 'access_zue_measurement_value_detail', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_moved_contract_detail', 'access_zue_moved_contract_detail', 'ir.model.access'),
        ('zue_customizations_sole.action_zue_equipment_category_models', 'action_zue_equipment_category_models', 'ir.actions.act_window'),
        ('zue_customizations_sole.actions_zue_areas', 'actions_zue_areas', 'ir.actions.act_window'),
        ('zue_customizations_sole.actions_zue_failure_causes', 'actions_zue_failure_causes', 'ir.actions.act_window'),
        ('zue_customizations_sole.actions_zue_failure_origin', 'actions_zue_failure_origin', 'ir.actions.act_window'),
        ('zue_customizations_sole.actions_zue_measurement_table', 'actions_zue_measurement_table', 'ir.actions.act_window'),
        ('zue_customizations_sole.menu_equipment_category_models', 'menu_equipment_category_models', 'ir.ui.menu'),
        ('zue_customizations_sole.menu_service_type', 'menu_service_type', 'ir.ui.menu'),
        ('zue_customizations_sole.menu_zue_areas', 'menu_zue_areas', 'ir.ui.menu'),
        ('zue_customizations_sole.menu_zue_failure_causes', 'menu_zue_failure_causes', 'ir.ui.menu'),
        ('zue_customizations_sole.menu_zue_failure_origin', 'menu_zue_failure_origin', 'ir.ui.menu'),
        ('zue_customizations_sole.menu_zue_maintenance_process', 'menu_zue_maintenance_process', 'ir.ui.menu'),
        ('zue_customizations_sole.menu_zue_measurement_value', 'menu_zue_measurement_value', 'ir.ui.menu'),
        ('zue_customizations_sole.view_zue_measurement_table_tree', 'view_zue_measurement_table_tree', 'ir.ui.view'),
        ('zue_customizations_sole.zue_failure_causes_form', 'zue_failure_causes_form', 'ir.ui.view'),
        ('zue_customizations_sole.zue_failure_causes_popup_view', 'zue_failure_causes_popup_view', 'ir.ui.view'),
        ('zue_customizations_sole.zue_failure_causes_tree', 'zue_failure_causes_tree', 'ir.ui.view'),
        ('zue_customizations_sole.zue_failure_origin_tree', 'zue_failure_origin_tree', 'ir.ui.view'),
    ),
    'zue_external_service': (
        ('zue_customizations_sole.access_zue_maintenance_routine_line', 'access_zue_maintenance_routine_line', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_minor_expenses', 'access_zue_minor_expenses', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_outsourcing_services_detail', 'access_zue_outsourcing_services_detail', 'ir.model.access'),
        ('zue_customizations_sole.access_zue_task_suggestion', 'access_zue_task_suggestion', 'ir.model.access'),
        ('zue_customizations_sole.view_form_stock_picking_type', 'view_form_stock_picking_type', 'ir.ui.view'),
        ('zue_customizations_sole.view_project_task_quotations_inherit', 'view_project_task_quotations_inherit', 'ir.ui.view'),
        ('zue_customizations_sole.view_stock_warehouse', 'view_stock_warehouse', 'ir.ui.view'),
        ('zue_customizations_sole.view_zue_project_task_inherit', 'view_zue_project_task_inherit', 'ir.ui.view'),
        ('zue_customizations_sole.view_zue_project_task_workorder_expenses_inherit', 'view_zue_project_task_workorder_expenses_inherit', 'ir.ui.view'),
        ('zue_customizations_sole.zue_custom_sale_order_inherit', 'zue_custom_sale_order_inherit', 'ir.ui.view'),
        ('zue_customizations_sole.zue_external_service_attributes', 'zue_external_service_attributes', 'ir.ui.view'),
        ('zue_customizations_sole.zue_hide_price_catalog_kanban', 'zue_hide_price_catalog_kanban', 'ir.ui.view'),
        ('zue_customizations_sole.zue_project_res_config_settings_view_form_analytic_account', 'zue_project_res_config_settings_view_form_analytic_account', 'ir.ui.view'),
        ('zue_customizations_sole.zue_project_task_inherit_variables', 'zue_project_task_inherit_variables', 'ir.ui.view'),
    ),
}


def preserve_split_xmlids(env, module):
    data = env['ir.model.data']
    aliases = data.browse()
    for previous, name, model in SPLIT_XMLIDS.get(module, ()):
        old_module, old_name = previous.split('.', 1)
        old = data.search([('module', '=', old_module), ('name', '=', old_name)], limit=1)
        if not old:
            continue
        if old.model != model:
            raise UserError('El identificador %s no corresponde al modelo %s; revise su migración.' % (previous, model))
        if not env[model].browse(old.res_id).exists():
            continue
        target = data.search([('module', '=', module), ('name', '=', name)], limit=1)
        if target and (target.model != model or target.res_id != old.res_id):
            raise UserError('Los identificadores %s y %s.%s apuntan a registros distintos; concílielos antes de actualizar.'
                            % (previous, module, name))
        if not target:
            target = data.create({'module': module, 'name': name, 'model': model, 'res_id': old.res_id, 'noupdate': old.noupdate})
        aliases |= target
    return aliases
