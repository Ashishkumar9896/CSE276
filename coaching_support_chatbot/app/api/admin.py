"""
Admin authentication and dashboard API routes.
"""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    AdminUser, Conversation, Enquiry, DemoRequest,
    ComplaintTicket, HumanHandover, Feedback, FAQ
)
from ..schemas import LoginRequest, TokenResponse, DashboardStats
from ..security import hash_password, verify_password, create_access_token, get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Admin login — returns a JWT access token."""
    admin = (
        db.query(AdminUser)
        .filter(AdminUser.username == payload.username, AdminUser.is_active == True)
        .first()
    )
    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    admin.last_login_at = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token({"sub": admin.username})
    return TokenResponse(access_token=token)


@router.get("/auth/me")
def get_me(admin: AdminUser = Depends(get_current_admin)):
    """Return current admin user info."""
    return {"username": admin.username, "is_active": admin.is_active}


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin dashboard: aggregate statistics."""
    return DashboardStats(
        total_conversations=db.query(Conversation).count(),
        open_enquiries=db.query(Enquiry).filter(
            Enquiry.status.in_(["new", "follow_up"])
        ).count(),
        open_complaints=db.query(ComplaintTicket).filter(
            ComplaintTicket.status.in_(["open", "in_progress", "awaiting_response"])
        ).count(),
        pending_demo_requests=db.query(DemoRequest).filter(
            DemoRequest.status == "requested"
        ).count(),
        pending_handovers=db.query(HumanHandover).filter(
            HumanHandover.status == "pending"
        ).count(),
        published_faqs=db.query(FAQ).filter(FAQ.is_published == True).count(),
        helpful_feedback=db.query(Feedback).filter(Feedback.rating == "helpful").count(),
        not_helpful_feedback=db.query(Feedback).filter(Feedback.rating == "not_helpful").count(),
    )
