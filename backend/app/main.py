from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.db.session import engine
from app.db.base import Base

# Import models so SQLAlchemy registers them
from app.models import user, project, project_member, issue, comment

# Import routers
from app.routers import auth, projects, issues, comments

load_dotenv()

APP_TITLE = "IssueHub API"
APP_VERSION = "1.0.0"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")


# ── Lifespan (Startup & Shutdown) ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting IssueHub API...")
    Base.metadata.create_all(bind=engine)
    yield
    print("Shutting down IssueHub API...")


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="IssueHub — a lightweight bug tracker API",
    lifespan=lifespan,
    redirect_slashes=False,  # prevents 307 redirects that strip POST body
)

# ── CORS Middleware ─────────────────────────────────────────────
origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Exception Handlers ───────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}

    # Safely convert all error values — bytes are not JSON serializable
    safe_details = []
    for err in errors:
        safe_err = {}
        for k, v in err.items():
            if isinstance(v, bytes):
                safe_err[k] = v.decode("utf-8", errors="replace")
            elif isinstance(v, (str, int, float, bool, list, dict, type(None))):
                safe_err[k] = v
            else:
                safe_err[k] = str(v)
        safe_details.append(safe_err)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": first_error.get("msg", "Validation failed"),
                "details": safe_details,
            }
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("Internal Error:", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred",
            }
        },
    )

# ── Include Routers ─────────────────────────────────────────────

app.include_router(auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(issues.router,   prefix="/api/issues",   tags=["Issues"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])

# ── Health Check ────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": APP_VERSION}