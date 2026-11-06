from odoo.tools.sql import table_columns

TABLE = 'product_template'
# Compañías donde el valor actual es válido cuando el producto es compartido (sin compañía).
VALID_COMPANIES = {
    'z_income_return_account': """
        SELECT rel.res_company_id FROM account_account_res_company_rel rel
         WHERE rel.account_account_id = (t.{col}->>'_value')::int""",
    'z_account_analytic_id': """
        SELECT c2.id FROM res_company c2
          JOIN account_analytic_account a ON a.id = (t.{col}->>'_value')::int
         WHERE a.company_id IS NULL OR a.company_id = c2.id""",
}


# Los campos pasan a company_dependent (jsonb {compañía: valor}); el ORM solo cambiaría el tipo y dejaría los valores sin compañía.
def migrate(cr, version):
    columns = table_columns(cr, TABLE)
    for col, companies in VALID_COMPANIES.items():
        udt = (columns.get(col) or {}).get('udt_name')
        if udt in ('int4', 'int8'):
            cr.execute("""
                SELECT con.conname FROM pg_constraint con
                  JOIN pg_attribute att ON att.attrelid = con.conrelid AND att.attnum = ANY(con.conkey)
                 WHERE con.conrelid = %s::regclass AND con.contype = 'f' AND att.attname = %s
            """, (TABLE, col))
            for (name,) in cr.fetchall():
                cr.execute(f'ALTER TABLE {TABLE} DROP CONSTRAINT "{name}"')
            cr.execute(f"ALTER TABLE {TABLE} ALTER COLUMN {col} TYPE jsonb USING CASE WHEN {col} IS NULL THEN NULL ELSE jsonb_build_object('_value', {col}) END")
        elif udt == 'jsonb':
            # Valores sueltos que pudo dejar una conversión previa hecha por el ORM.
            cr.execute(f"UPDATE {TABLE} SET {col} = jsonb_build_object('_value', ({col} #>> '{{}}')::int) WHERE jsonb_typeof({col}) = 'number'")
        else:
            continue
        condition = f"CASE WHEN t.company_id IS NOT NULL THEN c.id = t.company_id ELSE c.id IN ({companies.format(col=col)}) END"
        cr.execute(f"SELECT t.id FROM {TABLE} t WHERE t.{col} ? '_value' AND NOT EXISTS (SELECT 1 FROM res_company c WHERE {condition}) ORDER BY t.id LIMIT 20")
        orphans = [row[0] for row in cr.fetchall()]
        if orphans:
            raise RuntimeError(f'Contabilidad: productos con {col} sin compañía válida para conservar el valor; revisar antes de actualizar. IDs: {orphans}')
        cr.execute(f"""
            UPDATE {TABLE} t SET {col} = (SELECT jsonb_object_agg(c.id::text, t.{col}->'_value') FROM res_company c WHERE {condition})
             WHERE t.{col} ? '_value'
        """)
