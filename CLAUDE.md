# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Instrucciones generales
- Responde siempre en español
- No toques services/ salvo que yo lo pida explicitamente

## Project Overview

Inventory management REST API built with FastAPI + SQLAlchemy (PostgreSQL). Supports user registration/login with JWT auth and product stock management with audited movements.

## Environment Setup

Requires a `.env` file at the project root with:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Activate the virtual environment before running any commands:

```bash
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Unix
```

## Commands

```bash
# Run the development server
uvicorn api.main:app --reload

# Run all tests
pytest api/tests/

# Run a single test file
pytest api/tests/test_product.py

# Run a single test by name
pytest api/tests/test_product.py::test_create_product
```

## Architecture

```
api/
  main.py           # FastAPI app, router registration, table creation on startup
  core/
    security.py     # JWT creation/verification, argon2 password hashing
    depends.py      # get_current_user dependency (OAuth2 Bearer → User model)
  db/
    database.py     # SQLAlchemy engine, SessionLocal, Base, get_db dependency
  models/           # SQLAlchemy ORM models (User, Product, StockMovement)
  schemas/          # Pydantic request/response schemas
  services/         # Business logic layer — raises domain exceptions
  routes/           # FastAPI routers — catch domain exceptions, return HTTP errors
  utils/
    db_utils.py     # commit_and_refresh helper
  tests/
    conftest.py     # In-memory SQLite test DB, function-scoped `db` fixture
    test_product.py # Service-layer tests (bypass HTTP, call services directly)
```

### Key patterns

**Auth flow:** `POST /users/login` accepts `OAuth2PasswordRequestForm` (email in the `username` field). Returns a Bearer token. Protected routes use `Depends(get_current_user)` from `core/depends.py`.

**Stock mutation:** `POST /products/{id}/stock` accepts a `MovementCreate` with a signed `quantity` (positive = restock, negative = withdrawal). `services/product.py::update_stock` uses `SELECT ... FOR UPDATE` to prevent race conditions and records a `StockMovement` row on every change.

**Domain exceptions:** Services raise typed exceptions (`ProductNotFoundError`, `InsufficientStockError`, `UserAlreadyExistsError`, `InvalidCredentialsError`). Routes catch these and map them to HTTP status codes. Never catch bare `Exception` in services.

**Test isolation:** Tests hit service functions directly with a real (SQLite in-memory) DB. The `db` fixture drops all tables after each test.

