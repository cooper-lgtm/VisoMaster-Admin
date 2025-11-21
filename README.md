## VisoMaster Admin Monorepo

- Backend: FastAPI + PostgreSQL + MinIO (presigned upload/download)
- Frontend: React + TypeScript + Vite + Ant Design

### Quick start (Docker Compose)

```bash
docker-compose up --build
```

Services:

- API: http://localhost:8000 (FastAPI, auto-creates tables on start)
- Frontend preview: http://localhost:4173
- Postgres: localhost:5432
- MinIO: http://localhost:9000 (console http://localhost:9001, admin/minioadmin)

### Backend (local)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Configure `DATABASE_URL` and S3 settings in `.env`.
- Alembic config is ready under `backend/alembic`. Tables also auto-create on startup for dev.

### Frontend (local)

```bash
cd frontend
npm install
npm run dev
```

- API calls are proxied to `http://localhost:8000` via `vite.config.ts`.

### Notes

- Auth uses JWT bearer tokens; admin login at `/auth/admin/login`, user login at `/auth/user/login`.
- Presigned upload flow: `/images/upload-url` -> PUT to returned URL -> `/images` to save metadata.
- Assignments support both directions: `/assignments/users/{id}/assign-images` and `/assignments/images/{id}/assign-users`.
