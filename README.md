# ⚙️ Inventory Management API

Production-oriented REST API built with FastAPI, focused on one thing:

👉 Keeping data consistent under concurrent operations.

Because real systems don't fail on CRUD — they fail under race conditions.

---

## 🌍 Live Demo

Interactive API documentation:  
https://inventory-api-jpwh.onrender.com/docs

---

## 🧠 Why this project exists

Most beginner APIs work fine… until real-world conditions hit:

- Multiple users modifying the same resource  
- Race conditions corrupting data  
- Business rules enforced inconsistently  

This project focuses on solving those problems.

This project intentionally goes beyond MVP scope — concurrency control, Redis-based token management, and real infrastructure testing — to understand how production systems handle these problems before encountering them at scale.

---

## 💥 Core Problem

How do you guarantee stock consistency when multiple requests hit the same product at the same time?

### Naive flow:

1. Read stock  
2. Modify value  
3. Save  

### Under concurrency:
User A reads stock = 1
User B reads stock = 1
Both write → stock = -1 ❌

---

## ✅ Solution

- Row-level locking using `SELECT FOR UPDATE` inside database transactions,  
  ensuring concurrent requests cannot read stale values before mutation  

- Atomic stock operations  

- Domain-level validation before persistence

- Rate limiting on all endpoints via middleware and nginx reverse proxy, preventing brute force and DoS attacks

👉 Result: **Stock remains consistent under concurrent requests**

---

## 🏗 Architecture
```
api/
├── routes/     → HTTP handling, maps errors to status codes
├── services/   → Business logic & domain rules
├── models/     → Persistence (SQLAlchemy ORM)
├── domain/     → Domain exceptions (InsufficientStockError, ProductNotFoundError)
├── schemas/    → Input/output validation (Pydantic)
├── core/       → JWT, password hashing & rate limiting
├── middleware/ → Rate limiting middleware (applied to all endpoints)
├── db/         → Session management
└── tests/      → Unit, integration & concurrency tests
```

Business logic stays independent from the web framework.

This structure allows business rules to be tested independently  
from the HTTP layer and database implementation.

---

## ⚙️ Key Engineering Decisions

### 🔒 Concurrency Control
`SELECT FOR UPDATE` locks rows before mutation, preventing race conditions during simultaneous stock updates.

### 🧠 Domain-Driven Validation
Business rules enforced in the service layer:
- No negative stock  
- Typed exceptions (`InsufficientStockError`, `ProductNotFoundError`)  
- Mapped to HTTP responses in routes  

### 🔐 Security
- Argon2 password hashing (resistant to GPU/ASIC attacks)  
- JWT-based authentication  
- Refresh tokens with rotation and server-side revocation (Redis)
- Nginx reverse proxy with rate limiting (30 req/s per IP, burst 50) — first line of defense before requests reach the app
- Rate limiting via middleware (Redis) — applied to all endpoints:
  - `/users/login` → 5 req/min
  - `/users/register` → 10 req/hour
  - `/users/refresh` → 5 req/min
  - `POST /products/{id}/stock` → 10 req/min
  - `POST /products` and `PATCH` → 20 req/min
  - `DELETE` → 5 req/min
  - `GET` → 100 req/min

### 🛡 OWASP Top 10 Coverage
- **A01 Broken Access Control** → owner_id on products, 403 for unauthorized access
- **A02 Cryptographic Failures** → Argon2 password hashing
- **A03 Injection** → SQLAlchemy ORM, no raw queries
- **A07 Authentication Failures** → JWT, rate limiting on auth endpoints, refresh token rotation
- **A08 Software and Data Integrity** → Pydantic input validation, transactional rollbacks
- **A09 Logging Failures** → structured logging on all endpoints

**Known gaps (intentional trade-offs):**
- A05 Security Misconfiguration → CORS set to `*`, should be restricted to specific domains in production
- A06 Vulnerable Components → dependency scanning via Safety added to CI

### 🧪 Testing Strategy
- Unit tests for business logic
- Integration tests for full HTTP flow (Redis mocked for isolation)
- CI via GitHub Actions on every push
- Concurrency tests against real PostgreSQL via Testcontainers to validate `SELECT FOR UPDATE`
- Concurrency tests against real Redis via Testcontainers to validate rate limiting behavior

---

## ⚖️ Trade-offs

### SQLite in Tests

✔️ Fast, no DB server needed in CI  
❌ No support for `SELECT FOR UPDATE`

👉 Concurrency tests run against real PostgreSQL to validate locking behavior.  
Unit and integration tests use SQLite for speed.

This introduces a gap between test and production behavior,  
which is an intentional trade-off for faster CI execution.

### Redis in Tests

✔️ Integration tests mock Redis for speed and isolation  
❌ Mock doesn't validate real rate limiting behavior

👉 Concurrency tests run against real Redis via Testcontainers to validate blocking behavior.

---

## 🚀 Tech Stack

FastAPI · PostgreSQL · SQLAlchemy ·  
Pydantic · Argon2 · JWT · Alembic ·  
Docker · Redis · Pytest · Testcontainers ·  
GitHub Actions

---

## 🧠 Takeaway

This project is not about building an API that works.

It's about building one that keeps working  
when multiple things happen at the same time.

