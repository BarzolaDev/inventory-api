from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABABASE_URL = "postgresql://postgres:goku4321@localhost:5432/inventario_db"

engine = create_engine(DATABABASE_URL)

SessionLocal = sessionmaker(bind=engine)

#todas las tablas heredan de aca
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
