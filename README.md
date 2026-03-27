# 📦 Inventory Management API

Una REST API profesional desarrollada con **FastAPI** y **PostgreSQL**, enfocada en la integridad de datos, el manejo de alta concurrencia y la escalabilidad.

---

## 🚀 Características Principales

* **Arquitectura de Capas (Service Layer):** Separación clara entre los puntos de entrada (Routes) y la lógica de negocio (Services) para un código mantenible y testeable.
* **Control de Concurrencia (Pessimistic Locking):** Implementación de `with_for_update()` en operaciones críticas de stock, evitando condiciones de carrera (*race conditions*) cuando múltiples usuarios interactúan simultáneamente.
* **Integridad con Transacciones ACID:** Gestión de errores mediante bloques `try/except/rollback`, asegurando que la base de datos nunca quede en un estado inconsistente ante fallos inesperados.
* **Paginación Eficiente:** Consultas optimizadas con `limit` y `offset` para manejar grandes volúmenes de datos sin comprometer el rendimiento de la aplicación.
* **Seguridad y Tipado:** Uso exhaustivo de **Pydantic** para validación de esquemas y **SQLAlchemy** con tipado de sesiones para un desarrollo robusto y con autocompletado.
* **Trazabilidad:** Sistema de **Logging** profesional configurado para monitorear errores y eventos críticos en tiempo real.

---

## 🛠️ Tecnologías utilizadas

* **Framework:** FastAPI
* **Base de Datos:** PostgreSQL
* **ORM:** SQLAlchemy (v2.0 style)
* **Validación:** Pydantic v2
* **Entorno:** Python 3.10+

---

## 📝 Próximos pasos

- [ ] Implementar **Autenticación JWT** (OAuth2).
- [ ] Relación de usuarios con productos (Owner-based access).
- [ ] Containerización con **Docker** y **Docker Compose**.