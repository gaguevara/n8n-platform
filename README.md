# n8n-platform (plantilla)

## Uso rápido
```bash
cp .env.example .env   # edita secretos
make -C ops run-local  # levantar en Docker Desktop
make -C ops build push TAG=dev-YYYYMMDDHHMM
make -C ops deploy-staging TAG=dev-YYYYMMDDHHMM
```

## Estructura
- `app/workflows/`  JSON exportados (sin secretos)
- `infra/`          Dockerfile + compose local/staging
- `ops/`            Makefile + scripts de despliegue
- `.vscode/`        Tareas para VS Code

## Backups
El volumen `n8n_data` contiene todo el estado. Respáldalo antes de cada despliegue.
