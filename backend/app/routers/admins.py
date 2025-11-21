from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import get_current_admin, get_db, require_superadmin
from ..models import Admin, StatusEnum
from ..security import get_password_hash

router = APIRouter(prefix="/admins", tags=["admins"])


@router.get("/me", response_model=schemas.AdminRead)
async def read_me(admin: Admin = Depends(get_current_admin)):
    return admin


@router.post("/", response_model=schemas.AdminRead, status_code=status.HTTP_201_CREATED)
async def create_admin(
    payload: schemas.AdminCreate,
    session: AsyncSession = Depends(get_db),
    _superadmin: Admin = Depends(require_superadmin),
):
    exists = await session.execute(select(Admin).where(Admin.username == payload.username))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists")
    admin = Admin(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        is_superadmin=payload.is_superadmin,
        status=payload.status,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


@router.patch("/{admin_id}", response_model=schemas.AdminRead)
async def update_admin(
    admin_id: int,
    payload: schemas.AdminUpdate,
    session: AsyncSession = Depends(get_db),
    _superadmin: Admin = Depends(require_superadmin),
):
    result = await session.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    if payload.password:
        admin.password_hash = get_password_hash(payload.password)
    if payload.is_superadmin is not None:
        admin.is_superadmin = payload.is_superadmin
    if payload.status:
        admin.status = payload.status
    await session.commit()
    await session.refresh(admin)
    return admin
