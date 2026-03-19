---
name: cross-review
description: Ejecuta revisión cruzada de código siguiendo el Pattern 04. Usar cuando se completa un cambio significativo y se necesita validación por un agente diferente al autor.
---

# Cross Review

Sigue el Pattern 04 (cross-agent-review) de `.multiagent/core/patterns/`.

## Checklist de revisión

### Clean Code
- [ ] Nombres significativos
- [ ] Funciones ≤ 20 líneas
- [ ] Sin código muerto
- [ ] Sin duplicación
- [ ] Error handling específico

### Principios (SOLID / Clean Architecture)
- [ ] Single Responsibility
- [ ] Dependencias apuntan hacia adentro
- [ ] Sin God Objects

### Seguridad
- [ ] Sin credenciales hardcodeadas
- [ ] Sin SQL/ORM inseguro
- [ ] Inputs validados
- [ ] Permisos mínimos

### Tests
- [ ] Cubren happy path + edge cases
- [ ] Independientes entre sí

## Veredicto
- 🔴 REJECTED — tiene bloqueantes
- 🟡 APPROVED WITH COMMENTS — recomendaciones no bloqueantes
- 🟢 APPROVED — sin hallazgos

Registrar en log del agente revisor con archivos y veredicto específico.
