# SECURITY (extracto ISO/IEC 27001:2022)

- No subir `.env` ni secretos a Git.
- Usar `N8N_ENCRYPTION_KEY` fuerte (>32 chars).
- En staging/prod: `N8N_SECURE_COOKIE=true` y TLS en reverse proxy.
- Backups diarios del volumen `n8n_data` y prueba de restauración trimestral.
- Acceso al host y Portainer con MFA; roles mínimos (least privilege).
