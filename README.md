## Sistema de gestión de inventario (API REST)

# Estoy CONSTRUYENDO una API De inventario con control de stock y registro de movimientos

## 🚀 Features
- El stock se actualiza de forma segura;
- Excepciones HTTP
- Cada cambio de Stock se registra en "STOCK MOVEMENT"
- Los cambios de stock ACUMULATIVOS
## 🛠️ Tech Stack
- Python
- FastAPI 
- PostgreSQL 
- SQLAlchemy

## 📦 Endpoints

### Crear producto
POST /products

### Obtener producto
GET /products

### Modificar Stock
PATCH /products/{product_id}

### Stock Movement
-> En proceso ya lo detecto y almaceno en DB 

## 🧠 Lógica 
- El stock no puede llegar a menos de 0
- El stock se le suma al que ya tengo almacenado
- Movimientos de STOCK
  
  
