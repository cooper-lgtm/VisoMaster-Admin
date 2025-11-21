from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import get_current_admin, get_db
from ..models import Image, StatusEnum, User

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=schemas.StatsSummary)
async def summary(session: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    total_users = (await session.execute(select(func.count()).select_from(User))).scalar_one()
    active_users = (
        await session.execute(select(func.count()).select_from(User).where(User.status == StatusEnum.active))
    ).scalar_one()
    disabled_users = total_users - active_users
    soon = datetime.now(timezone.utc) + timedelta(days=7)
    expiring_users = (
        await session.execute(
            select(func.count()).select_from(User).where(User.expires_at.is_not(None), User.expires_at <= soon)
        )
    ).scalar_one()
    total_images = (await session.execute(select(func.count()).select_from(Image))).scalar_one()
    return schemas.StatsSummary(
        total_users=total_users,
        active_users=active_users,
        disabled_users=disabled_users,
        expiring_users=expiring_users,
        total_images=total_images,
    )
