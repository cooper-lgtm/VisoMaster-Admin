from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..config import get_settings
from ..deps import get_db
from ..models import Admin, StatusEnum, User
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/admin/login", response_model=schemas.TokenResponse)
async def admin_login(payload: schemas.AdminLoginRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Admin).where(Admin.username == payload.username))
    admin = result.scalar_one_or_none()
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if admin.status != StatusEnum.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    admin.last_login_at = datetime.now(timezone.utc)
    await session.commit()
    token = create_access_token(subject=admin.username, role="admin")
    return schemas.TokenResponse(access_token=token)


@router.post("/user/login", response_model=schemas.TokenResponse)
async def user_login(payload: schemas.UserLoginRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.status != StatusEnum.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    if user.expires_at and user.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account expired")

    token = create_access_token(subject=user.username, role="user", expires_minutes=settings.jwt_expires_minutes)
    return schemas.TokenResponse(access_token=token)
