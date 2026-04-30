from api.services.auth import authenticate_user, refresh_access_token, InvalidCredentialsError
from api.services.user import create_user
from api.schemas.user import UserCreate
import pytest

USER_DEFAULTS = dict(
    username="testuser",
    email="test@example.com",
    password="password123"
)

@pytest.mark.asyncio
async def test_authenticate_user_ok(db):
    create_user(db, UserCreate(**USER_DEFAULTS))
    token = await authenticate_user("test@example.com", "password123", db)
    assert token.access_token is not None
    assert token.refresh_token is not None


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(db):
    create_user(db, UserCreate(**USER_DEFAULTS))
    with pytest.raises(InvalidCredentialsError):
        await authenticate_user("test@example.com", "wrongpassword", db)


@pytest.mark.asyncio
async def test_refresh_token_ok(db):
    create_user(db, UserCreate(**USER_DEFAULTS))
    token_response = await authenticate_user("test@example.com", "password123", db)
    new_tokens = await refresh_access_token(token_response.refresh_token, db)
    assert new_tokens.access_token is not None
    assert new_tokens.refresh_token is not None
    assert new_tokens.refresh_token != token_response.refresh_token


@pytest.mark.asyncio
async def test_refresh_token_revoked(db):
    create_user(db, UserCreate(**USER_DEFAULTS))
    token_response = await authenticate_user("test@example.com", "password123", db)
    await refresh_access_token(token_response.refresh_token, db)
    with pytest.raises(InvalidCredentialsError):
        await refresh_access_token(token_response.refresh_token, db)