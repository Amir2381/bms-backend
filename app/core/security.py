import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis import sync_redis
from app.db.database import get_db
from app.models.user import User
from app.repositories import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        email = payload.get("sub")
        jti = payload.get("jti")

        if email is None or jti is None:
            raise credentials_exception

        if sync_redis.exists(f"bl_{jti}"):
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = user_repository.get_user_by_email(
        db,
        email,
    )

    if user is None:
        raise credentials_exception

    return user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user: User) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )

    to_encode = {
        "sub": user.email,
        "role": user.role.value,
        "type": "access",
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt


def create_refresh_token(user: User) -> str:
    expire = datetime.now(UTC) + timedelta(
        days=settings.refresh_token_expire_days,
    )

    to_encode = {
        "sub": user.email,
        "type": "refresh",
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt
