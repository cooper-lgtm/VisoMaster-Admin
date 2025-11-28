from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import get_current_admin, get_db, http_bearer
from ..models import Image, User, UserImage
from ..services import images as image_service
from ..storage import generate_presigned_get_url
from ..security import decode_token

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
    include_urls: bool = Query(False, description="Return presigned download URLs"),
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    session: AsyncSession = Depends(get_db),
):
    # Auth: admin可访问任何用户，user只能访问自己的图片
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    role = payload.get("role")
    username = payload.get("sub")

    target_user = await _get_user(session, user_id)
    if role == "admin":
        pass
    elif role == "user":
        if not username or target_user.username != username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    result = await session.execute(
        select(UserImage, Image)
        .join(Image, Image.id == UserImage.image_id)
        .where(UserImage.user_id == user_id)
    )
    images = [row[1] for row in result.fetchall()]
    if include_urls:
        for img in images:
            img.presigned_url = None
            img.download_url = f"/api/images/{img.id}/download"
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


@router.delete("/users/{user_id}/images/{image_id}", status_code=204)
async def unassign_image_from_user(
    user_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    await image_service.remove_image_from_user(session, user_id, image_id)
    return None
