from api.services.user import (
    create_user,
    get_user_by_id,
    UserAlreadyExistsError,
    UserNotFoundError
)

from api.schemas.user import UserCreate

import pytest


USER_DEFAULTS = dict(
    username="testuser",
    email="test@example.com",
    password="password123"
)


def test_create_user_ok(db):
    data = UserCreate(**USER_DEFAULTS)
    user = create_user(db, data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"


def test_get_user_by_id(db):
    data = UserCreate(**USER_DEFAULTS)
    created = create_user(db, data)

    user = get_user_by_id(db, created.id)

    assert user.id == created.id
    assert user.email == created.email


def test_create_user_already_exists(db):
    data = UserCreate(**USER_DEFAULTS)
    create_user(db, data)

    with pytest.raises(UserAlreadyExistsError):
        create_user(db, data)


def test_get_user_by_id_not_found(db):
    with pytest.raises(UserNotFoundError):
        get_user_by_id(db, 9999)
