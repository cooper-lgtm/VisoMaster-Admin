from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import select

from .config import get_settings
from .deps import SessionLocal, engine
from .models import Admin, Base, StatusEnum
from .routers import admins, assignments, auth, images, stats, users
from .security import get_password_hash

app = FastAPI(title="VisoMaster Admin API")

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
