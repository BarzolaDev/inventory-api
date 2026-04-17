# 📦 Inventory Management API

A robust REST API for inventory management built with **FastAPI** and **PostgreSQL**.

## 🚀 Live Demo

API deployed on Render:  
[https://inventory-api-jpwh.onrender.com/docs](https://inventory-api-jpwh.onrender.com/docs)

**Key Features:**

  * Product registration and signed stock movements with full audit trails.
  * User management with **JWT Authentication**.
  * **Clean Architecture:** Decoupled logic across specialized layers.
  * **Frontend:** A lightweight dashboard built with HTML, Tailwind CSS, and Vanilla JavaScript consuming the API.

-----

## 🧰 Tech Stack

| Technology | Purpose |
|------------|-----|
| **FastAPI** | High-performance Web Framework |
| **SQLAlchemy** | SQL Toolkit & ORM |
| **PostgreSQL** | Relational Database |
| **Pydantic** | Data Validation & Settings Management |
| **Argon2** | Secure Password Hashing |
| **JWT** | Stateless Authentication |
| **Alembic** | Database Migrations |
| **Docker** | Containerization |

-----

## 🏗️ Architecture

The project follows a **Layered Architecture** pattern to ensure separation of concerns:

```text
api/
├── routes/    → Handles HTTP requests, delegates to services, manages HTTP errors.
├── services/  → Core Business Logic; raises Domain Exceptions.
├── models/    → SQLAlchemy ORM Models.
├── schemas/   → Data validation (Input/Output) via Pydantic.
├── core/      → Security (JWT, Hashing) and global dependencies (get_current_user).
├── db/        → Database engine, session management, and get_db dependency.
├── utils/     → Reusable helpers (e.g., commit_and_refresh).
└── tests/     → Service-level and Integration (HTTP) tests.
```

-----

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

-----

## ▶️ Getting Started

### 🐳 Using Docker

```bash
docker compose up --build
```

### 💻 Local Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Unix/MacOS
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
alembic upgrade head
uvicorn api.main:app --reload
```

*Interactive docs available at `http://localhost:8000/docs`*

-----

## 🔌 API Endpoints

### Auth & Users

| Method | Endpoint | Description |
|--------|------|-------------|
| POST | `/users/register` | User registration |
| POST | `/users/login` | Login - returns Bearer Token |

### Inventory

| Method | Endpoint | Auth | Description |
|--------|------|------|-------------|
| GET | `/products/` | No | List products (Supports pagination: `skip`, `limit`) |
| GET | `/products/{id}` | No | Retrieve product details |
| POST | `/products/` | Yes | Create new product |
| PATCH | `/products/{id}` | Yes | Update product |
| DELETE | `/products/{id}` | Yes | Delete product |
| POST | `/products/{id}/stock` | Yes | Update stock level |
| GET | `/products/{id}/movements` | Yes | Stock movement history |

> **Note:** Stock movements use signed integers (**positive = restock**, **negative = sale/withdrawal**).

-----

## 🧪 Testing

```bash
pytest api/tests/
```

**Coverage levels:**

1.  **Service Tests:** Direct business logic validation, covering happy paths and edge cases.
2.  **Integration Tests:** Using `TestClient` to verify HTTP status codes, schemas, and Auth middleware.

*Tests run against an isolated **SQLite in-memory database** per function.*

-----

## 🔍 Engineering Decisions & Trade-offs

  * **Concurrency Control:** Implemented **`SELECT FOR UPDATE`** on stock mutations to prevent race conditions during concurrent writes.
  * **Domain-Driven Validation:** Stock levels are strictly validated in the Service Layer to ensure they never drop below zero before persistence.
  * **Layered Exception Handling:** Custom typed exceptions (`ProductNotFoundError`, `InsufficientStockError`) are raised in the Service Layer. Routes catch these and map them to appropriate HTTP status codes, keeping the business logic agnostic of the web layer.
  * **Advanced Hashing:** Chose **Argon2** over BCrypt. As the winner of the Password Hashing Competition, it provides superior resistance to GPU/ASIC attacks through memory-hard functions.
  * **SOLID Principles & DI:** Utilized FastAPI's `Depends()` for **Dependency Injection** (`get_db`, `get_current_user`). This decouples routes from resource instantiation, aligning with the Dependency Inversion Principle.
  * **Database Migrations:** Integrated **Alembic** to provide versioned, reproducible schema changes, moving away from manual database updates.
  * **DRY Database Helpers:** Extracted the `add → commit → refresh` pattern with automated rollbacks into a `db_utils` helper to ensure session consistency across services.
  * **Infrastructure as Code:** Used **Docker** to standardize the development environment, eliminating "it works on my machine" issues.
  * **Testing Strategy:** Prioritized high-impact logic coverage. While currently using SQLite for speed, I acknowledge its lack of support for `SELECT FOR UPDATE`, meaning concurrency logic is validated via PostgreSQL integration in production.
  * **Security Trade-offs:** For this MVP, JWTs are stored in `localStorage` and lack a server-side revocation list (Redis). Production iterations would implement `httpOnly` cookies and Refresh Tokens.

-----

