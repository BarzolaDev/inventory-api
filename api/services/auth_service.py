from sqlalchemy.orm import Session
from models import user_model
from schemas.auth_schema import TokenResponse
from core.security import create_access_token, verify_password


class InvalidCredentialsError(Exception):
    pass

def authenticate_user(email: str, password_plain: str, db: Session) -> TokenResponse:
    user = (
        db.query(user_model.User)
        .filter(user_model.User.email == email)
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

