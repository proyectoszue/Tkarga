from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists


def migrate(cr, version):
    if not column_exists(cr, 'hr_payslip_line', 'z_legacy_contract_type_id'):
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.flush_all()
    cr.execute("""
        SELECT l.id FROM hr_payslip_line l
          LEFT JOIN hr_version v ON v.id = l.version_id
         WHERE l.z_legacy_contract_type_id IS NOT NULL
           AND (v.id IS NULL OR v.contract_type IS NULL
                OR v.contract_type NOT IN ('obra', 'fijo', 'indefinido', 'aprendizaje', 'temporal')
                OR (NULLIF(l.contract_type, '') IS NOT NULL AND l.contract_type IS DISTINCT FROM v.contract_type))
         ORDER BY l.id LIMIT 20
    """)
    conflicts = cr.fetchall()
    if conflicts:
        raise RuntimeError('Nómina: la selección de contrato no coincide con la versión del recibo. Revisar líneas: %s' % conflicts)
    cr.execute("""
        UPDATE hr_payslip_line l SET contract_type = v.contract_type
          FROM hr_version v
         WHERE v.id = l.version_id AND l.z_legacy_contract_type_id IS NOT NULL
           AND NULLIF(l.contract_type, '') IS NULL
        RETURNING l.id
    """)
    lines = env['hr.payslip.line'].browse([row[0] for row in cr.fetchall()])
    lines.invalidate_recordset(['contract_type'])
    lines.modified(['contract_type'])
    env.flush_all()
    # El ID anterior era copia de hr_version.contract_type_id, que se conserva; no se deja la columna duplicada.
    cr.execute('ALTER TABLE hr_payslip_line DROP COLUMN z_legacy_contract_type_id')
