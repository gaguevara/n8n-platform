---
description: Reglas universales para Dockerfiles y docker-compose
paths: ["**/Dockerfile*", "**/docker-compose*.yml", "**/docker-compose*.yaml"]
---

# Docker Rules

- Procesos con usuario no-root.
- Multi-stage builds cuando la imagen final no necesita herramientas de build.
- No COPY de secretos, .env, credenciales ni API keys en ningún layer.
- Fijar versiones de imágenes base (no usar `latest` en producción).
- HEALTHCHECK definido en cada servicio.
- Resource limits (memory, cpu) en docker-compose para staging/prod.
- BD PostgreSQL no expuesta al host (solo accesible desde red interna Docker).
- Ejecutar `hadolint` sobre Dockerfiles modificados.
- En compose: usar networks nombradas, no la default.
- Volúmenes con nombre para persistencia, no bind mounts en producción.
