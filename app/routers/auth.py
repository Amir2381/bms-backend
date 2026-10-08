from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis import sync_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    oauth2_scheme,
    verify_password,
    blacklist_token,
)
from app.db.database import get_db
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import LogoutRequest, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    db_user = user_repository.get_user_by_email(db, form_data.username)
    if db_user is None or not verify_password(
        form_data.password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )
    access_token = create_access_token(db_user)
    refresh_token = create_refresh_token(db_user)
    payload = jwt.decode(
        refresh_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    sync_redis.sadd(f"user_sessions:{db_user.id}", payload["jti"])
    sync_redis.expire(
        f"user_sessions:{db_user.id}", settings.refresh_token_expire_days * 86400
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            request.refresh_token, settings.secret_key, algorithms=[settings.algorithm]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        email = payload.get("sub")
        jti = payload.get("jti")
        db_user = user_repository.get_user_by_email(db, email)
        if db_user is None or not sync_redis.sismember(
            f"user_sessions:{db_user.id}", jti
        ):
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )
        new_access_token = create_access_token(db_user)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
def logout(
    request: LogoutRequest,
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
):
    blacklist_token(token)
    if request.refresh_token:
        try:
            rt_payload = jwt.decode(
                request.refresh_token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
            rt_jti = rt_payload.get("jti")
            if rt_jti:
                sync_redis.srem(f"user_sessions:{current_user.id}", rt_jti)
        except JWTError:
            pass
    return {"message": "Logged out successfully"}


@router.post("/logout-all")
def logout_all(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
):
    blacklist_token(token)
    sync_redis.delete(f"user_sessions:{current_user.id}")
    return {"message": "Logged out from all devices successfully"}
