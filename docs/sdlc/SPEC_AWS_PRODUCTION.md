# SPEC: Despliegue en AWS ECS Fargate para n8n

## 1. Objetivo
Definir los requisitos de infraestructura, arquitectura y configuración necesarios para desplegar n8n en producción sobre AWS ECS Fargate, garantizando alta disponibilidad, seguridad de secretos y persistencia de datos adecuada.

## 2. Arquitectura General
El despliegue en producción consistirá en:
- **Compute:** AWS ECS Fargate (Serverless compute para contenedores).
- **Base de Datos:** AWS RDS PostgreSQL (Para la base de datos interna de n8n y de Threat Intelligence).
- **Almacenamiento (Opcional/Recomendado para binarios):** AWS EFS (Elastic File System) montado en la tarea ECS para persistencia de archivos compartidos (si los workflows requieren procesamiento de archivos en disco), aunque se prefiere mantener el diseño *stateless* y almacenar binarios en la BD (PostgreSQL) o S3.
- **Redes:** VPC con subredes públicas (para el ALB) y subredes privadas (para ECS y RDS).
- **Exposición:** Application Load Balancer (ALB) manejando terminación SSL y redirigiendo tráfico al contenedor ECS.
- **Gestión de Imágenes:** AWS ECR (Elastic Container Registry) para almacenar la imagen de n8n.
- **Seguridad:** AWS Secrets Manager para inyección segura de contraseñas y claves.
- **Observabilidad:** Amazon CloudWatch para logs y métricas.

## 3. Best Practices para n8n en ECS Fargate

### 3.1. Networking y Exposición
- **ALB (Application Load Balancer):** Actúa como punto de entrada público, realiza la terminación TLS/SSL (mediante AWS Certificate Manager) y reenvía tráfico por HTTP (puerto 5678) a las tareas de Fargate en subredes privadas.
- **Security Groups:** 
  - **ALB SG:** Permite inbound 443/80 desde Internet.
  - **ECS SG:** Permite inbound 5678 SOLO desde el ALB SG. Egress libre para alcanzar APIs de terceros (Threat Intel, etc.).
  - **RDS SG:** Permite inbound 5432 SOLO desde el ECS SG.

### 3.2. Persistencia y Almacenamiento (Storage)
- **Base de Datos:** Configurar n8n para usar PostgreSQL (`DB_TYPE=postgresdb`, `DB_POSTGRESDB_HOST`, etc.). La base de datos guarda ejecuciones y credenciales de flujos de trabajo cifradas.
- **Archivos/Volúmenes (EFS vs Bind):** Por defecto, n8n requiere almacenamiento local para algunos datos temporales (ej. subida de archivos). Se recomienda usar **EFS** adjunto a la Task Definition si se requiere compartir estado entre réplicas (por ejemplo en modo Queue) o para `/home/node/.n8n`. Para un despliegue simple sin modo Queue, el almacenamiento efímero nativo de Fargate (volumen `bind` efímero) es suficiente si TODA la persistencia está en RDS y S3.

### 3.3. Inyección de Secretos (Secrets Management)
Las variables críticas NO deben configurarse en texto plano en la Task Definition. Se deben usar referencias `valueFrom` en `secrets` apuntando a **AWS Secrets Manager** o **SSM Parameter Store** (con cifrado KMS). La Execution Role de la tarea de ECS necesita permisos `secretsmanager:GetSecretValue` y `ssm:GetParameters`.

### 3.4. Logging
- **CloudWatch:** Configurar el `logConfiguration` de la Task Definition utilizando el driver `awslogs`.
- **Destino:** Crear un Log Group específico (ej. `/ecs/n8n-prod`).

## 4. Mapeo de Variables y Mecanismos de Inyección

La siguiente tabla define cómo se debe inyectar cada variable definida en el `.env.example` en la Task Definition de ECS.

