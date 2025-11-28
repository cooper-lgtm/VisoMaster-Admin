import uuid
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from PIL import Image as PILImage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..config import get_settings
from ..deps import get_current_admin, get_db
from ..models import Image
from ..services import images as image_service
from ..storage import get_s3_client

router = APIRouter(prefix="/images", tags=["images"])


def _make_thumb(data: bytes, max_size: int = 400) -> tuple[bytes, str]:
    """Generate a thumbnail and return bytes and mime."""
    img = PILImage.open(BytesIO(data))
    img.thumbnail((max_size, max_size))
    fmt = (img.format or "PNG").upper()
    mime = f"image/{'jpeg' if fmt == 'JPG' else fmt.lower()}"
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue(), mime


@router.post("/upload-file", response_model=schemas.ImageRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    directory: str | None = None,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    settings = get_settings()
    filename = Path(file.filename or "upload.bin").name
    key = f"{directory or 'uploads'}/{uuid.uuid4()}/{filename}"
    data = await file.read()
    client = get_s3_client()
    client.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data,
        ContentType=file.content_type or "application/octet-stream",
    )
    thumb_key = f"{key}.thumb"
    try:
        thumb_bytes, thumb_mime = _make_thumb(data)
        client.put_object(
            Bucket=settings.s3_bucket,
            Key=thumb_key,
            Body=thumb_bytes,
            ContentType=thumb_mime,
        )
    except Exception:
        thumb_key = None

    image = await image_service.create_image_record(
        session,
        schemas.ImageCreate(
            bucket=settings.s3_bucket,
            key=key,
            filename=filename,
            mime_type=file.content_type,
            size_bytes=len(data),
        ),
        admin,
    )
    image.presigned_url = None
    image.download_url = f"/api/images/{image.id}/download"
    image.thumb_url = f"/api/images/{image.id}/thumb" if thumb_key else None
    return image


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
            img.presigned_url = None
            img.download_url = f"/api/images/{img.id}/download"
            img.thumb_url = f"/api/images/{img.id}/thumb"
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


@router.get("/{image_id}/download")
async def download_image(
    image_id: int,
    session: AsyncSession = Depends(get_db),
    # 下载不再强制鉴权，依赖后端仅内网访问 MinIO
):
    image = await _get_image_or_404(session, image_id)
    client = get_s3_client()
    obj = client.get_object(Bucket=image.bucket, Key=image.key)
    stream = obj["Body"]
    return StreamingResponse(
        stream.iter_chunks(),
        media_type=image.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{image.filename}"', "Cache-Control": "public, max-age=86400"},
    )


@router.get("/{image_id}/thumb")
async def get_thumb(
    image_id: int,
    session: AsyncSession = Depends(get_db),
):
    image = await _get_image_or_404(session, image_id)
    settings = get_settings()
    client = get_s3_client()
    thumb_key = f"{image.key}.thumb"
    try:
        client.head_object(Bucket=settings.s3_bucket, Key=thumb_key)
    except Exception:
        obj = client.get_object(Bucket=image.bucket, Key=image.key)
        original = obj["Body"].read()
        thumb_bytes, thumb_mime = _make_thumb(original)
        client.put_object(Bucket=settings.s3_bucket, Key=thumb_key, Body=thumb_bytes, ContentType=thumb_mime)

    obj = client.get_object(Bucket=settings.s3_bucket, Key=thumb_key)
    stream = obj["Body"]
    return StreamingResponse(
        stream.iter_chunks(),
        media_type=obj.get("ContentType", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=86400"},
    )
