# IssueHub — Full-Stack Issue Tracking System

> A full-stack web application for tracking bugs and issues across projects.  
> Built with **FastAPI** · **React** · **SQLAlchemy** · **JWT Auth**

---

## Table of Contents

- [Project Overview](#1-project-overview)
- [Technology Stack](#2-technology-stack)
- [Project Structure](#3-project-structure)
- [Setup & Installation](#4-setup--installation)
- [API Reference](#5-api-reference)
- [Authentication & Security](#6-authentication--security)
- [Database Design](#7-database-design)
- [Frontend Architecture](#8-frontend-architecture)
- [Error Handling](#9-error-handling)
- [Running the Application](#10-running-the-application)
- [Key Design Choices](#11-key-design-choices)
- [Limitations & Future Improvements](#12-limitations--future-improvements)

---

## 1. Project Overview

**IssueHub** is a full-stack issue tracking system built as an academic assignment. It demonstrates:

- RESTful API design with FastAPI
- JWT-based stateless authentication
- Role-based access control (RBAC)
- Relational database modeling with SQLAlchemy
- A React single-page frontend with no CSS framework

It is comparable in feature set to tools like **GitHub Issues**, **Jira**, and **Linear**.

> ✅ Built entirely from scratch — no pre-built admin panels or scaffolding tools were used.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 (Vite) | Single-page application, component-based UI |
| Frontend | Vanilla CSS-in-JS | Custom design system, no external CSS framework |
| Backend | FastAPI (Python) | Async REST API with automatic OpenAPI docs |
| Backend | SQLAlchemy ORM | Database models, queries, session management |
| Backend | Pydantic v2 | Request/response schema validation |
| Auth | JWT (python-jose) | Stateless authentication via Bearer tokens |
| Auth | bcrypt (passlib) | Secure password hashing |
| Database | SQLite / PostgreSQL | Relational storage (configurable via `.env`) |
| Dev Tools | Uvicorn | ASGI server for running FastAPI |
| Dev Tools | python-dotenv | Environment variable management |

---

## 3. Project Structure

### 3.1 Backend

```
backend/
├── app/
│   ├── main.py                  # App entry point, middleware, routers
│   ├── database.py              # SQLAlchemy engine & session
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── project.py           # Project model
│   │   ├── project_member.py    # Membership + roles
│   │   ├── issue.py             # Issue model
│   │   └── comment.py           # Comment model
│   ├── schemas/
│   │   ├── user.py              # UserCreate, UserLogin
│   │   ├── project.py           # ProjectCreate, ProjectResponse
│   │   ├── issue.py             # IssueCreate, IssueUpdate, IssueResponse
│   │   └── comment.py           # CommentCreate, CommentResponse
│   ├── routers/
│   │   ├── auth.py              # /api/auth/*
│   │   ├── projects.py          # /api/projects/*
│   │   ├── issues.py            # /api/issues/*
│   │   └── comments.py          # /api/comments/*
│   ├── core/
│   │   ├── security.py          # bcrypt hashing, JWT creation/verification
│   │   ├── dependencies.py      # get_current_user() dependency
│   │   └── permissions.py       # get_project_role(), require_maintainer()
│   └── db/
│       ├── base.py              # Declarative Base
│       └── session.py           # Engine + SessionLocal
├── .env
└── requirements.txt
```

### 3.2 Frontend

```
frontend/
├── src/
│   ├── App.jsx                  # Entire frontend (single-file architecture)
│   └── main.jsx                 # React DOM entry point
├── index.html
├── vite.config.js
└── package.json
```

> **Note:** The frontend uses a single-file architecture to keep the codebase lean and immediately reviewable. All components, styles, context, and API calls live in `App.jsx`.

---

## 4. Setup & Installation

### 4.1 Backend

**Step 1 — Create a virtual environment**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Create `.env` file**
```env
DATABASE_URL=sqlite:///./issuehub.db
SECRET_KEY=your-secret-key-change-this-in-production
CORS_ORIGINS=http://localhost:5173
```

**Step 4 — Run the server**
```bash
uvicorn app.main:app --reload --port 8000
```

> Tables are created automatically on first startup via SQLAlchemy's `create_all()`. No migrations needed for development.

---

### 4.2 Frontend

**Step 1 — Create the Vite project** *(first time only)*
```bash
npm create vite@latest issuehub-frontend -- --template react
cd issuehub-frontend
npm install
```

**Step 2 — Replace `src/App.jsx`**  
Delete the default `src/App.jsx` and `src/App.css`, then paste the provided `App.jsx`.

**Step 3 — Clean up `src/main.jsx`**
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode><App /></React.StrictMode>
)
```

**Step 4 — Start the dev server**
```bash
npm run dev
```

> Frontend runs on `http://localhost:5173`, backend on `http://localhost:8000`. Both must be running simultaneously.

---

## 5. API Reference

**Base URL:** `http://localhost:8000/api`

All protected endpoints require:
```
Authorization: Bearer <JWT_TOKEN>
```

---

### 5.1 Auth APIs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/signup` | ❌ | Register a new user account |
| `POST` | `/auth/login` | ❌ | Authenticate user, returns JWT access token |

**Signup request body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "123456"
}
```

**Login request body:**
```json
{
  "email": "john@example.com",
  "password": "123456"
}
```

**Login response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 5.2 Project APIs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/projects/` | ✅ | Create a new project. Creator becomes maintainer automatically |
| `GET` | `/projects/` | ✅ | List all projects where the current user is a member |
| `POST` | `/projects/{project_id}/members` | ✅ | Add a user to a project (maintainer only) |

**Create project request body:**
```json
{
  "name": "Bug Tracker",
  "key": "BUG",
  "description": "Track all bugs"
}
```

> The `key` field is a short unique identifier for the project (e.g. `BUG`, `FE`, `API`). Must be unique across all projects.

---

### 5.3 Issue APIs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/issues/project/{project_id}` | ✅ | Create a new issue inside a project |
| `GET` | `/issues/project/{project_id}` | ✅ | List issues with optional filters + pagination |
| `GET` | `/issues/{issue_id}` | ✅ | Fetch full details of a single issue |
| `PATCH` | `/issues/{issue_id}` | ✅ | Update issue fields (maintainer or reporter only) |
| `DELETE` | `/issues/{issue_id}` | ✅ | Delete an issue (maintainer or reporter only) |

**Create issue request body:**
```json
{
  "title": "Login bug",
  "description": "User cannot log in on mobile",
  "priority": "high"
}
```

**Update issue request body** *(all fields optional)*:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "medium"
}
```

**Valid `status` values:** `open` · `in_progress` · `closed`

**Valid `priority` values:** `low` · `medium` · `high`

**List issues — query parameters:**
```
GET /issues/project/1?status=open&priority=high&skip=0&limit=10
```

---

### 5.4 Comment APIs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/comments/issue/{issue_id}` | ✅ | Add a comment to an issue (project members only) |
| `GET` | `/comments/issue/{issue_id}` | ✅ | List all comments on an issue |

**Add comment request body:**
```json
{
  "body": "This bug is reproducible on Chrome v120"
}
```

---

## 6. Authentication & Security

### 6.1 JWT Flow

IssueHub uses **stateless JWT authentication**. On successful login, the server signs a token containing the user's ID using a secret key. The client stores this token and sends it in every protected request.

- **Token type:** Bearer
- **Algorithm:** HS256
- **Payload contains:** user ID (`sub`), expiry (`exp`)
- **Verification:** `get_current_user()` dependency injects the authenticated user into every protected route

### 6.2 Password Security

- Passwords are **never stored in plain text**
- `bcrypt` hashing is applied via `passlib` before writing to the database
- `verify_password()` uses bcrypt's constant-time comparison to prevent timing attacks

### 6.3 Role-Based Access Control (RBAC)

Every project member has one of two roles: `maintainer` or `member`. The `reporter_id` on an issue grants the creator special write permissions regardless of their role.

| Action | Maintainer | Reporter | Member |
|--------|-----------|---------|--------|
| Create Issue | ✅ | ✅ | ✅ |
| View Issues | ✅ | ✅ | ✅ |
| Update Issue | ✅ | ✅ (own) | ❌ |
| Delete Issue | ✅ | ✅ (own) | ❌ |
| Add Comment | ✅ | ✅ | ✅ |
| View Comments | ✅ | ✅ | ✅ |
| Add Members | ✅ | ❌ | ❌ |

---

## 7. Database Design

### 7.1 Tables

| Table | Key Columns | Purpose |
|-------|------------|---------|
| `users` | `id`, `name`, `email`, `password_hash` | Stores registered users and hashed credentials |
| `projects` | `id`, `name`, `key`, `description` | Tracks all created projects with unique keys |
| `project_members` | `project_id`, `user_id`, `role` | Links users to projects with maintainer/member roles |
| `issues` | `id`, `project_id`, `reporter_id`, `title`, `status`, `priority` | Core issue tracking with status and priority |
| `comments` | `id`, `issue_id`, `author_id`, `body` | Discussion thread attached to each issue |

### 7.2 Relationships

```
users ──< project_members >── projects
                                  │
                               issues ──< comments
                                  │
                              reporter_id → users
                                  
comments.author_id → users
```

- A `User` can belong to many `Projects` through `project_members` (many-to-many)
- A `Project` has many `Issues`; each `Issue` belongs to one `Project`
- An `Issue` has many `Comments`; each `Comment` belongs to one `Issue`
- Each `Issue` has a `reporter_id` linking back to the `User` who created it
- Each `Comment` has an `author_id` linking back to the `User` who wrote it

---

## 8. Frontend Architecture

### 8.1 Component Hierarchy

```
App                        → root, manages auth state + page routing
├── AuthPage               → login / signup forms
├── Sidebar                → navigation, user info, logout button
├── ProjectsPage           → grid of projects + create modal
│   └── Modal              → reusable modal wrapper
└── IssuesPage             → issue list + detail split panel
    ├── CreateIssueModal   → new issue form
    ├── EditIssueModal     → edit status/priority/title form
    └── Comment section    → inline comment list + post input
```

### 8.2 State Management

| State | Location | Description |
|-------|----------|-------------|
| `token` | `App` + localStorage | JWT stored across sessions |
| `userEmail` | `App` + localStorage | Display name in sidebar |
| `page` | `App` | String-based routing: `'projects'` or `'issues'` |
| `project` | `App` | Currently selected project object |
| `filters` | `IssuesPage` | Status/priority filters, triggers API re-fetch |
| `selected` | `IssuesPage` | Open issue, controls split-panel layout |

### 8.3 Key Design Decisions

- **No router library** — simple string-based page state keeps dependencies minimal
- **React Context** — `AuthContext` shares JWT token across components without prop drilling
- **Custom Toast system** — lightweight notification system with no library dependency
- **Auto re-fetch on filter change** — `useEffect` watches filter state and calls the API automatically
- **Split-panel layout** — clicking an issue opens detail + comments inline without a page change

---

## 9. Error Handling

### 9.1 Backend

| Error | Handler | Response |
|-------|---------|----------|
| Validation failure | `RequestValidationError` handler | `422` with safe, human-readable details (bytes decoded to avoid JSON crash) |
| Bad request / not found | `HTTPException` raised explicitly | `400` / `401` / `403` / `404` with descriptive message |
| Unexpected crash | General `Exception` handler | `500` with generic message, full traceback logged to console |
| Trailing slash redirect | `redirect_slashes=False` on app | Prevents `307` redirect that strips `POST` body data |

### 9.2 Frontend

- All API calls wrapped in `try/catch` — errors surface as toast notifications
- Form validation checks required fields before submitting
- Inline error messages displayed inside modals using styled `error-msg` div
- Loading spinners shown on buttons and page areas during fetch operations

---

## 10. Running the Application

### Start Both Servers

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd issuehub-frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

- Swagger UI (interactive API docs): **http://localhost:8000/docs**
- ReDoc (clean API docs): **http://localhost:8000/redoc**

### Manual Testing Flow

1. Register two users via the signup form
2. Log in as User 1, create a project with a unique key
3. Create issues with different priorities and statuses
4. Edit issue status: `open` → `in_progress` → `closed`
5. Add comments to issues
6. Log in as User 2 — verify they cannot see User 1's project
7. As User 1 (maintainer), add User 2 as a member via `POST /projects/{id}/members`
8. Log in as User 2 — verify they can now see the project and create issues

---

## 11. Key Design Choices

### Why FastAPI?
FastAPI was chosen for its automatic OpenAPI documentation generation, native Pydantic v2 integration, and Python type hint system. The interactive `/docs` endpoint makes manual API testing straightforward without needing an external tool like Postman.

### Why JWT over Sessions?
JWT tokens are stateless — the server does not store session data. This makes the backend horizontally scalable and eliminates the need for a session store. The trade-off is that tokens cannot be invalidated before expiry, which was intentionally omitted as out of scope.

### Why SQLAlchemy ORM?
SQLAlchemy provides a database-agnostic ORM layer, allowing the app to run on SQLite during development and PostgreSQL in production by changing only the `DATABASE_URL` environment variable. The models serve as a single source of truth for the schema.

### Why Single-File Frontend?
The single `App.jsx` architecture keeps the codebase simple and immediately reviewable. In a production app, components would be split into feature folders (`auth/`, `projects/`, `issues/`, `shared/`). The architecture is already structured to support that refactor with minimal changes.

---

## 12. Limitations & Future Improvements

### Current Limitations

- JWT tokens cannot be revoked (no logout blacklist)
- No file attachment support for issues
- No email notifications for issue assignments or comments
- No pagination UI in the frontend (API supports `skip`/`limit`)
- No issue assignment to specific members (only reporter tracking)

### Future Improvements

- [ ] Refresh token mechanism for longer sessions
- [ ] WebSocket support for real-time comment notifications
- [ ] Issue assignment — assign to specific project members
- [ ] Labels and milestones — categorize issues beyond status and priority
- [ ] Activity log — audit trail of all changes to an issue
- [ ] Docker Compose setup for one-command deployment
- [ ] Unit and integration tests (pytest for backend, Vitest for frontend)

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [React Documentation](https://react.dev)
- [Pydantic v2 Documentation](https://docs.pydantic.dev)
- [python-jose JWT](https://python-jose.readthedocs.io)
- [Passlib (bcrypt)](https://passlib.readthedocs.io)
- [Vite Documentation](https://vitejs.dev)

---

*IssueHub — Assignment submission. All code written from scratch.*