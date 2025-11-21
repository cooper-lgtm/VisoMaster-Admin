from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import get_current_admin, get_db
from ..models import Image, User, UserImage
from ..services import images as image_service

router = APIRouter(prefix="/assignments", tags=["assignments"])


async def _get_image(session: AsyncSession, image_id: int) -> Image:
    result = await session.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


async def _get_user(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/images/{image_id}/assign-users")
async def assign_users(
    image_id: int,
    payload: schemas.AssignUsersRequest,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    image = await _get_image(session, image_id)
    await image_service.assign_image_to_users(session, image, payload, admin)
    return {"status": "ok"}


@router.post("/users/{user_id}/assign-images")
async def assign_images(
    user_id: int,
    payload: schemas.AssignImagesRequest,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    user = await _get_user(session, user_id)
    await image_service.assign_images_to_user(session, user, payload, admin)
    return {"status": "ok"}


@router.get("/users/{user_id}/images", response_model=list[schemas.ImageRead])
async def list_images_for_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    await _get_user(session, user_id)
    result = await session.execute(
        select(UserImage, Image)
        .join(Image, Image.id == UserImage.image_id)
        .where(UserImage.user_id == user_id)
    )
    images = [row[1] for row in result.fetchall()]
    return images


@router.get("/images/{image_id}/users", response_model=list[schemas.UserRead])
async def list_users_for_image(
    image_id: int,
    session: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    await _get_image(session, image_id)
    result = await session.execute(
        select(UserImage, User)
        .join(User, User.id == UserImage.user_id)
        .where(UserImage.image_id == image_id)
    )
    users = [row[1] for row in result.fetchall()]
    return users
