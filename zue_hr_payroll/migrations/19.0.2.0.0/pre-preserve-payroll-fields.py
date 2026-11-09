from odoo.tools.sql import rename_column, table_columns


def migrate(cr, version):
    columns = table_columns(cr, 'hr_payslip_line')
    contract_type = columns.get('contract_type')
    if contract_type and contract_type['udt_name'] in ('int2', 'int4', 'int8'):
        if 'z_legacy_contract_type_id' in columns:
            raise RuntimeError('Nómina: existen contract_type entero y su respaldo. Revisar ambas columnas antes de actualizar; no se sobrescriben.')
        cr.execute("""
            SELECT l.id FROM hr_payslip_line l
              LEFT JOIN hr_version v ON v.id = l.version_id
              LEFT JOIN hr_contract_type t ON t.id = l.contract_type
             WHERE l.contract_type IS NOT NULL
               AND (t.id IS NULL OR v.id IS NULL OR v.contract_type IS NULL
                    OR v.contract_type NOT IN ('obra', 'fijo', 'indefinido', 'aprendizaje', 'temporal'))
             ORDER BY l.id LIMIT 20
        """)
        conflicts = cr.fetchall()
        if conflicts:
            raise RuntimeError('Nómina: líneas sin tipo de contrato o versión válida para conservar ambos tipos. Revisar IDs: %s' % conflicts)
        # La nueva selección se obtiene de la versión; el ID previo conserva su columna y su relación.
        rename_column(cr, 'hr_payslip_line', 'contract_type', 'z_legacy_contract_type_id')
    elif contract_type and contract_type['udt_name'] in ('varchar', 'text'):
        cr.execute("""
            SELECT l.id FROM hr_payslip_line l
              LEFT JOIN hr_version v ON v.id = l.version_id
             WHERE NULLIF(l.contract_type, '') IS NOT NULL
               AND (l.contract_type NOT IN ('obra', 'fijo', 'indefinido', 'aprendizaje', 'temporal')
                    OR l.contract_type IS DISTINCT FROM v.contract_type)
             ORDER BY l.id LIMIT 20
        """)
        conflicts = cr.fetchall()
        if conflicts:
            raise RuntimeError('Nómina: selección de contrato inválida o distinta de la versión; no se sobrescriben líneas. Revisar IDs: %s' % conflicts)
    elif contract_type:
        raise RuntimeError('Nómina: tipo SQL inesperado en hr_payslip_line.contract_type; revisar antes de actualizar.')
