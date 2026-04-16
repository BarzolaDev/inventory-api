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
| **Alembic** | Migraciones de base de datos |
| **Docker** | Contenedorización |

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
alembic upgrade head
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
| GET | `/products/` | No | Listar productos (soporta paginación con `skip` y `limit`) |
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

Dos niveles de cobertura:
- **Tests de servicio** — llaman directo a la lógica de negocio, cubren happy paths y edge cases
- **Tests HTTP** — usan `TestClient` para verificar status codes, response schemas y autenticación en los endpoints

Corren contra una base de datos SQLite en memoria, aislada por función.

---

## 🗄️ Migraciones

```bash
# Aplicar migraciones pendientes
alembic upgrade head

# Generar migración después de cambiar un modelo
alembic revision --autogenerate -m "descripcion del cambio"
```

---

## 🔍 Decisiones técnicas

- **`SELECT FOR UPDATE`** en mutaciones de stock para prevenir race conditions bajo escrituras concurrentes
- **Stock no puede ser negativo** — el servicio valida que el resultado de cada movimiento sea `>= 0` antes de persistir
- **`sale_price` debe ser mayor que `purchase_price`** — validado en el schema al crear y en el servicio al actualizar
- **Excepciones de dominio tipadas** (`ProductNotFoundError`, `InsufficientStockError`) en la capa de servicios — el servicio no sabe nada de HTTP, solo señala qué falló en la lógica de negocio; la ruta atrapa la excepción y decide el código HTTP correspondiente sin mezclar responsabilidades
- **Argon2** para hashing de contraseñas en lugar de bcrypt, por ser el ganador de Password Hashing Competition
- **`GET /products/` y `GET /products/{id}` son públicos** — se decidió que la consulta de productos no requiere autenticación para permitir que cualquier visitante vea el catálogo sin registrarse; las operaciones de escritura (crear, editar, eliminar, mover stock) sí requieren token
- **Pytest incorporado para cubrir happy paths, edge cases y el flujo completo routes → services → db** — al ser la primera API REST se priorizó tener cobertura de los casos críticos; en el próximo proyecto se arranca directamente con TDD
- **Separación en capas routes/services** — el código arrancó con toda la lógica en las rutas; al necesitar inyectar `get_current_user` como dependencia en las rutas protegidas se hizo evidente la necesidad de separar la lógica de negocio en servicios independientes para mantener las rutas limpias y testeables
- **Alembic para migraciones** — inicialmente los cambios de esquema se aplicaban a mano via DBeaver; se incorporó Alembic para versionar y reproducir los cambios de la DB de forma controlada y sin intervención manual
- **Docker para estandarizar el entorno** — elimina el "en mi máquina funciona"; cualquiera puede levantar la app con `docker compose up --build` sin instalar PostgreSQL ni configurar variables manualmente
- **Inyección de dependencias con `Depends()`** — `get_db` y `get_current_user` se inyectan en las rutas en vez de instanciarse adentro de cada una; las rutas no saben cómo se crea la sesión ni cómo se verifica el token, lo que se alinea con el principio DIP de SOLID
- **Herencia de schemas `Base → Create → Response`** — se aplicó el patrón estándar de Pydantic para evitar duplicación de campos y facilitar la extensión si el proyecto escala; cada schema agrega solo lo que le corresponde
- **`utils/db_utils.py` con `commit_and_refresh`** — el patrón `add → commit → refresh` con rollback en caso de error se repetía en múltiples servicios; se extrajo a un helper aplicando DRY para evitar inconsistencias de sesión por copy-paste
- **JWT sin refresh token ni revocación server-side** — el token expira según `ACCESS_TOKEN_EXPIRE_MINUTES`; el logout es client-side (se elimina de `localStorage`). No hay blacklist ni mecanismo de invalidación anticipada. En producción se implementaría refresh token y revocación via Redis o tabla de tokens invalidados
- **SQLite en tests en lugar de PostgreSQL** — los tests corren contra una base de datos SQLite en memoria por velocidad y simplicidad de setup; la limitación es que SQLite no soporta `SELECT FOR UPDATE`, por lo que esa lógica de concurrencia no se testea a nivel unitario sino que se confía en la integración con PostgreSQL en producción
- **JWT guardado en `localStorage`** en el frontend por simplicidad durante desarrollo — en producción se usaría una `httpOnly cookie` para prevenir XSS
