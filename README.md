# Inventory Management API

REST API built with FastAPI and PostgreSQL for managing products and stock.

## 🚀 Features
- Create and list products
- Update stock with validation (no negative stock)
- Track stock movements for history and auditing

## 🛠️ Tech Stack
- Python (FastAPI)
- PostgreSQL
- SQLAlchemy

## 📦 Endpoints

### Create Product
POST /products

### Get Products
GET /products

### Update Stock
PATCH /products/{product_id}

## 🧠 Business Logic
- Stock cannot go below zero
- Every stock change creates a movement record
- Ensures data consistency between products and movements
