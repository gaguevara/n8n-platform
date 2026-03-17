# CONTEXT_SECURITY.md — Inventario de Secretos y Variables Sensibles

> **Generado por:** Claude (Governor — cross-review + security audit)
> **Fecha:** 2026-03-17
> **Referencia:** PROJECT_RULES.md §8 (Escalation), CODEX_LOG ENTRADA-002, GEMINI_LOG ENTRADA-001

---

## 1. Clasificación de variables

### 🔴 CRÍTICAS — Nunca commitear, rotar ante exposición

| Variable             | Descripción                           | Entorno       | Dónde se usa                        |
|----------------------|---------------------------------------|---------------|-------------------------------------|
| `N8N_ENCRYPTION_KEY` | Clave de cifrado de credenciales n8n  | Todos         | `.env`, docker-compose              |
| `RDS_PASSWORD`       | Password PostgreSQL en AWS RDS        | Producción    | `.env`, ECS task definition         |
| `N8N_BASIC_AUTH_PASSWORD` | Password básica de acceso UI   | Staging/Prod  | `.env` si se habilita basic auth    |

**Rotación:** Si `N8N_ENCRYPTION_KEY` se rota, todas las credenciales almacenadas en n8n quedan inválidas — requiere re-autenticación de cada nodo.

---

### 🟡 SENSIBLES — Controlar acceso, no exponer en logs

| Variable               | Descripción                           | Entorno       | Dónde se usa             |
|------------------------|---------------------------------------|---------------|--------------------------|
| `RDS_HOST`             | Endpoint RDS (expone topología AWS)   | Producción    | `.env`, ECS              |
| `RDS_USER`             | Usuario de BD                         | Producción    | `.env`, ECS              |
| `AWS_ACCOUNT_ID`       | ID de cuenta AWS                      | Producción    | Makefile, scripts ECR    |
| `WEBHOOK_URL`          | URL pública de webhooks               | Staging/Prod  | `.env`, docker-compose   |
| `N8N_EDITOR_BASE_URL`  | URL del editor (expone host interno)  | Staging       | `.env`, docker-compose   |
| `ECR_REGISTRY`         | Registro de imagen Docker             | Producción    | Makefile, CI/CD          |

---

### 🟢 CONFIGURACIÓN — Sin riesgo de exposición directa

| Variable            | Descripción              | Default               |
|---------------------|--------------------------|-----------------------|
| `TZ`                | Zona horaria             | `America/Bogota`      |
| `GENERIC_TIMEZONE`  | Zona horaria n8n         | `America/Bogota`      |
| `N8N_PORT`          | Puerto local             | `5678`                |
| `AWS_REGION`        | Región AWS               | `us-east-1`           |
| `TAG`               | Tag de imagen Docker     | `latest`              |

---

## 2. Mecanismos de protección activos

| Mecanismo              | Estado   | Evidencia                              |
|------------------------|----------|----------------------------------------|
| `.env` en `.gitignore` | ✅ Activo | Confirmado por Codex ENTRADA-001       |
| `detect-secrets` hook  | ✅ Activo | `.secrets.baseline` creado por Codex   |
| `.env.example` sin valores reales | ✅ | Verificado — solo placeholders |
| Secretos en ECS Task Definition | ⚠️ | No auditado — fuera del repo  |

---

## 3. Riesgos residuales identificados

| Riesgo                                               | Severidad | Recomendación                                  |
|------------------------------------------------------|-----------|------------------------------------------------|
| `N8N_ENCRYPTION_KEY` hardcodeada en ECS si no usa Secrets Manager | 🔴 Alto | Migrar a AWS Secrets Manager o SSM Parameter Store |
| `RDS_PASSWORD` en variables planas de ECS Task Definition | 🔴 Alto | Usar AWS Secrets Manager reference en ECS     |
| Imagen `latest` en producción (`TAG=latest`)         | 🟡 Medio  | Usar tags fijos con SHA o versión semántica    |
| `detect-secrets` v1.4.0 fijado — puede desalinearse  | 🟡 Medio  | Documentar proceso de actualización coordinada |
| Scripts shell dependen de Git Bash/WSL en Windows    | 🟡 Medio  | Documentado en ONBOARDING.md (Gemini)         |

---

## 4. Checklist de auditoría periódica

- [ ] Verificar que `.env` no está trackeado: `git ls-files .env`
- [ ] Ejecutar `python -m pre_commit run detect-secrets --all-files`
- [ ] Rotar `N8N_ENCRYPTION_KEY` si hubo acceso no autorizado al repo
- [ ] Auditar ECS Task Definition en AWS Console — confirmar uso de Secrets Manager
- [ ] Revisar que `TAG=latest` no llega a producción sin override

---

> **Próxima revisión:** al agregar una nueva integración o variable de entorno
> **Escalar a:** Claude (Governor) ante cualquier exposición sospechosa
