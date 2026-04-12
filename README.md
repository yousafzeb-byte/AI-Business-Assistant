# AI Business Operations Assistant — React | Flask | PostgreSQL | CI/CD

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?logo=typescript&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![CI](https://github.com/yousafzeb-byte/AI-Business-Assistant/actions/workflows/ci.yml/badge.svg)

## 🎯 Project: Full-Stack AI Business Operations Platform

A production-ready full-stack web application that helps small business owners automate daily operations using AI. Upload invoices, notes, contracts, and tasks — get instant summaries, extracted data, cost tracking, and actionable insights powered by OpenAI GPT-4o.

## Recruiter Snapshot

- Built a full-stack app with **React 19 + TypeScript** frontend and **Flask REST API** backend
- JWT authentication with **access tokens (30 min)** and **refresh token rotation (7 days)**
- **OpenAI GPT-4o-mini** integration for AI-powered document analysis with structured JSON output
- Production security: fail-fast secrets, Marshmallow validation, MIME checks, rate limiting, security headers
- **36 automated tests** covering auth, records, analytics, soft delete, and token refresh
- Containerized with **Docker Compose** (Postgres + Redis + Backend + Frontend) and **CI/CD via GitHub Actions**

## Architecture At A Glance

- Application Factory pattern with Blueprint-based routes and Marshmallow validation
- React 19 + TypeScript SPA with Vite dev server and Nginx production build
- SQLAlchemy ORM with PostgreSQL, connection pooling, and pre-ping health checks
- Redis-backed rate limiting that scales across multiple backend instances
- OpenAI integration for document analysis with explicit error propagation
- Docker Compose orchestrates all services (Postgres, Redis, Backend, Frontend)
- Nginx reverse proxy with security headers, static caching, and HTTPS-ready config

## Visual Showcase

> Add screenshots and demo GIFs under `docs/media/` to make this project faster to evaluate for recruiters.

## 📋 Features Implemented

### 🤖 AI-Powered Analysis

- Document summarization, date/cost/task extraction, category classification via OpenAI GPT-4o-mini
- AI-generated action items with priority levels, cost tracking, and due date detection
- Explicit error propagation (no silent mock fallback) with content truncation for token management

### 🔐 Authentication & Security

- JWT access tokens (30 min) + refresh tokens (7 days) with frontend auto-refresh and request queuing
- Fail-fast config — app refuses to start without required secrets; non-root Docker user
- Security headers (CSP, HSTS, X-Frame-Options, nosniff, XSS-Protection), generic error responses
- Redis-backed rate limiting: 60/min default, 5/min signup, 10/min login, 20/min record creation

### 📄 File Upload & Data Management

- Upload PDF, TXT, MD, CSV with MIME type validation + extension allowlist (10 MB limit)
- Automatic text extraction (PyPDF for PDFs) with file cleanup after processing
- Soft delete with `deleted_at` timestamp (GDPR-aware, recoverable)
- Full-text search, category/status filtering, pagination (max 100 per page)
- Marshmallow schema validation + Bleach sanitization on all inputs

### 📊 Analytics Dashboard

- Total records, expense tracking, category breakdown (pie charts), status distribution (bar charts)
- Pending action items aggregation, soft-deleted records excluded from all analytics

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your secrets and database URL
```

### 3. Initialize Database

```bash
cd backend
export SECRET_KEY="dev-secret" JWT_SECRET_KEY="dev-jwt" DATABASE_URL="sqlite:///dev.db"
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

### 4. Run the Application

```bash
# Backend (terminal 1)
python run.py                                        # → http://localhost:5000

# Frontend (terminal 2)
cd frontend && VITE_API_URL=http://localhost:5000/api npm run dev  # → http://localhost:5173
```

## 🧪 Unit Testing

This project includes 36 automated tests covering all 12 API endpoints:

### Running Tests

```bash
cd backend
SECRET_KEY=test JWT_SECRET_KEY=test DATABASE_URL=sqlite:///:memory: python -m pytest tests/ -v
# 36 passed ✓
```

### Test Breakdown by Module

- **Auth (15 tests)**:
  - Signup (success, duplicate, short password, missing fields, invalid email)
  - Login (success, wrong password, nonexistent user)
  - Get me (success, no token)
  - Refresh token (success, access token rejected)
- **Records (18 tests)**:
  - Create (text, no content, empty content, unauthenticated)
  - List (empty, with records, pagination, search, filter by status)
  - Get (success, not found, other user blocked)
  - Delete (success, not found, already deleted)
  - Update status (success, invalid)
  - Update fields (title, category, invalid category, empty title)
- **Analytics (3 tests)**:
  - Summary empty, summary with records, unauthenticated

## 📊 Database Schema

### Tables

- **users** — Email (unique), password hash, full name, role, timestamps
- **records** — Title, content, AI outputs, metadata, `deleted_at` (soft delete)

### Relationships

- User → Records (One-to-Many)

### Indexes

- `users.email` (unique)
- `records.user_id`, `records.category`, `records.status`, `records.deleted_at`

## 🔑 Key API Endpoints

### Authentication

- `POST /api/auth/signup` — Create account (rate limited: 5/min)
- `POST /api/auth/login` — Login and get access + refresh tokens
- `POST /api/auth/refresh` — Get new access token using refresh token
- `GET /api/auth/me` — Get current user profile (requires token)

### Records

- `POST /api/records` — Create record from text or file upload (AI analyzed)
- `GET /api/records` — List with search, category, status filters + pagination
- `GET /api/records/:id` — Get single record
- `PATCH /api/records/:id` — Update title/category (Marshmallow validated)
- `PATCH /api/records/:id/status` — Update status (processed, pending, archived)
- `DELETE /api/records/:id` — Soft-delete record

### Analytics & Health

- `GET /api/analytics/summary` — Dashboard data (totals, categories, statuses, actions)
- `GET /api/health` — Health check with database connectivity verification

## 🛠️ Technologies Used

- React 19 — Frontend UI framework
- TypeScript 6.0 — Type-safe frontend development
- Vite 8 — Frontend build tool and dev server
- Recharts — Dashboard charts and visualizations
- Axios — HTTP client with interceptors for auth
- Flask 3.1 — Backend web framework
- Flask-SQLAlchemy 3.1 — ORM with connection pooling
- Flask-JWT-Extended 4.7 — JWT access + refresh tokens
- Flask-Limiter 3.12 — Redis-backed rate limiting
- Marshmallow 3.25 — Request validation and serialization
- Bleach 6.2 — HTML/input sanitization
- OpenAI 1.68 — GPT-4o-mini integration
- PyPDF 5.4 — PDF text extraction
- Gunicorn 23 — Production WSGI server
- PostgreSQL 16 — Production database
- Redis 7 — Rate limit storage
- Docker + Docker Compose — Containerization
- Nginx — Reverse proxy with security headers
- GitHub Actions — CI/CD pipeline
- Pytest 8.3 — Backend test framework

## 📁 Project Structure

```
AI-Business-Assistant/
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD: lint, test, build, deploy
├── backend/
│   ├── app/
│   │   ├── __init__.py           # App factory, middleware, error handlers, health check
│   │   ├── config.py             # Fail-fast config with required env vars
│   │   ├── models/               # User (password hashing) + Record (soft delete)
│   │   ├── routes/               # auth, records (CRUD + AI), analytics
│   │   ├── services/ai_service.py    # OpenAI integration with error propagation
│   │   └── utils/file_helpers.py     # MIME validation + text extraction
│   ├── tests/                    # 36 tests: auth (15), records (18), analytics (3)
│   ├── Dockerfile                # Non-root user, gunicorn, worker recycling
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── context/AuthContext.tsx    # Auth state + refresh token management
│   │   ├── services/             # API client (auto-refresh), auth, records
│   │   ├── components/           # ErrorBoundary, Layout, ProtectedRoute
│   │   ├── pages/                # Dashboard, NewInput, History, Analytics, Login, Signup
│   │   └── types/index.ts
│   ├── nginx.conf                # Security headers, caching, proxy, HTTPS-ready
│   └── Dockerfile                # Multi-stage build (Node → Nginx)
├── docker-compose.yml            # Postgres + Redis + Backend + Frontend
├── .env.example                  # All env vars documented
└── README.md
```

## ✅ Project Checklist

### Authentication & Security

- ✅ JWT access + refresh tokens with auto-refresh and request queuing
- ✅ Fail-fast secret validation (app won't start without env vars)
- ✅ Security headers (CSP, HSTS, X-Frame-Options, etc.)
- ✅ Redis-backed rate limiting with per-endpoint limits
- ✅ CORS with explicit origin and credentials
- ✅ Non-root Docker user

### AI Integration

- ✅ OpenAI GPT-4o-mini document analysis with structured JSON output
- ✅ Explicit error propagation (no silent mock fallback)
- ✅ Content truncation to manage token usage

### File Upload & Data

- ✅ MIME type validation + extension allowlist
- ✅ Soft delete, full-text search, pagination
- ✅ Marshmallow schema validation on all inputs

### Testing & CI/CD

- ✅ 36 automated tests (auth, records, analytics)
- ✅ GitHub Actions CI/CD pipeline (lint, test, build, deploy)
- ✅ Backend: Pyright + Pytest + pip-audit
- ✅ Frontend: TypeScript check + ESLint + Vitest + npm audit

### Deployment

- ✅ Docker Compose with Postgres, Redis, Backend, Frontend
- ✅ Gunicorn production server with worker recycling
- ✅ Nginx reverse proxy with caching and security headers
- ✅ HTTPS-ready config, structured JSON logging, health check

## 🚀 Production Deployment

This project is fully containerized and deployment-ready!

### Quick Deploy

1. **Server**: Any VPS with Docker installed (DigitalOcean, AWS EC2, etc.)
2. **Clone**: `git clone <repo> && cd AI-Business-Assistant`
3. **Configure**: `cp .env.example .env && nano .env` (set real secrets)
4. **Launch**: `docker compose up -d --build`
5. **Done**: App available at your server's IP/domain

### CI/CD Pipeline Features

- ✅ **Lint Job**: Pyright (backend) + ESLint (frontend)
- ✅ **Test Job**: Pytest 36 tests + Vitest frontend tests
- ✅ **Build Job**: Docker images pushed to GitHub Container Registry
- ✅ **Deploy Job**: Staging environment with smoke tests
- ✅ **Trigger**: On push/PR to main branch

### Production Features

- Configuration Management: Fail-fast env var validation
- Database: PostgreSQL with connection pooling and pre-ping
- Rate Limiting: Redis-backed, scales across instances
- Logging: Structured JSON to stdout
- Health Check: `/api/health` verifies database connectivity
- HTTPS: Nginx config ready — uncomment SSL block and provide certs

## 🔒 Security Notes

> ⚠️ **Important**: Sensitive data is managed via environment variables in production!

**Secret Key Management**:

- Development: Set in `.env` file (not committed to git)
- Production: Set in server environment variables
- Generate secure key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

**Database Credentials**:

- Never commit database passwords to version control
- Use `.env` for local development (in `.gitignore`)
- Use server environment variables for production

## 📝 Additional Features

Beyond typical project requirements, this project includes:

- Comprehensive error handling with global handlers (400/404/405/429/500)
- JWT error handlers (expired, invalid, missing tokens)
- Frontend error boundary with sanitized error display
- Automatic token refresh with failed request queuing
- Soft delete for data recovery compliance
- Database connection pooling for production performance
- Worker recycling in Gunicorn to prevent memory leaks

## 🤝 Contributing

This is a portfolio project demonstrating full-stack development with production-ready practices.

## 📄 License

MIT License

## 👨‍💻 Author

**Yousaf Zeb** — Full-Stack Software Engineer
Project completed: **April 2026**
Stack: **React, TypeScript, Flask, PostgreSQL, Redis, Docker, OpenAI**
