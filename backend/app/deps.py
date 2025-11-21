from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings
from .models import Admin, StatusEnum, User
from .security import decode_token

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
http_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    session: AsyncSession = Depends(get_db),
) -> Admin:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await session.execute(select(Admin).where(Admin.username == username))
    admin = result.scalar_one_or_none()
    if not admin or admin.status != StatusEnum.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")
    return admin


async def require_superadmin(admin: Admin = Depends(get_current_admin)) -> Admin:
    if not admin.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superadmin required")
    return admin


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload.get("role") != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or user.status != StatusEnum.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user
