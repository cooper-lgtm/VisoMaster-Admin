from typing import Iterable, List, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Admin, Image, User, UserImage
from ..schemas import AssignImagesRequest, AssignUsersRequest, ImageCreate


async def create_image_record(session: AsyncSession, payload: ImageCreate, admin: Optional[Admin]) -> Image:
    image = Image(
        bucket=payload.bucket,
        key=payload.key,
        filename=payload.filename,
        mime_type=payload.mime_type,
        size_bytes=payload.size_bytes,
        checksum_sha256=payload.checksum_sha256,
        uploader_admin_id=admin.id if admin else None,
    )
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image


async def list_images(session: AsyncSession) -> List[Image]:
    result = await session.execute(select(Image).order_by(Image.created_at.desc()))
    return list(result.scalars())


async def delete_image(session: AsyncSession, image: Image) -> None:
    await session.delete(image)
    await session.commit()


async def remove_image_from_user(session: AsyncSession, user_id: int, image_id: int) -> None:
    result = await session.execute(
        select(UserImage).where(UserImage.user_id == user_id, UserImage.image_id == image_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    await session.delete(link)
    await session.commit()


async def assign_image_to_users(
    session: AsyncSession, image: Image, payload: AssignUsersRequest, admin: Optional[Admin]
) -> None:
    for user_id in payload.user_ids:
        exists = await session.execute(select(UserImage).where(UserImage.user_id == user_id, UserImage.image_id == image.id))
        if exists.scalar_one_or_none():
            continue
        session.add(
            UserImage(
                user_id=user_id,
                image_id=image.id,
                expires_at=payload.expires_at,
                granted_by_admin_id=admin.id if admin else None,
            )
        )
    await session.commit()


async def assign_images_to_user(
    session: AsyncSession, user: User, payload: AssignImagesRequest, admin: Optional[Admin]
) -> None:
    for image_id in payload.image_ids:
        exists = await session.execute(
            select(UserImage).where(UserImage.user_id == user.id, UserImage.image_id == image_id)
        )
        if exists.scalar_one_or_none():
            continue
        session.add(
            UserImage(
                user_id=user.id,
                image_id=image_id,
                expires_at=payload.expires_at,
                granted_by_admin_id=admin.id if admin else None,
            )
        )
    await session.commit()
