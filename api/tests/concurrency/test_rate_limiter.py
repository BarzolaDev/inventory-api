import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from testcontainers.redis import RedisContainer

from api.main import app
from api.core import redis_client as redis_module


@pytest.fixture(scope="module")
def real_redis_client(pg_client):
    with RedisContainer("redis:7-alpine") as redis_cont:
        host = redis_cont.get_container_host_ip()
        port = redis_cont.get_exposed_port(6379)

        import redis as sync_redis
        sync_redis.Redis(host=host, port=int(port)).ping()

        import redis.asyncio as aioredis
        async_client = aioredis.from_url(
            f"redis://{host}:{port}",
            encoding="utf-8",
            decode_responses=True
        )
        redis_module.redis_client = async_client
        yield pg_client

@pytest.mark.real_redis
def test_rate_limit_blocks_after_limit(real_redis_client):
    # Los primeros 5 intentos pasan (401 credenciales malas)
    for _ in range(5):
        response = real_redis_client.post("/users/login", data={
            "username": "fake@fake.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    # El 6to debe ser bloqueado por rate limiter
    response = real_redis_client.post("/users/login", data={
        "username": "fake@fake.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 429