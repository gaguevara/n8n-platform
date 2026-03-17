# ONBOARDING.md — Guía de Incorporación al Proyecto

## 1. Propósito

Permitir que un desarrollador o agente nuevo entienda el proyecto y pueda colaborar de forma efectiva, tanto en la gobernanza multi-agente como en el desarrollo técnico de n8n.

---

## 2. Setup Técnico (Desarrollo Local)

### Requisitos previos
- **Sistema Operativo:** Windows 11 con Docker Desktop instalado.
- **Herramientas:** Git, Make (vía `choco install make` o similar).
- **Entorno:** Git Bash o PowerShell Core.

### Pasos iniciales
1. **Configurar entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con valores locales si es necesario
   ```
2. **Levantar n8n local:**
   ```bash
   make -C ops dev
   ```
3. **Acceso:** Abrir `http://localhost:5678` en el navegador.

### Estructura de Datos Local
- `./data`: Persistencia de SQLite (configuración y ejecuciones de n8n).
- `./shared-files`: Carpeta compartida con el contenedor para lectura/escritura de archivos desde n8n.

---

## 3. Flujo de Trabajo con Workflows

Todo cambio en los flujos debe versionarse en Git como JSON:

1. Modificar el flujo en la UI de n8n.
2. Ejecutar exportación local:
   ```bash
   make -C ops export
   ```
3. Commitear los cambios en `app/workflows/`.

---

## 4. Orden obligatorio de lectura (Gobernanza)

1. `docs/governance/PROJECT_RULES.md` — Reglas y estándares
2. `docs/governance/CONTEXT.md` — Estado actual del proyecto
3. `docs/governance/LOG_INDEX.md` — Índice de actividad reciente
4. Logs recientes de los otros agentes en `docs/logs/`
5. Overlay del agente correspondiente en `docs/agents/` (e.g., `GEMINI.md`)
6. Código fuente y configuración clave (`infra/`, `scripts/`)

---

## 5. Protocolo de Agentes

### Qué debe entender primero
- Objetivo actual del proyecto
- Arquitectura y stack (Local → Staging → Prod)
- Decisiones vigentes (ADRs)
- Bloqueos activos y riesgos residuales

### Qué no hacer al entrar
- No proponer refactorizaciones globales sin evidencia de necesidad.
- No repetir intentos fallidos ya registrados en los logs.
- No ignorar decisiones activas documentadas en `CONTEXT.md`.
- No asumir que documentación antigua sigue vigente — verificar fechas.
- No cerrar tareas sin registro y evidencia en el log correspondiente.

---

## 6. Checklist de Inicio

- [ ] Entendí el objetivo actual del proyecto
- [ ] Revisé decisiones activas en `CONTEXT.md`
- [ ] Instalé el entorno local y puedo ver la UI de n8n
- [ ] Leí el `LOG_INDEX.md` y los logs recientes relevantes
- [ ] Sé cómo exportar mis cambios de workflow a JSON
- [ ] Conozco las áreas críticas que requieren validación cruzada (Security/Prod)
