from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .deps import engine
from .models import Base
from .routers import admins, assignments, auth, images, stats, users

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


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(users.router)
app.include_router(images.router)
app.include_router(assignments.router)
app.include_router(stats.router)