| Variable | Tipo de Dato | Mecanismo de Inyección en ECS | Razón / Permisos Requeridos |
|----------|--------------|-------------------------------|-----------------------------|
| `TZ` | Configuración | Texto Plano (`environment`) | No sensible. |
| `GENERIC_TIMEZONE` | Configuración | Texto Plano (`environment`) | No sensible. |
| `N8N_PORT` | Configuración | Texto Plano (`environment`) | Puerto interno del contenedor (ej. 5678). |
| `N8N_ENCRYPTION_KEY` | Crítico | **AWS Secrets Manager** (`secrets`) | Clave maestra para cifrar credenciales en n8n. |
| `N8N_EDITOR_BASE_URL` | Configuración | Texto Plano (`environment`) | URL pública, no sensible. |
| `WEBHOOK_URL` | Configuración | Texto Plano (`environment`) | URL pública, no sensible. |
| `RDS_HOST` | Infraestructura | Texto Plano (`environment`) / SSM (Opcional) | Endpoint interno de la VPC. |
| `RDS_USER` | Infraestructura | Texto Plano (`environment`) | Usuario de DB. |
| `RDS_PASSWORD` | Crítico | **AWS Secrets Manager** (`secrets`) | Contraseña de la base de datos principal de n8n. |
| `THREAT_DB_USER` | Infraestructura | Texto Plano (`environment`) | Usuario DB de Threat Intel. |
| `THREAT_DB_PASSWORD` | Crítico | **AWS Secrets Manager** (`secrets`) | Contraseña DB de Threat Intel. |
| `THREAT_DB_HOST_PORT` | Configuración | Texto Plano (`environment`) | Puerto DB Threat Intel. |
| `REDIS_PASSWORD` | Crítico | **AWS Secrets Manager** (`secrets`) | Contraseña de caché. |
| `REDIS_HOST_PORT` | Configuración | Texto Plano (`environment`) | Puerto Redis. |
| `FORTIGATE_HOST`, `WAZUH_API_URL`, `ZABBIX_API_URL` | Infraestructura | Texto Plano (`environment`) | URLs de servicios de origen. |
| `WAZUH_API_USER` | Infraestructura | Texto Plano (`environment`) | Usuario API no crítico. |
| `FORTIGATE_API_KEY`, `WAZUH_API_PASSWORD`, `ZABBIX_API_TOKEN` | Sensible | **SSM Parameter Store (SecureString)** | Credenciales de integración, rotación moderada. |
| `ABUSEIPDB_API_KEY`, `OTX_API_KEY`, `VIRUSTOTAL_API_KEY` | Sensible | **SSM Parameter Store (SecureString)** | Tokens de APIs externas. |
| `SLACK_WEBHOOK_URL`, `TEAMS_WEBHOOK_URL` | Sensible | **SSM Parameter Store (SecureString)** | Webhooks con capacidad de escritura. |
| `ALERT_EMAIL_TO`, `ALERT_EMAIL_FROM` | Configuración | Texto Plano (`environment`) | Correos de alerta, no sensibles. |

*Nota sobre AWS Variables (`AWS_ACCOUNT_ID`, `AWS_REGION`, `TAG`, `ECR_REGISTRY`):* Estas variables son para el pipeline de CI/CD (Makefile) y no necesitan ser inyectadas directamente en el contenedor de n8n, a menos que n8n use un nodo nativo de AWS que requiera el SDK. Si es así, se recomienda proveer acceso mediante la **Task Role** de IAM de ECS, no mediante variables de entorno.

## 6. Análisis de Brechas (docker-compose.prod.yml vs Task Definition)

Al revisar `infra/docker-compose.prod.yml`, se detectan los siguientes gaps que deben ser resueltos en el despliegue real de ECS:

1. **Gestión de Secretos:** El compose utiliza interpolación de variables `${VAR}`, mientras que ECS debe usar `secrets` con `valueFrom` (ARNs de Secrets Manager/SSM) para evitar que los secretos residan en la definición de la tarea en texto plano.
2. **Fuentes de Threat Intel:** El compose de producción no incluye las variables para FortiGate, Wazuh, Zabbix y OSINT mapeadas en la Sección 4. Estas deben agregarse a la Task Definition.
3. **Servicios Adicionales:** El pipeline requiere `threat-cache` (Redis) y acceso a una segunda DB (`threat_intel`). En AWS, esto se traduce en:
    - Redis: Instancia AWS ElastiCache o contenedor sidecar en el cluster.
    - DB: La instancia RDS debe albergar ambas bases de datos (`n8n` y `threat_intel`).
4. **Plantilla de Referencia:** Se ha generado una plantilla JSON completa en `docs/architecture/ECS_TASK_DEFINITION_TEMPLATE.json` que resuelve estos gaps.

## 7. Resumen de Creación de Recursos
... (resto del contenido)