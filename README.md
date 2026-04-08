# 🚀 Inventory API  
### Backend que no se rompe cuando las cosas se ponen reales

Sistema de gestión de inventario diseñado para algo que muchos ignoran:

👉 **la consistencia de datos bajo concurrencia**

No es un CRUD.  
Es un sistema que asegura que el stock nunca entra en estados inválidos, incluso bajo múltiples operaciones simultáneas.

---

## 🌐 Live Demo

👉 https://inventory-api-jpwh.onrender.com/docs  

Explorá los endpoints directamente desde Swagger y probá el flujo completo con autenticación.

---

## ⚡ ¿Por qué este proyecto no es “uno más”?

La mayoría de APIs de inventario:

- actualizan stock directamente  
- no manejan concurrencia  
- confían en inputs  
- rompen bajo presión  

👉 **Este proyecto no.**

---

## 🧠 Problemas reales que resuelve

- ❌ Race conditions al actualizar stock  
- ❌ Estados inválidos (stock negativo)  
- ❌ Inconsistencia en operaciones concurrentes  
- ❌ Lógica de negocio acoplada al framework  

✔️ Solucionados con decisiones concretas de diseño

---

## 🔥 Features clave

- 🔐 Autenticación con JWT  
- 📦 Gestión de productos  
- 🔄 Sistema de movimientos de stock  
- ⚠️ Validaciones de negocio estrictas  
- 🔒 Protección de endpoints  
- 🧪 Testing sobre lógica crítica  
- 🧠 Manejo de errores + rollback automático  

---

## ⚔️ Decisiones técnicas (lo importante de verdad)

Este proyecto no se trata de “usar tecnologías”, sino de **cómo usarlas**:

- Se utiliza `SELECT FOR UPDATE` para bloquear filas y evitar condiciones de carrera  
- Se implementan transacciones para garantizar atomicidad  
- La lógica de negocio vive en `services/`, no en los endpoints  
- Se usan excepciones de dominio para desacoplar reglas del framework  

👉 Esto permite escalar el sistema sin convertirlo en un caos.

---

## 🧵 Concurrencia y consistencia

Cuando múltiples requests intentan modificar el mismo recurso:

- 🔒 Lock a nivel base de datos (`SELECT FOR UPDATE`)  
- 🔁 Transacciones con commit / rollback  
- ⚖️ Consistencia garantizada  

👉 El sistema prioriza integridad por sobre velocidad ingenua.

---

## ⚠️ Manejo de errores

No hay errores “silenciosos”:

- validaciones explícitas (ej: stock insuficiente)  
- excepciones de dominio claras  
- traducción a respuestas HTTP coherentes  
- rollback automático ante fallos  

---

## 🔑 Autenticación

Sistema basado en JWT:

```bash
Authorization: Bearer <token>