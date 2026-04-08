## 🚀 Inventory API

**Backend orientado a consistencia bajo concurrencia**

Sistema de gestión de inventario diseñado para abordar un problema común en backend:

👉 la consistencia de datos bajo operaciones concurrentes

No es un CRUD tradicional.
El sistema está pensado para evitar estados inválidos (como stock negativo) incluso cuando múltiples requests operan al mismo tiempo.

---

## 🧠 Problemas que aborda

* Race conditions al actualizar stock
* Estados inválidos (ej: stock negativo)
* Inconsistencia en operaciones concurrentes
* Lógica de negocio acoplada al framework

---

## 🔥 Features

* Autenticación con JWT
* Gestión de productos
* Sistema de movimientos de stock
* Validaciones de negocio
* Testing de lógica crítica
* Manejo de errores con rollback
* Registro de movimientos de stock con consistencia en operaciones concurrentes

---

## ⚔️ Decisiones técnicas

* Uso de `SELECT FOR UPDATE` para evitar condiciones de carrera
* Transacciones para garantizar atomicidad
* Separación de lógica de negocio en `services/`
* Uso de excepciones de dominio

---

## 🧵 Concurrencia y consistencia

Cuando múltiples requests modifican el mismo recurso:

* Lock a nivel base de datos (`SELECT FOR UPDATE`)
* Transacciones con commit / rollback
* Registro consistente de movimientos de stock
* Validaciones para mantener integridad

---

## ⚠️ Manejo de errores

* Validaciones explícitas (ej: stock insuficiente)
* Excepciones de dominio
* Respuestas HTTP coherentes
* Rollback automático ante fallos
