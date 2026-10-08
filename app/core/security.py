import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis import sync_redis
from app.db.database import get_db
from app.models.user import User
from app.repositories import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


@dataclass
class AuthContext:
    user: User | None = None
    api_key: Any | None = None


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if not token:
        raise credentials_exception
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
    user = user_repository.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


def get_auth_context(
    token: str | None = Depends(oauth2_scheme),
    api_key: str | None = Depends(api_key_header),
    db: Session = Depends(get_db),
) -> AuthContext:
    if token:
        try:
            user = get_current_user(token, db)
            return AuthContext(user=user)
        except HTTPException:
            pass
    if api_key:
        from app.repositories import api_key_repository

        key_record = api_key_repository.get_api_key_by_key(db, api_key)
        if key_record and key_record.is_active:
            if key_record.expires_at and key_record.expires_at.replace(
                tzinfo=UTC
            ) < datetime.now(UTC):
                pass
            else:
                return AuthContext(api_key=key_record)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


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


def blacklist_token(token: str) -> None:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            ttl = exp - int(datetime.now(UTC).timestamp())
            if ttl > 0:
                sync_redis.setex(f"bl_{jti}", ttl, "1")
    except JWTError:
        pass
