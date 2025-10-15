## Resumen
- Cambios en infra/workflows
- Sin secretos ni .env en el diff

## Pruebas
- `docker compose ... up` OK
- Healthcheck 200, logs sin errores

## Riesgos / rollback
- Tag anterior para revertir: