from odoo.tools.sql import column_exists


# El respaldo de identificación anterior deja de existir; antes de que Odoo elimine la columna se verifica que el valor siga en alguna versión del empleado.
def migrate(cr, version):
    if not column_exists(cr, 'hr_employee', 'z_legacy_identification_id'):
        return
    cr.execute("""
        SELECT e.id FROM hr_employee e
         WHERE NULLIF(e.z_legacy_identification_id, '') IS NOT NULL
           AND NOT EXISTS (SELECT 1 FROM hr_version v WHERE v.employee_id = e.id AND v.identification_id = e.z_legacy_identification_id)
         ORDER BY e.id LIMIT 20
    """)
    missing = [row[0] for row in cr.fetchall()]
    if missing:
        raise RuntimeError('Identificaciones: empleados cuya identificación anterior no está en ninguna de sus versiones; revisar antes de actualizar. IDs: %s' % missing)
