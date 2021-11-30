# -*- coding: utf-8 -*-
{
    'name': "zue_fleet_maintenance",

    'summary': """
        Folders for maintenance. """,

    'description': """
        Folders for maintenance. 
    """,

    'author': "ZUE S.A.S",
    
    'category': 'ZueMaintenance',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','account','zue_erp','stock','zue_stock','product','purchase','hr','hr_payroll'],

    # always loaded
    'data': [
        'views/actions_symptoms.xml',
        'views/actions_detection.xml',
        'views/actions_technician.xml',
        'views/actions_services_type.xml',
        'views/actions_component.xml',
        'views/actions_causes.xml',
        'views/actions_catalog.xml',
        'views/actions_routines.xml',
        'views/actions_documents_types.xml',
        'views/actions_fleet_vehicle.xml',
        'views/actions_io_view.xml',
        'views/actions_request_view.xml',
        'views/actions_workorder_view.xml',
        'views/actions_task_view.xml',        
        'views/fleet_vehicle_odometer_view.xml', 
        'views/actions_vehiculos_linea.xml',
        'views/actions_inventarios.xml',
        'views/program_wizard_view.xml',
        'views/actions_payroll.xml',
        'views/security_branch.xml',
        'report/custom_report_layout.xml',
        'report/workorder_report_template.xml',
        'report/workorder_report.xml',
        'report/mntc_input_output_report_template.xml',
        'report/mntc_input_output_report.xml',
        'views/report_mntc_workorder_rh.xml',
        'views/wizards/confirm_wizard.xml',
        'views/report_mntc_workorder_task.xml',
        'views/report_mntc_workorder_rrhh.xml',
        'views/availability_indicator_wizard.xml',
        'views/availability_indicator_report_document.xml',
        'views/availability_indicator_report_document_template.xml',
        'views/actions_indicators_maintenance.xml',
        'views/fleet_vehicle_spare_parts_indicator.xml',
        'views/menus.xml',
        # 'data/mntc_detection_methods_data.xml',
        'security/ir.model.access.csv',        
        # 'data/mntc_workforce_data.xml',
        ## 'data/mntc_vehicle_system_data.xml',
        #'data/mntc_action_taken_data.xml',
        ## 'data/mntc_component_data.xml',
        ## 'data/mntc_spare_part_type_data.xml',
        # 'data/mntc_services_type_data.xml',
        # 'data/mntc_causes_data.xml', 
        # 'data/mntc_documents_type_data.xml',
    ]
}
