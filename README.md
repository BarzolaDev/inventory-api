# ⚙️ Inventory Management API

Production-oriented REST API built with FastAPI, focused on two things:

👉 Keeping data consistent under concurrent operations.
👉 Learning to defend itself from attacks in real time.

---

## 🤖 ML Security Layer

A behavioral analysis system that learns from every request.

```
Request → Logs (eyes) → PostgreSQL (memory) → Random Forest (reasoning) → Block or Allow
```
- Random Forest trained on synthetic traffic (NORMAL / SUSPICIOUS / BLOCKED)
- `class_weight="balanced"` to handle class imbalance
- `ml_predictor.py` loads the model and assists `agent_defender.py` in real time
- Auto-override if model confidence ≥ 85%
- **Feedback loop**: every request is stored in DB → next training cycle improves the model

The model doesn't just block known attacks — it learns patterns and blocks what the rules didn't anticipate.

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

## 💥 Core Problem:

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
├── middleware/ → Rate limiting + structured audit logging
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

**Network architecture — single entry point:**
- Only port 80 (Nginx) exposed to the exterior
- Redis, PostgreSQL, PgBouncer, and API have no exposed ports
- All internal communication via Docker network only

**Defense in depth:**
- **TLS/HTTPS** → managed by Render (Let's Encrypt, automatic renewal) — encrypted transport in production
- Nginx reverse proxy with rate limiting (30 req/s per IP, burst 50) — first line of defense
- **ModSecurity WAF + OWASP CRS** → 846 rules active, blocks SQL injection, XSS and known attacks (HTTP 403)
- **ModSecurity CRS Paranoia Level 2** — blocks malicious user-agents (sqlmap, nikto, scrapy) and requests missing standard browser headers at network level
- Argon2 password hashing (resistant to GPU/ASIC attacks)
- JWT-based authentication with refresh token rotation and server-side revocation (Redis)
- CORS restricted to specific origins (configured via environment variable)
- Rate limiting via middleware (Redis) — applied to all endpoints
- **PgBouncer** — connection pooling, no direct database access from exterior
- **Agent detection middleware** — behavioral analysis before requests reach business logic:
  - Honeypot endpoints — flags and blocks automation instantly
  - IP blocking via Redis (1 hour TTL)
  - Timing analysis — detects non-human request intervals via standard deviation (< 50ms variability = agent)
- **Behavioral analysis agent** (`agent_defender`) — evaluates each action in real time via scoring:
  - Mass product scraping detection
  - Stock manipulation without prior product lookup
  - Automated off-hours activity detection
  - Repetitive sequence detection — same endpoints looping = bot
  - Repeated stock manipulation detection
  - Decisions: `NORMAL` / `SUSPICIOUS` / `BLOCKED`
  - **Dual blacklist**: IP-based (1h TTL) + user_id-based (1h or 24hs based on score) — proxy-resistant
  - **Long-term memory (24hs)**: cross-session tracking — detects attackers who recon first, attack later
  - **Recon/attack correlation**: if ≥2 recon signals in long_history (24hs) + active attack now → score ×3.0 multiplier
  - **Adaptive thresholds**: block thresholds adjust dynamically based on time of day (night = stricter), system-wide attack pressure (global block counter in Redis), and recidivism — thresholds can drop up to 66% for high-risk contexts
  - **ML layer**: Random Forest model trained on real traffic assists decisions in real time — auto-override at ≥85% confidence

### 🛡 OWASP Top 10 Coverage
- **A01 Broken Access Control** → owner_id enforced on all product endpoints (list, get, movements) — users only see their own data. Generic 404 on all not-found responses to avoid confirming resource existence
- **A02 Cryptographic Failures** → Argon2 password hashing + TLS in transit (Render)
- **A03 Injection** → SQLAlchemy ORM, no raw queries + ModSecurity WAF blocking injection patterns at network level
- **A05 Security Misconfiguration** → CORS restricted to specific origins, no exposed ports except Nginx
- **A06 Vulnerable Components** → dependency scanning via pip-audit in CI
- **A07 Authentication Failures** → JWT, rate limiting on auth endpoints, refresh token rotation. Timing attack mitigation: dummy Argon2 hash computed on non-existent users to normalize response time and prevent user enumeration
- **A08 Software and Data Integrity** → Pydantic input validation, transactional rollbacks
- **A09 Logging Failures** → structured audit logging on all endpoints + agent detection events (honeypot_triggered, agent_detected_timing, blocked_ip_request)

Known gaps (intentional trade-offs):
- **Encryption at rest** → PostgreSQL data on disk is not encrypted — requires filesystem-level or pgcrypto solution, deferred for this stage

### 🧪 Testing Strategy
- Unit tests for business logic
- Integration tests for full HTTP flow (Redis mocked for isolation)
- CI via GitHub Actions on every push
- Concurrency tests against real PostgreSQL via Testcontainers to validate `SELECT FOR UPDATE`
- Concurrency tests against real Redis via Testcontainers to validate rate limiting behavior

### 📋 Audit Logging
Structured logging across two layers:
- **Middleware** → every request: method, path, status code, duration, user_id, IP
- **Service layer** → business events: stock_lock_waiting, stock_lock_acquired,
  stock_updated (before/after/delta), stock_insufficient

Under 1000 concurrent requests (rate limiter disabled for testing), logs confirmed:
- SELECT FOR UPDATE serialized all operations correctly
- No request read a stale stock value
- System saturated at PostgreSQL max_connections=100 — infrastructure limit,
  not a code bug. Protected in production by rate limiting (10 req/min on stock endpoint)

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

### Connection Pool Under Extreme Load
Under 1000 concurrent requests, PostgreSQL max_connections=100 was saturated → 500 errors.
In production this cannot occur — rate limiting caps stock endpoint at 10 req/min.
Production-scale solution implemented: PgBouncer with transaction pooling (max 1000 client connections → 20 real PostgreSQL connections).

---

## 🚀 Tech Stack

FastAPI · PostgreSQL · SQLAlchemy ·
Pydantic · Argon2 · JWT · Alembic ·
Docker · Redis · Pytest · Testcontainers ·
GitHub Actions · Nginx · ModSecurity · PgBouncer ·
scikit-learn · Random Forest · SMOTE

---

## 🧠 Takeaway

This project is not about building an API that works.

It's about building one that keeps working — and keeps learning —
when multiple things happen at the same time.