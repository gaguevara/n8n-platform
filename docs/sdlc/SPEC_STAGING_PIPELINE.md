# SPEC_STAGING_PIPELINE.md — Especificación de Pipeline Staging → Producción

## 1. Contexto y Objetivos

El objetivo de este pipeline es garantizar una transición segura de workflows de n8n desde el entorno de desarrollo local hasta la infraestructura de producción en AWS ECS Fargate, utilizando un entorno de Staging intermedio ejecutado en hardware on-premise (Dell R720).

## 2. Definición de Entornos

| Entorno    | Infraestructura        | Persistencia      | Objetivo                          |
|------------|------------------------|-------------------|-----------------------------------|
| **Local**  | Docker Desktop (Win11) | SQLite (Carpeta)  | Desarrollo rápido y exportación.  |
| **Staging**| Dell R720 (LAN)        | SQLite (Volumen)  | Pruebas de integración en red LAN. |
| **Prod**   | AWS ECS Fargate        | PostgreSQL (RDS) | Carga real y alta disponibilidad.  |

## 3. Flujo de Trabajo (Promoción de Cambios)

### Paso 1: Desarrollo Local
1. Desarrollar o modificar el workflow en la interfaz UI de n8n local (`localhost:5678`).
2. Exportar el workflow a la carpeta `app/workflows/` usando el script:
   ```bash
   make -C ops export
   ```
3. Commitear el archivo JSON generado.

### Paso 2: Validación en Staging (Dell R720)
1. Desplegar los cambios en el servidor Dell R720.
2. Importar los workflows al contenedor de staging:
   ```bash
   # En el servidor de staging
   ./scripts/import-workflows.sh n8n_staging
   ```
3. Validar funcionamiento, conectividad a servicios y triggers.

### Paso 3: Despliegue a Producción (AWS)
1. Una vez validado en Staging, el cambio se promociona a la rama `main`.
2. El proceso de CI/CD (o manual según `docs/AWS_DEPLOYMENT.md`):
   - Construye la imagen (vía `infra/Dockerfile` si hay cambios en base, o usa la oficial).
   - Sube la imagen a Amazon ECR.
   - Actualiza la **Task Definition** en ECS Fargate con la nueva configuración de variables.
   - n8n en producción consumirá los workflows (vía importación automatizada o volumen si aplica).

## 4. Consideraciones Técnicas

- **Cifrado:** La variable `N8N_ENCRYPTION_KEY` debe ser idéntica entre entornos si se desea importar workflows con credenciales guardadas (no recomendado por seguridad; se prefiere re-configurar credenciales en cada entorno o usar variables).
- **Base de Datos:** El cambio de SQLite a PostgreSQL en producción es transparente para la lógica de los workflows (JSON), pero requiere validación de tipos de datos complejos si los hay.
- **Red:** Staging opera en LAN, Prod en VPC AWS. Asegurar que las URLs de Webhooks (`WEBHOOK_URL`) estén correctamente configuradas por entorno.

## 5. Validación de Éxito

- Workflow importado correctamente en Staging sin errores de esquema.
- Pruebas de "Dry Run" exitosas en el entorno de Staging.
- Despliegue en AWS sin caídas del servicio (ECS Rolling Update).
