# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack Todo application with:
- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Frontend**: Next.js (React) with TypeScript and shadcn/ui
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT-based with HTTP-only cookies
- **Features**: Todo CRUD, filtering, sorting, pagination, rate limiting, background tasks

## Running the Application

```bash
# Backend (from cloud directory)
cd /Users/Mac/code/project/FastAPI/cloud
python -m uvicorn src.core.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (from frontend directory)
cd /Users/Mac/code/project/FastAPI/frontend
npm run dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Testing

```bash
# All tests (from cloud directory)
pytest src/tests/ -v

# Single test file
pytest src/tests/test_api.py -v

# Single test
pytest src/tests/test_api.py::TestAuthAPI::test_register -v

# With coverage
pytest src/tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Architecture

### Backend Structure (cloud/src/)
- `api/v1/` - API routes and endpoints
- `core/` - App configuration, security, logging, main.py
- `db/` - Database session and CRUD operations
- `models/` - SQLAlchemy models (UserDB, TodoDB)
- `schemas/` - Pydantic request/response schemas
- `services/` - Business logic (todo_service.py)
- `tests/` - Pytest test suite
- `utils/` - Utilities (email)

### Frontend Structure (frontend/src/)
- `app/` - Next.js pages (file-based routing)
- `components/ui/` - shadcn/ui components
- `services/` - API client
- `store/` - Zustand auth state

### Key Files
- `cloud/src/core/main.py` - FastAPI app initialization, middleware setup
- `cloud/src/core/config.py` - Settings via pydantic-settings
- `cloud/src/api/v1/api.py` - Router aggregation
- `cloud/alembic.ini` - Database migration config
- `cloud/docker-compose.yml` - Production stack (API, PostgreSQL, Redis, Nginx)

## Database Migrations

```bash
cd /Users/Mac/code/project/FastAPI/cloud
alembic upgrade head       # Apply migrations
alembic migration create   # Create new migration
alembic history            # View history
```

## Environment Variables

Backend uses `.env` file in cloud directory with settings from `src/core/config.py`. Key variables:
- `DATABASE_URL` - Database connection
- `SECRET_KEY` - JWT signing key
- `DEBUG_MODE` - Enable debug logging
- `CORS_ORIGINS` - Allowed origins

Frontend uses `.env.local` for `NEXT_PUBLIC_API_URL`.

## API Endpoints

- `POST /auth/register` - Register user
- `POST /auth/login` - Login, get JWT
- `GET /auth/me` - Get current user
- `GET /todos` - List todos (pagination, filtering, sorting)
- `POST /todos` - Create todo
- `GET /todos/{id}` - Get todo
- `PATCH /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo
- `GET /health` - Health check
