import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import get_current_admin, get_db
from ..models import Image
from ..services import images as image_service
from ..storage import generate_presigned_get_url, generate_presigned_put_url

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload-url", response_model=schemas.UploadUrlResponse)
async def request_upload_url(
    payload: schemas.UploadUrlRequest,
    _admin=Depends(get_current_admin),
):
    filename = Path(payload.filename).name
    directory = payload.directory or "uploads"
    key = f"{directory}/{uuid.uuid4()}/{filename}"
    presigned = generate_presigned_put_url(key=key, content_type=payload.content_type)
    return schemas.UploadUrlResponse(**presigned)


@router.post("/", response_model=schemas.ImageRead, status_code=status.HTTP_201_CREATED)
async def save_image_metadata(
    payload: schemas.ImageCreate,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return await image_service.create_image_record(session, payload, admin)


@router.get("/", response_model=list[schemas.ImageRead])
async def list_images(
    include_urls: bool = Query(False, description="Return presigned download URLs"),
    session: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    images = await image_service.list_images(session)
    if include_urls:
        for img in images:
            img.presigned_url = generate_presigned_get_url(img.key)
    return images


async def _get_image_or_404(session: AsyncSession, image_id: int) -> Image:
    result = await session.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return image


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    session: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    image = await _get_image_or_404(session, image_id)
    await image_service.delete_image(session, image)
    return None
