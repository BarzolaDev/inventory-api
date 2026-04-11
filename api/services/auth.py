from sqlalchemy.orm import Session
from api.models import user
from api.schemas.auth import TokenResponse
from api.core.security import create_access_token, verify_password


class InvalidCredentialsError(Exception):
    pass

def authenticate_user(email: str, password_plain: str, db: Session) -> TokenResponse:
    user = (
        db.query(user.User)
        .filter(user.User.email == email)
        .first()
    )

    if not user or not verify_password(password_plain, user.hashed_password):
        raise InvalidCredentialsError("Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return TokenResponse(
        access_token=access_token
    )

