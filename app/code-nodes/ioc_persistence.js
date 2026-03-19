// ============================================================
// NODO: IoC Persistence Layer
// Tipo: Code Node (JavaScript) en n8n
// Input: items[] normalizados con _should_persist === true
// Output: SQL queries para ejecutar via nodo PostgreSQL
//
// NOTA: Este nodo genera los queries. El nodo PostgreSQL
// downstream los ejecuta. No se usa ORM.
// ============================================================

const persistItems = $input.all().filter(item => item.json._should_persist);

if (persistItems.length === 0) {
  return [{ json: { _skip: true, message: 'No items to persist' } }];
}

const output = [];

for (const item of persistItems) {
  const ioc = item.json;

  // 1. Upsert IoC via función PL/pgSQL
  output.push({
    json: {
      _operation: 'upsert_ioc',
      query: `SELECT upsert_ioc($1, $2::ioc_type, $3::severity_level, $4::SMALLINT, $5::TEXT[], $6::JSONB)`,
      params: [
        ioc.ioc_value,
        ioc.ioc_type,
        ioc.severity,
        ioc.confidence,
        ioc.tags || [],
        JSON.stringify(ioc.metadata || {})
      ],
      // Datos para el sighting (se ejecuta después del upsert)
      _sighting: {
        source: ioc.source,
        raw_event: ioc.metadata,
        observed_at: ioc.observed_at
      }
    }
  });
}

return output;
