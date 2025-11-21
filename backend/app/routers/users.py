from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import get_current_admin, get_db
from ..models import StatusEnum, User
from ..security import get_password_hash
from ..services import users as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[schemas.UserRead])
async def list_users(
    session: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars())


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: schemas.UserCreate,
    session: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return await user_service.create_user(session, payload)


async def _get_user_or_404(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/{user_id}", response_model=schemas.UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return await _get_user_or_404(session, user_id)


@router.patch("/{user_id}", response_model=schemas.UserRead)
async def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    user = await _get_user_or_404(session, user_id)
    return await user_service.update_user(session, user, payload)


@router.post("/{user_id}/extend", response_model=schemas.UserRead)
async def extend_user(
    user_id: int,
    payload: schemas.UserExtendRequest,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    user = await _get_user_or_404(session, user_id)
    return await user_service.extend_user(session, user, payload, operator_admin_id=admin.id)


@router.post("/{user_id}/reset_password", response_model=schemas.UserRead)
async def reset_password(
    user_id: int,
    payload: schemas.UserUpdate,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    if not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password required")
    user = await _get_user_or_404(session, user_id)
    user.password_hash = get_password_hash(payload.password)
    await session.commit()
    await session.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=schemas.UserRead)
async def update_user_status(
    user_id: int,
    payload: schemas.UserUpdate,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    user = await _get_user_or_404(session, user_id)
    if payload.status is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status required")
    user.status = payload.status
    await session.commit()
    await session.refresh(user)
    return user
