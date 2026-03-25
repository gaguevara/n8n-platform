# SPEC_TEMPLATE.md — Plantilla de Especificación por Feature

> **Propósito:** Toda feature, módulo o cambio significativo inicia con una spec.
> El agente lee la spec antes de escribir código. Basado en Spec-Driven Development (GitHub Spec Kit).
>
> **Flujo:** Intent → Spec → Plan Review → Implementación → Validación

---

## Instrucciones de uso

1. Copiar este archivo a `docs/sdlc/SPEC_[NOMBRE].md`
2. Completar todas las secciones marcadas con `[COMPLETAR]`
3. Revisar la spec con el equipo antes de iniciar implementación
4. El agente ejecutor lee la spec completa antes de escribir una línea de código
5. El agente validador verifica el resultado contra los criterios de aceptación

---

## Spec: [NOMBRE DE LA FEATURE]

### Metadata

| Campo | Valor |
|-------|-------|
| ID | SPEC-[NNN] |
| Fecha | [YYYY-MM-DD] |
| Autor | [Nombre] |
| Fase del proyecto | [1/2/3/4] |
| Empresa(s) afectada(s) | [COMPLETAR — si aplica multi-empresa] |
| ADR relacionado | [ADR-NNN o "Ninguno"] |
| Riesgo asociado | [RISK-NNN o "Ninguno"] |
| Estado | [Draft / En revisión / Aprobada / En implementación / Completada] |

---

### 1. Objetivo

[COMPLETAR — Qué se quiere lograr. Una frase clara. No cómo, sino qué.]

---

### 2. Contexto y motivación

[COMPLETAR — Por qué se necesita. Qué problema resuelve. Qué pasa si no se hace.]

---

### 3. Alcance

**Dentro del alcance:**
- [COMPLETAR]

**Fuera del alcance:**
- [COMPLETAR]

---

### 4. Requisitos funcionales

| ID | Requisito | Prioridad |
|----|----------|-----------|
| RF-01 | [COMPLETAR] | Alta / Media / Baja |
| RF-02 | [COMPLETAR] | Alta / Media / Baja |

---

### 5. Requisitos no funcionales

| ID | Requisito | Métrica |
|----|----------|---------|
| RNF-01 | Performance: [COMPLETAR] | [ej: respuesta < 2s] |
| RNF-02 | Seguridad: [COMPLETAR] | [ej: sin secrets hardcodeados] |
| RNF-03 | Mantenibilidad: [COMPLETAR] | [ej: cobertura tests > 80%] |

---

### 6. Inputs y Outputs

**Inputs:**
- [COMPLETAR — datos, archivos, APIs, configuraciones que la feature recibe]

**Outputs:**
- [COMPLETAR — datos, archivos, APIs, UI, reportes que la feature produce]

---

### 7. Restricciones técnicas

- [COMPLETAR — limitaciones de stack, dependencias, compatibilidad, normativa]

---

### 8. Criterios de aceptación

| ID | Criterio | Verificación |
|----|----------|-------------|
| CA-01 | [COMPLETAR] | [cómo se verifica: test, demo, review] |
| CA-02 | [COMPLETAR] | |
| CA-03 | [COMPLETAR] | |

---

### 9. Plan de implementación (alto nivel)

| Paso | Descripción | Agente responsable | Archivos afectados |
|------|-------------|-------------------|-------------------|
| 1 | [COMPLETAR] | [Claude / Codex / Gemini / Humano] | [rutas] |
| 2 | [COMPLETAR] | | |
| 3 | [COMPLETAR] | | |

---

### 10. Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| [COMPLETAR] | [B/M/A] | [B/M/A/C] | [COMPLETAR] |

---

### 11. Definition of Done

- [ ] Todos los criterios de aceptación verificados
- [ ] Tests unitarios escritos y pasando
- [ ] Linter/formatter sin errores
- [ ] Code review completado (agente revisor)
- [ ] Documentación actualizada (CONTEXT.md, README si aplica)
- [ ] Log del agente registrado
- [ ] RISK_REGISTER actualizado si se detectaron riesgos
- [ ] Spec marcada como "Completada"

---

*Plantilla basada en Spec-Driven Development (GitHub Spec Kit) adaptada al framework multi-agente.*

---

### 12. Verification Criteria

> **Formato ISC (Ideal State Criteria):** Cada criterio es una afirmacion booleana
> de 8-12 palabras que describe el estado ideal del sistema tras la implementacion.
> El metodo de verificacion indica como se comprueba:
>
> - **test** — un test automatizado (unitario o integracion) lo valida.
> - **inspection** — revision manual de codigo, configuracion o datos.
> - **demo** — demostracion funcional en la interfaz de usuario.
>
> Minimo 3 criterios por spec. Maximo ~12 para features complejas.

| # | Criterion | Method | Pass? |
|---|-----------|--------|-------|
| VC-01 | [COMPLETAR — afirmacion booleana de 8-12 palabras] | [test / inspection / demo] | |
| VC-02 | [COMPLETAR] | | |
| VC-03 | [COMPLETAR] | | |

**Ejemplo:**

```
| # | Criterion | Method | Pass? |
|---|---|---|---|
| VC-01 | Invoice total includes IVA 16% tax correctly | test | |
| VC-02 | Multi-company isolation prevents cross-company access | test | |
| VC-03 | User sees withholding line in payment form | demo | |
```

> **Nota:** Todo criterio debe ser verificable. Si no se puede escribir un test o
> demo para comprobarlo, el criterio es demasiado vago.

---

### 13. Task Breakdown (generado por /plan)

> Esta sección se completa usando el comando `/plan` después de que la spec sea aprobada.

| Task ID | Descripción | Archivos | Patrón | Test | Riesgo | Dependencia | Estado |
|---------|-------------|----------|--------|------|--------|-------------|--------|
| TASK-001 | [COMPLETAR] | [rutas] | [patrón o N/A] | [test file] | [B/M/A] | [TASK-NNN o ninguna] | [ ] |
| TASK-002 | [COMPLETAR] | | | | | | [ ] |
| TASK-003 | [COMPLETAR] | | | | | | [ ] |

---

### 14. Harness Review (post-implementación)

| Pregunta | Respuesta |
|----------|-----------|
| ¿Se detectaron harness gaps durante la implementación? | [Sí/No — describir] |
| ¿Qué se agregó al harness para prevenir recurrencia? | [doc/tool/spec/constraint o N/A] |
| ¿El framework necesita actualización por esta feature? | [Sí/No] |

