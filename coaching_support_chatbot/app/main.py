"""
Future Vision Classes — AI Customer Support Chatbot
Main FastAPI application entry point.

SCOPE: Website-only chatbot. No WhatsApp, SMS, or other messaging channels.
DISCLAIMER: Independent prototype. Not commissioned by Future Vision Classes.
"""
from __future__ import annotations
import logging
import pathlib
from dotenv import load_dotenv

# Ensure .env is always loaded into os.environ regardless of terminal settings
_env_path = pathlib.Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import get_settings
from .database import Base, engine
from .models import AdminUser, FAQ
from .security import hash_password
from .api import chat, enquiries, demos, complaints, faqs, feedback, admin, handovers

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
settings = get_settings()

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Official AI Academic Support and Admissions Assistant for Future Vision Classes, Sonipat.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# State for limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
origins = [o.strip() for o in settings.frontend_origin.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(chat.router)
app.include_router(enquiries.router)
app.include_router(demos.router)
app.include_router(complaints.router)
app.include_router(faqs.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(handovers.router)



# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    """
    Create tables (development convenience).
    For production: use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
    _seed_initial_data()
    logger.info("Application startup complete.")
    if settings.has_openai:
        logger.info("OpenAI key detected — LLM responses enabled.")
    else:
        logger.info("No OpenAI key — using rules-based engine only.")


def _seed_initial_data():
    """Create default admin user and seed FAQ data if not already present."""
    from .database import SessionLocal
    from datetime import datetime, timezone
    import csv
    import pathlib

    db = SessionLocal()
    try:
        # Create default admin if missing
        if not db.query(AdminUser).filter(AdminUser.username == "admin").first():
            admin = AdminUser(
                username="admin",
                hashed_password=hash_password("changeme123"),
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.warning(
                "Created default admin user: admin / changeme123 "
                "— CHANGE THIS PASSWORD before public deployment."
            )

        # Seed FAQs from CSV if table is empty
        if db.query(FAQ).count() == 0:
            faq_csv = pathlib.Path(__file__).resolve().parent.parent / "data" / "public_faq_dataset.csv"
            if faq_csv.exists():
                with faq_csv.open(encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader, 1):
                        faq_code = (row.get("faq_id") or row.get("\ufefffaq_id") or f"FVC{idx:03d}").strip()
                        faq = FAQ(
                            faq_code=faq_code,
                            category=row.get("category", "general").strip(),
                            question=row.get("question", "").strip(),
                            answer=row.get("answer", "").strip(),
                            source_url=row.get("source_url", "").strip() or None,
                            source_type=row.get("source_type", "unverified").strip(),
                            verification_status=row.get("status", "pending").strip(),
                            is_published=True,  # Publish seed FAQs
                            internal_notes=row.get("notes", "").strip() or None,
                        )
                        db.add(faq)
                db.commit()
                logger.info("Seeded FAQ data from CSV.")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"])
def health():
    """Health check endpoint for load balancers and deployment monitors."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "llm_enabled": settings.has_openai,
    }


# ---------------------------------------------------------------------------
# Root info
# ---------------------------------------------------------------------------
@app.get("/", tags=["info"])
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/health",
        "note": (
            "This is the API backend. "
            "The React frontend is served separately (see frontend/ directory)."
        ),
    }
