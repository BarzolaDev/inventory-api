# ⚙️ Inventory Management System

Backend system built with FastAPI, designed to ensure **data consistency and reliable behavior under concurrent operations**.

Focused on enforcing **business rules at the service layer**, preventing **race conditions**, and maintaining **transactional integrity** in real-world inventory scenarios.

👉 Live Demo: https://inventory-api-jpwh.onrender.com/docs

---

## 🧠 Overview

This project simulates a production-style backend where stock operations must remain consistent even under concurrent access.

Key design goals:

- Ensure **data consistency** during stock mutations  
- Prevent **race conditions** using database-level locking (`SELECT FOR UPDATE`)  
- Enforce **domain-level validation** to guarantee that stock never becomes invalid  
- Maintain clear **separation of concerns** through a layered architecture  
- Provide **predictable and testable behavior** via automated testing  

---

## ⚙️ Core Principles

- **Transactional Integrity:** All stock updates are executed within controlled transactions  
- **Business Rules Enforcement:** Validation is handled in the service layer, not in routes  
- **Layered Architecture:** Decouples HTTP handling from core business logic  
- **Dependency Injection:** Resources are managed via FastAPI dependencies  
- **Regression Prevention:** Critical logic is protected through test coverage  

---

## 🧱 Architecture

Structured using a **layered architecture** to isolate responsibilities:

- **Routes:** Handle HTTP requests and responses  
- **Services:** Contain core business logic and domain validation  
- **Models:** Represent database entities (SQLAlchemy)  
- **Schemas:** Validate input/output data (Pydantic)  
- **Core:** Security, authentication, and shared dependencies  
- **DB:** Session management and database configuration  

---

## 🧪 Reliability

The system is built with a strong focus on **testable business logic** and **regression prevention**:

- Service-level tests for domain rules  
- Integration tests validating HTTP behavior  
- Isolated test environment for consistent execution  

---

## 🔐 Security

- **JWT-based authentication** for stateless access control  
- **Argon2 password hashing** for secure credential storage  

---

## ⚡ Configuration

Centralized configuration using **Pydantic Settings**, with environment loading extracted into a dedicated module (`load_toenv()`), improving:

- Maintainability  
- Environment consistency  
- Testability  

---

## 🚀 Environment

- Containerized setup using Docker for reproducible environments  
- Database migrations handled via Alembic  
