from api.services.auth import authenticate_user, InvalidCredentialsError
from api.services.user import create_user
from api.schemas.user import UserCreate


import pytest

USER_DEFAULTS = dict(
     username="testuser",
     email="test@example.com",
     password="password123"
)

def test_authenticate_user_ok(db):
      create_user(db, UserCreate(**USER_DEFAULTS))
      token = authenticate_user("test@example.com", "password123", db)
      assert token.access_token is not None


def test_authenticate_user_invalid_credentials(db):
      create_user(db, UserCreate(**USER_DEFAULTS))

      with pytest.raises(InvalidCredentialsError):
          authenticate_user("test@example.com", "wrongpassword", db)