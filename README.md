# Inventory Management API

Production-ready REST API for inventory management built with FastAPI.  
Designed to ensure data consistency under concurrent operations, with automated testing and CI/CD integration.

---

## 🌍 Live Demo

Interactive API documentation:  
[https://inventory-api-jpwh.onrender.com/docs](https://inventory-api-jpwh.onrender.com/docs)

---

## 🧠 Overview

This project focuses on building a reliable backend system with:

- Data consistency under concurrent operations
- Clear separation of concerns via layered architecture
- Automated testing and CI to ensure reliability

The goal is to simulate real-world backend constraints beyond basic CRUD APIs.

---

## ✨ Key Features

- Product registration and signed stock movements with full audit trails
- User management with JWT Authentication
- Concurrency-safe stock operations (`SELECT FOR UPDATE`)
- Clean Architecture with clear separation of responsibilities
- Fully dockerized environment
- Automated testing (unit + integration)
- CI pipeline with GitHub Actions

---

## 🧰 Tech Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | High-performance Web Framework |
| SQLAlchemy | ORM & DB Toolkit |
| PostgreSQL | Relational Database |
| Pydantic | Validation & Settings |
| Argon2 | Password Hashing |
| JWT | Authentication |
| Alembic | Migrations |
| Docker | Containerization |

---

## 🏗 Architecture

```text
api/
├── routes/    → Handles HTTP requests, delegates to services, maps HTTP errors
├── services/  → Core business logic; raises domain exceptions
├── models/    → SQLAlchemy ORM models
├── schemas/   → Input/output validation via Pydantic
├── core/      → Security (JWT, hashing) and global dependencies
├── db/        → Engine, session management, and get_db dependency
├── utils/     → Reusable helpers (e.g., commit_and_refresh)
└── tests/     → Service-level and integration (HTTP) tests
```

Layered architecture ensures separation between HTTP, business logic, and persistence layers.

---

## ⚙️ Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🚀 Getting Started

```bash
docker compose up --build
```

Application will be available at: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### Auth & Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/register` | User registration |
| POST | `/users/login` | Login — returns Bearer Token |

### Inventory

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/products/` | No | List products (pagination: `skip`, `limit`) |
| GET | `/products/{id}` | No | Get product |
| POST | `/products/` | Yes | Create product |
| PATCH | `/products/{id}` | Yes | Update product |
| DELETE | `/products/{id}` | Yes | Delete product |
| POST | `/products/{id}/stock` | Yes | Update stock level |
| GET | `/products/{id}/movements` | Yes | Stock movement history |

> Stock movements use signed integers — **positive = restock**, **negative = sale/withdrawal**.

---

## 🧪 Testing

```bash
pytest api/tests/
```

- **Service tests:** Direct business logic validation, covering happy paths and edge cases
- **Integration tests:** Using `TestClient` to verify HTTP status codes, schemas, and auth middleware

Tests run automatically on every push via GitHub Actions.

---

## 🧠 Engineering Decisions & Trade-offs

- **Concurrency control with `SELECT FOR UPDATE`:** Stock mutation queries lock the row before reading, preventing race conditions during concurrent writes. This ensures stock levels stay consistent under simultaneous requests.

- **Domain validation in the service layer:** Stock levels are validated before persistence, ensuring they never drop below zero. The service layer raises typed exceptions (`InsufficientStockError`, `ProductNotFoundError`) that routes catch and map to appropriate HTTP status codes — keeping business logic agnostic of the web layer.

- **Argon2 over BCrypt for password hashing:** As the winner of the Password Hashing Competition, Argon2 provides superior resistance to GPU/ASIC attacks through memory-hard functions. BCrypt would have worked, but Argon2 is the current best practice.

- **Dependency Injection via FastAPI `Depends()`:** Used for `get_db` and `get_current_user`, decoupling routes from resource instantiation. This aligns with the Dependency Inversion Principle and makes unit testing significantly easier.

- **Alembic for database migrations:** Provides versioned, reproducible schema changes instead of manual `CREATE TABLE` scripts. This is essential for any project that evolves over time or runs across multiple environments.

- **Pydantic `BaseSettings` over `load_dotenv`:** Environment variables are type-safe and validated at startup. `database.py` consumes `settings.DATABASE_URL` directly, centralizing configuration and eliminating manual `os.getenv()` calls scattered across the codebase.

- **SQLite in tests, PostgreSQL in production:** SQLite keeps the test suite fast and dependency-free (no DB server needed in CI). The trade-off is that `SELECT FOR UPDATE` isn't supported in SQLite, so concurrency logic is validated against PostgreSQL in production rather than in automated tests.

- **Docker for environment standardization:** Eliminates environment-specific bugs and makes the project runnable with a single command regardless of the host OS.

- **Auto-increment IDs over UUIDs:** Chosen for simplicity and query performance. UUIDs would be preferable in distributed systems or scenarios requiring non-guessable public identifiers.

---

## ⚠️ Known Limitations & Future Improvements

- **JWT stored in `localStorage`:** Vulnerable to XSS. A production iteration would use `httpOnly` cookies and implement Refresh Tokens with a server-side revocation list (Redis).
- **No rate limiting:** Should be added before any public-facing deployment.
- **No `SELECT FOR UPDATE` coverage in tests:** Due to SQLite limitations in CI. Future improvement would spin up a PostgreSQL container in the test environment.