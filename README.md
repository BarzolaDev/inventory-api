# Inventory API

REST API de gestión de inventario construida con FastAPI y PostgreSQL. Permite registrar productos, controlar stock con movimientos auditados y gestionar usuarios con autenticación JWT.

## Stack

- **FastAPI** — framework web
- **SQLAlchemy** — ORM
- **PostgreSQL** — base de datos
- **Pydantic** — validación de datos
- **Argon2** — hashing de contraseñas
- **JWT** — autenticación

## Arquitectura

El proyecto aplica separación de responsabilidades en capas:

routes/     → recibe HTTP, delega a services, maneja errores HTTP
services/   → lógica de negocio, lanza excepciones de dominio
models/     → modelos ORM
schemas/    → validación de entrada/salida con Pydantic

DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

```bash
python -m venv .venv
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
uvicorn api.main:app --reload
```

Documentación interactiva disponible en `http://localhost:8000/docs`

## Endpoints

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

Los movimientos de stock usan cantidad con signo: positivo = ingreso, negativo = retiro.

## Tests

```bash
pytest api/tests/
```

Los tests corren contra una base de datos SQLite en memoria, aislada por función.

## Decisiones técnicas

- **`SELECT FOR UPDATE`** en mutaciones de stock para prevenir race conditions bajo escrituras concurrentes
- **Excepciones de dominio tipadas** (`ProductNotFoundError`, `InsufficientStockError`) en la capa de servicios — las rutas las mapean a códigos HTTP
- **Argon2** para hashing de contraseñas en lugar de bcrypt, por ser el ganador de Password Hashing Competition