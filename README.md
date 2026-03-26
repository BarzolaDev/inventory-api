# 📦 Inventory Management API (FastAPI + PostgreSQL)

API robusta desarrollada con **FastAPI** para la gestión de inventarios en tiempo real. Este proyecto destaca por su arquitectura modular y lógica de negocio orientada a la trazabilidad de stock.

## 🚀 Características Principales

- **Arquitectura Modular:** Separación clara de responsabilidades (Models, Schemas, Routes, Database).
- **Lógica de Stock Acumulativa:** Los movimientos de stock no solo reemplazan valores, sino que se registran de forma incremental en un historial de movimientos.
- **Validaciones de Integridad:** Control de stock negativo.
  - Prevención de duplicados por nombre de producto.
  - Manejo de errores HTTP con su respectivo Detalle.
    
- **Persistencia:** Integración con PostgreSQL mediante SQLAlchemy.

## 🛠️ Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy)
- **Validación de Datos:** Pydantic
- **Entorno:** Python Dotenv (Seguridad de credenciales)

## 📡 Endpoints
- POST /products → Crear nuevo producto -> {"name": "mouse", "stock": 32}
- GET /products → Obtenemos -> Obtenemos todos los productos de la db
- PATCH /products/{id} → Actualiza el stock dependiendo si se vendio o se obtuvieron mas productos  
- GET /products/{id}/movements → Obtenemos todos los movimientos del Producto.
