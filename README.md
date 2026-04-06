# 🚀 Inventory API – FastAPI + PostgreSQL

API backend para gestión de inventario con control de stock, concurrencia y lógica de negocio consistente.

Diseñada con foco en claridad, mantenibilidad y escenarios reales de producción.

---

## 📦 Overview

Este proyecto implementa un sistema de gestión de inventario que permite:

- Crear y administrar productos
- Registrar movimientos de stock
- Mantener consistencia de datos
- Evitar estados inválidos (ej: stock negativo)

La arquitectura está pensada para escalar y adaptarse a entornos reales.

---

## 🚀 Features

- 🔐 Autenticación con JWT (OAuth2 Password Flow)
- 📦 Gestión de productos y stock
- 🔄 Registro de movimientos de inventario
- ⚠️ Validación de reglas de negocio (stock no negativo)
- 🔒 Protección de endpoints con usuario autenticado
- 🧪 Testing de lógica de negocio con pytest
- 🧠 Manejo de errores y rollback en transacciones

---

## ⚡ Concurrencia y consistencia

- Uso de `SELECT FOR UPDATE` para evitar condiciones de carrera
- Manejo de transacciones con commit / rollback
- Garantía de consistencia en operaciones críticas de stock

---

## ⚠️ Manejo de errores

- Validaciones de negocio (ej: stock insuficiente)
- Uso de excepciones controladas (`ValueError`)
- Traducción a respuestas HTTP adecuadas
- Rollback automático en caso de error


## ▶️ Correr el proyecto

### 🔑 Endpoints y Autenticación

El sistema cuenta con protección de rutas mediante **JWT (JSON Web Tokens)**:

* **Públicos:** * `GET /products`: Permite visualizar el stock disponible sin necesidad de estar autenticado.
* **Privados:** * Todos los demás endpoints (POST, PUT, DELETE y gestión de movimientos) requieren registro e inicio de sesión.
    
**Cómo usar la autorización:**
Para probar los endpoints protegidos, debés incluir el token en el header de la siguiente forma:
`Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpX...`


### 1. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

## 2. Instalar las dependencias 

pip install -r requirements.txt

## 3. Ejercutar servidor

uvicorn api.main:app --reload

## 🧠 Arquitectura

El proyecto sigue una estructura por capas:
api/

```bash
api/
├── routes/     → endpoints HTTP
├── services/   → lógica de negocio
├── models/     → ORM (SQLAlchemy)
├── schemas/    → validación (Pydantic)
├── tests/      → testing (Pytest)
├── core/       → config y dependencias
```

### 🔹 Principios aplicados

- Separación de responsabilidades  
- Lógica desacoplada de la capa HTTP  
- Código orientado a mantenibilidad  
- Diseño basado en casos reales  

---

## ⚙️ Stack tecnológico

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Pytest

---

## 🧪 Testing

El proyecto incluye tests sobre la lógica de negocio utilizando `pytest`.

### Cobertura actual:

- ✅ Creación de productos  
- ✅ Actualización de stock  
- ❗ Validación de errores (edge cases)  
- ❗ Prevención de stock negativo  

Ejecutar tests:

```bash
pytest
```





