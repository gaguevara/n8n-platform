# SECURITY - ISO/IEC 27001:2022

## Control de Acceso (A.9)

- [ ] `N8N_ENCRYPTION_KEY` generada con `openssl rand -hex 32` (mínimo 256 bits)
- [ ] Key almacenada en AWS Secrets Manager (prod) o vault seguro
- [ ] Acceso SSH a staging/prod solo con llaves, no passwords
- [ ] MFA habilitado en AWS Console y Portainer
- [ ] Principio de mínimo privilegio en IAM roles

## Protección de Datos (A.8)

- [ ] `.env` excluido de Git (verificar .gitignore)
- [ ] Credenciales encriptadas en reposo (n8n usa AES-256-GCM)
- [ ] Backups encriptados en S3 con SSE-KMS
- [ ] No logs de datos sensibles (revisar workflows)

## Seguridad en Red (A.13)

- [ ] HTTPS obligatorio en producción (ALB/CloudFront)
- [ ] `N8N_SECURE_COOKIE=true` en staging/prod
- [ ] Security Groups restrictivos (solo puertos necesarios)
- [ ] VPC con subnets privadas para ECS tasks

## Gestión de Vulnerabilidades (A.12)

- [ ] Imagen base actualizada regularmente
- [ ] Escaneo de vulnerabilidades en ECR habilitado
- [ ] Dependencias auditadas (npm audit)
- [ ] Parches aplicados en ventana de mantenimiento

## Continuidad (A.17)

- [ ] Backups diarios automatizados
- [ ] Retención: 7 días diarios, 4 semanas semanales, 12 meses mensuales
- [ ] Prueba de restauración trimestral documentada
- [ ] RTO objetivo: 4 horas
- [ ] RPO objetivo: 24 horas

## Registro y Monitoreo (A.12.4)

- [ ] Logs centralizados en CloudWatch
- [ ] Alertas configuradas para:
  - Container unhealthy
  - Error rate > 5%
  - CPU/Memory > 80%
- [ ] Retención de logs: 90 días

## Checklist Pre-Deployment

### Staging
- [ ] Variables de entorno configuradas
- [ ] Healthcheck respondiendo
- [ ] Workflows críticos probados
- [ ] Backup pre-deploy realizado

### Producción
- [ ] Aprobación de cambio registrada
- [ ] Staging validado
- [ ] Rollback plan documentado
- [ ] Ventana de mantenimiento comunicada

## Incidentes

Ante incidente de seguridad:
1. Contener: Aislar recurso afectado
2. Notificar: IT Manager + Compliance
3. Investigar: Logs, accesos, cambios recientes
4. Remediar: Aplicar fix, rotar credenciales si necesario
5. Documentar: Causa raíz y lecciones aprendidas
