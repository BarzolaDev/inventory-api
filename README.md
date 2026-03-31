# 📦 Inventory Management API
### Backend Developer Portfolio | BarzolaDev

Este proyecto es una API robusta para la gestión de inventarios y movimientos de stock, diseñada con un enfoque en la integridad de datos y la escalabilidad.

## 🛠️ Arquitectura y Decisiones Técnicas

* **Separación de Responsabilidades:** Se utilizaron modelos de **SQLAlchemy** para la persistencia de datos y esquemas de **Pydantic** para la validación de entrada/salida, garantizando que los datos sensibles (como hashes de contraseñas) no sean expuestos en las respuestas de la API.

* **Gestión de Concurrencia:** Implementación de **bloqueos pesimistas** (`with_for_update`) en las transacciones de stock. Esto asegura la integridad de los datos en entornos multiusuario, evitando condiciones de carrera (*race conditions*) durante la actualización de existencias.

* **Infraestructura Modernizada:** Contenedorización completa mediante **Docker** y **Docker Compose**, facilitando un entorno de desarrollo consistente y un despliegue simplificado con **PostgreSQL**.

## 🚀 Tecnologías Utilizadas
* **Framework:** FastAPI (Python)
* **ORM:** SQLAlchemy
* **Validación:** Pydantic
* **Base de Datos:** PostgreSQL
* **DevOps:** Docker & Docker Compose