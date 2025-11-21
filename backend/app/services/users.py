from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import StatusEnum, User, UserExtension
from ..schemas import UserCreate, UserExtendRequest, UserUpdate
from ..security import get_password_hash
from ..utils.time import utc_now


async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    exists = await session.execute(select(User).where(User.username == payload.username))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        status=payload.status,
        expires_at=payload.expires_at,
        notes=payload.notes,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user: User, payload: UserUpdate) -> User:
    if payload.password:
        user.password_hash = get_password_hash(payload.password)
    if payload.status:
        user.status = payload.status
    if payload.expires_at is not None:
        user.expires_at = payload.expires_at
    if payload.notes is not None:
        user.notes = payload.notes
    await session.commit()
    await session.refresh(user)
    return user


async def extend_user(
    session: AsyncSession, user: User, payload: UserExtendRequest, operator_admin_id: Optional[int]
) -> User:
    record = UserExtension(
        user_id=user.id,
        old_expires_at=user.expires_at,
        new_expires_at=payload.new_expires_at,
        reason=payload.reason,
        operated_by_admin_id=operator_admin_id,
        created_at=utc_now(),
    )
    user.extended_until = payload.new_expires_at
    user.expires_at = payload.new_expires_at
    session.add(record)
    await session.commit()
    await session.refresh(user)
    return user


async def disable_user(session: AsyncSession, user: User) -> User:
    user.status = StatusEnum.disabled
    await session.commit()
    await session.refresh(user)
    return user
