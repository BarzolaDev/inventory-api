# 📦 Inventory API

REST API de gestión de inventario construida con FastAPI y PostgreSQL.

## 🚀 Demo

API deployada en Render:  
https://inventory-api-jpwh.onrender.com/docs

Permite registrar productos, controlar stock con movimientos auditados y gestionar usuarios con autenticación JWT.

![Swagger UI](docs/swagger.png)

---

## 🧰 Stack

| Tecnología | Uso |
|------------|-----|
| **FastAPI** | Framework web |
| **SQLAlchemy** | ORM |
| **PostgreSQL** | Base de datos |
| **Pydantic** | Validación de datos |
| **Argon2** | Hashing de contraseñas |
| **JWT** | Autenticación |

---

## 🏗️ Arquitectura

Separación en capas:

```
routes/     → recibe HTTP, delega a services, maneja errores HTTP
services/   → lógica de negocio, lanza excepciones de dominio
models/     → modelos ORM
schemas/    → validación de entrada/salida con Pydantic
```

---

## ⚙️ Variables de entorno

Creá un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ▶️ Cómo correr el proyecto

### 🐳 Con Docker

```bash
docker compose up --build
```

### 💻 Local

```bash
python -m venv .venv
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
uvicorn api.main:app --reload
```

Documentación interactiva disponible en `http://localhost:8000/docs`

---

## 🔌 Endpoints

### Usuarios

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/users/register` | Registro de usuario |
| POST | `/users/login` | Login — devuelve Bearer token |

### Productos

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/products/` | No | Listar productos |
| GET | `/products/{id}` | No | Obtener producto |
| POST | `/products/` | Sí | Crear producto |
| PATCH | `/products/{id}` | Sí | Actualizar producto |
| DELETE | `/products/{id}` | Sí | Eliminar producto |
| POST | `/products/{id}/stock` | Sí | Actualizar stock |
| GET | `/products/{id}/movements` | Sí | Historial de movimientos |

> Los movimientos de stock usan cantidad con signo: **positivo = ingreso**, **negativo = retiro**.

---

## 🧪 Tests

```bash
pytest api/tests/
```

Los tests apuntan directamente a la capa de servicios sin pasar por HTTP, cubriendo happy paths y edge cases de producto, usuario y autenticación. Corren contra una base de datos SQLite en memoria, aislada por función.

---

## 🔍 Decisiones técnicas

- **`SELECT FOR UPDATE`** en mutaciones de stock para prevenir race conditions bajo escrituras concurrentes
- **Stock no puede ser negativo** — el servicio valida que el resultado de cada movimiento sea `>= 0` antes de persistir
- **`sale_price` debe ser mayor que `purchase_price`** — validado en el schema al crear y en el servicio al actualizar
- **Excepciones de dominio tipadas** (`ProductNotFoundError`, `InsufficientStockError`) en la capa de servicios — las rutas las mapean a códigos HTTP
- **Argon2** para hashing de contraseñas en lugar de bcrypt, por ser el ganador de Password Hashing Competition
