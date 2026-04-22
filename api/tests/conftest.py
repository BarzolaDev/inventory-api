import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from api.core.settings import settings
from api.db.database import Base, get_db
from api.main import app


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_client(client):
    client.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "secret123"
    })
    response = client.post("/users/login", data={
        "username": "test@test.com",
        "password": "secret123"
    })
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(scope="session")
def pg_client():
    with PostgresContainer("postgres:16-alpine") as postgres:
        pg_engine = create_engine(postgres.get_connection_url())
        PgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)

        Base.metadata.create_all(bind=pg_engine)

        def override_get_db():
            db = PgSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=pg_engine)


@pytest.fixture(scope="function")
def pg_auth_client(pg_client):
    pg_client.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "secret123"
    })
    response = pg_client.post("/users/login", data={
        "username": "test@test.com",
        "password": "secret123"
    })
    token = response.json()["access_token"]
    pg_client.headers.update({"Authorization": f"Bearer {token}"})
    return pg_client