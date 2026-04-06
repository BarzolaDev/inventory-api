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

---

## ▶️ Correr el proyecto

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





