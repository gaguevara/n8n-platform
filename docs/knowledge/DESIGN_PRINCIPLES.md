# DESIGN_PRINCIPLES.md — Base de Conocimiento: Principios de Diseño

> **Propósito:** Referencia obligatoria para todo agente que genere, revise o refactorice código.
> Los agentes deben aplicar estos principios sin que el humano los recuerde en cada prompt.

---

## 1. SOLID (Robert C. Martin)

| Principio | Regla | Violación típica en código generado por IA |
|-----------|-------|---------------------------------------------|
| **S** — Single Responsibility | Una clase/módulo hace una cosa. Si necesitas usar "y" para describir su propósito, son dos cosas. | Clases "God object" que mezclan lógica de negocio, acceso a datos y presentación. |
| **O** — Open/Closed | Abierto a extensión, cerrado a modificación. Extiende comportamiento sin editar código existente. | Modificar un switch/case cada vez que se agrega un caso nuevo en vez de usar polimorfismo o strategy. |
| **L** — Liskov Substitution | Un subtipo debe poder reemplazar a su tipo base sin romper el comportamiento esperado. | Override de métodos que cambian las precondiciones o postcondiciones del padre. |
| **I** — Interface Segregation | Interfaces pequeñas y específicas. Ningún cliente debe depender de métodos que no usa. | Interfaces "fat" con 15 métodos donde cada implementación deja 10 vacíos o con `NotImplementedError`. |
| **D** — Dependency Inversion | Depender de abstracciones, no de implementaciones concretas. | Instanciar dependencias con `new` dentro de la clase en vez de inyectarlas. |

---

## 2. Clean Code (Robert C. Martin)

### Reglas que todo agente debe aplicar por defecto

