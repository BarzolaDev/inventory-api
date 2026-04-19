from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from sqlalchemy.orm import Session
from api.core.settings import settings

is_sqlite = str(settings.DATABASE_URL).startswith("sqlite")

engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    **({} if is_sqlite else {"pool_size": 10, "max_overflow": 20})
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()