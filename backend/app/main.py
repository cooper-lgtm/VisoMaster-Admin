from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
from sqlalchemy import select
from botocore.exceptions import ClientError

from .config import get_settings
from .deps import SessionLocal, engine
from .models import Admin, Base, StatusEnum
from .routers import admins, assignments, auth, images, stats, users
from .security import get_password_hash
from .storage import get_s3_client

app = FastAPI(title="VisoMaster Admin API")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_admin()
    await ensure_bucket()


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(users.router)
app.include_router(images.router)
app.include_router(assignments.router)
app.include_router(stats.router)


async def seed_admin() -> None:
    settings = get_settings()
    if not settings.seed_admin_username or not settings.seed_admin_password:
        return
    async with SessionLocal() as session:
        exists = await session.execute(select(Admin).where(Admin.username == settings.seed_admin_username))
        if exists.scalar_one_or_none():
            return
        admin = Admin(
            username=settings.seed_admin_username,
            password_hash=get_password_hash(settings.seed_admin_password),
            is_superadmin=settings.seed_admin_is_superadmin,
            status=StatusEnum.active,
        )
        session.add(admin)
        await session.commit()


async def ensure_bucket() -> None:
    settings = get_settings()
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
        return
    except ClientError as e:
        # If bucket not found, try to create; other errors bubble up
        error_code = e.response.get("Error", {}).get("Code")
        if error_code not in ("404", "NoSuchBucket", "404 Not Found", "NotFound"):
            logger.error("Failed to check bucket: %s", e)
            raise
    try:
        params = {"Bucket": settings.s3_bucket}
        if settings.s3_region and settings.s3_region != "us-east-1":
            params["CreateBucketConfiguration"] = {"LocationConstraint": settings.s3_region}
        client.create_bucket(**params)
        logger.info("Created bucket %s", settings.s3_bucket)
    except ClientError as e:
        # Ignore if already exists after race
        error_code = e.response.get("Error", {}).get("Code")
        if error_code not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            logger.error("Failed to create bucket: %s", e)
            raise