- **Nombres significativos.** Variables, funciones y clases deben revelar su intención. `d` no es aceptable; `elapsed_time_in_days` sí.
- **Funciones pequeñas.** Una función hace una cosa. Si tiene más de 20 líneas, probablemente hace demasiado.
- **Un nivel de abstracción por función.** No mezclar lógica de alto nivel con detalles de implementación.
- **Comentarios solo cuando el código no puede expresar la intención.** El mejor comentario es el que no necesitas porque el nombre es claro.
- **Sin código muerto.** No dejar funciones, imports o variables sin usar.
- **DRY (Don't Repeat Yourself).** Si copias y pegas, necesitas una abstracción.
- **Boy Scout Rule.** Deja el código más limpio de lo que lo encontraste.
- **Error handling explícito.** No capturar excepciones genéricas. Capturar excepciones específicas con contexto.

---

## 3. Clean Architecture (Robert C. Martin)

### Regla de dependencia

```
Frameworks → Interface Adapters → Use Cases → Entities
     ↑               ↑                ↑           ↑
  outer            middle          inner       innermost

La dependencia SIEMPRE apunta hacia adentro.
Nunca un Use Case importa un Framework.
Nunca una Entity conoce la base de datos.
```

### Capas

| Capa | Contiene | Ejemplo |
|------|----------|---------|
| **Entities** | Reglas de negocio enterprise, independientes de la aplicación | Cálculo de impuesto, regla de descuento |
| **Use Cases** | Reglas de negocio de la aplicación (orquestación) | "Crear factura", "Aprobar orden de compra" |
| **Interface Adapters** | Conversión de datos entre capas | Controllers, Presenters, Gateways, ORM mappers |
| **Frameworks & Drivers** | Detalles de implementación | Base de datos, web framework, UI, dispositivos |

### Aplicación en agentes

Cuando un agente genera código, debe verificar que las dependencias fluyan hacia adentro. Si un módulo de negocio importa directamente `psycopg2`, `requests`, o un framework web, es una violación.

---

## 4. Design Patterns (GoF)

### Patrones que los agentes deben reconocer y aplicar

| Patrón | Cuándo usarlo | Anti-patrón equivalente |
|--------|--------------|------------------------|
| **Strategy** | Comportamiento intercambiable en runtime | Cascadas de if/elif/else o switch |
| **Factory** | Creación de objetos sin acoplar al tipo concreto | `new ConcreteClass()` disperso por el código |
| **Observer** | Notificación de cambios a múltiples consumidores | Polling o callbacks anidados |
| **Adapter** | Interfaz incompatible con el contrato esperado | Modificar la clase original para que "encaje" |
| **Repository** | Abstracción de acceso a datos | Queries SQL directos en la lógica de negocio |
| **Decorator** | Agregar comportamiento sin modificar la clase | Herencia profunda para agregar features |
| **Command** | Encapsular una acción como objeto (undo, queue, log) | Métodos enormes que hacen todo inline |

### Patrones que los agentes deben evitar (anti-patrones)

| Anti-patrón | Síntoma | Solución |
|-------------|---------|----------|
| **God Object** | Una clase con demasiadas responsabilidades | Separar por responsabilidad (SRP) |
| **Spaghetti Code** | Flujo de control imposible de seguir | Refactorizar en funciones pequeñas con un nivel de abstracción |
| **Premature Optimization** | Optimizar antes de medir | Hacer que funcione primero, luego medir, luego optimizar |
| **Magic Numbers/Strings** | Valores literales sin contexto | Constantes con nombre significativo |
| **Shotgun Surgery** | Un cambio requiere editar 10 archivos | Consolidar la lógica dispersa |
| **Copy-Paste Programming** | Duplicación de bloques de código | Extraer función o clase reutilizable |

---

## 5. Refactoring (Martin Fowler)

### Técnicas que todo agente debe dominar

| Técnica | Cuándo | Señal |
|---------|--------|-------|
| **Extract Method** | Bloque de código con comentario explicativo | "Este bloque hace X" → crear método `do_x()` |
| **Rename** | Nombre no revela intención | `tmp`, `data`, `result`, `info` |
| **Move Method** | Método usa más datos de otra clase que de la propia | Feature Envy |
| **Replace Temp with Query** | Variable temporal usada solo para cachear un cálculo simple | `total = price * qty; if total > 100` → `if calculate_total() > 100` |
| **Introduce Parameter Object** | Función con 4+ parámetros del mismo dominio | `def create_invoice(customer, date, items, currency, tax)` |
| **Replace Conditional with Polymorphism** | Switch/case que crece con cada tipo nuevo | Strategy o herencia |

### Regla para agentes

Antes de agregar código nuevo, verificar si el código existente necesita refactoring para acomodar el cambio limpiamente. Nunca agregar un hack "porque funciona" — documentar la deuda técnica si no hay tiempo para el refactoring.

---

## 6. Algoritmos y Estructuras de Datos

### Complejidad que todo agente debe evaluar

| Operación | Aceptable | Sospechoso | Inaceptable |
|-----------|-----------|-----------|-------------|
| Búsqueda en lista | O(n) si n < 1000 | O(n) si n > 10,000 | O(n²) siempre |
| Ordenamiento | O(n log n) | O(n²) para n > 100 | Bubble sort en producción |
| Búsqueda en dict/map | O(1) amortizado | — | Iterar dict para buscar por valor |
| Query DB | Con índice | Full table scan < 10K rows | Full table scan > 100K rows sin índice |

### Regla

Todo agente debe evaluar la complejidad algorítmica de las soluciones que genera. Si genera un loop anidado sobre una colección que puede crecer, debe señalarlo explícitamente y proponer alternativa.

---

## 7. Security by Design

| Principio | Aplicación |
|-----------|-----------|
| **Least Privilege** | Permisos mínimos necesarios. No dar admin cuando basta read. |
| **Defense in Depth** | Múltiples capas de validación. No confiar solo en frontend. |
| **Fail Secure** | Si algo falla, el estado resultante debe ser seguro (no abierto). |
| **Input Validation** | Todo input externo es hostil hasta probarse lo contrario. |
| **No Secrets in Code** | Credenciales, tokens, API keys en variables de entorno o secret manager. |
| **Audit Trail** | Toda acción relevante genera un log auditable. |

---

## Fuentes de referencia

| Libro | Autor | Relevancia |
|-------|-------|-----------|
| Design Patterns | Gamma, Helm, Johnson, Vlissides (GoF) | Patrones clásicos |
| Head First Design Patterns | Freeman & Robson | Patrones con ejemplos prácticos |
| Refactoring | Martin Fowler | Técnicas de mejora continua del código |
| Clean Architecture | Robert C. Martin | Arquitectura por capas de dependencia |
| Clean Code | Robert C. Martin | Código legible y mantenible |
| Introduction to Algorithms | Cormen, Leiserson, Rivest, Stein (CLRS) | Complejidad y estructuras de datos |

---

*Este archivo es parte del knowledge base del framework multi-agente. Todo agente debe tener acceso a estos principios y aplicarlos por defecto.*
