# Pattern: Insert After Anchor

> En archivos Markdown largos, insertar contenido nuevo después de un anchor estable en lugar de reescribir bloques completos.

## When to use

- Cuando el archivo tiene headings o anchors mecánicos (`### @AGENTE - Rol`, `<!-- sync_start -->`, etc.)
- Cuando necesitas agregar una regla puntual a un documento de gobernanza
- Cuando quieres reducir el riesgo de truncado en archivos largos
- Cuando el archivo no debe ser append-only puro, pero sí necesita cambios locales y seguros

## Steps

1. **Elegir un anchor estable** — usar un heading o comentario único y persistente.
2. **Verificar unicidad** — confirmar que el anchor aparece una sola vez antes de editar.
3. **Insertar después del anchor** — agregar solo el bloque nuevo, preservando el contenido anterior y posterior.
4. **Limitar el diff** — revisar que solo cambiaron el anchor adyacente y el bloque insertado.
5. **Releer el archivo completo** — confirmar que no se truncaron secciones, tablas o entradas históricas.

## Anti-pattern

- Reemplazar un archivo completo para agregar una sola regla
- Usar `replace` sobre bloques amplios cuando existe un heading estable
- Mover o reordenar historial al insertar nuevo contenido
- Usar este patrón en logs append-only, donde corresponde agregar al final del archivo

## Verification

El diff conserva el contenido histórico intacto y solo agrega el bloque nuevo inmediatamente después del anchor esperado.
