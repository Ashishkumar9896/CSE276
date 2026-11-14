"""
Complaint ticket API routes.
Tickets are accessible via a lookup_token to prevent guessable ID enumeration.
"""
from __future__ import annotations
import secrets
import string
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ComplaintTicket, AdminUser
from ..schemas import (
    ComplaintCreate, ComplaintStatusLookup, ComplaintPublicOut,
    ComplaintAdminOut, ComplaintUpdate, PaginatedResponse
)
from ..security import get_current_admin

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

_VALID_STATUSES = {"open", "in_progress", "awaiting_response", "resolved", "closed"}
_VALID_PRIORITIES = {"low", "normal", "high", "urgent"}
_VALID_CATEGORIES = {
    "general", "billing", "teaching_quality", "behaviour",
    "facilities", "scheduling", "refund", "other"
}


def _gen_ticket_ref() -> str:
    """Generate a readable ticket reference like TKT-20241028-AB3X."""
    suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"TKT-{date_str}-{suffix}"


@router.post("", status_code=201)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    """Submit a complaint or support ticket."""
    ticket_ref = _gen_ticket_ref()
    lookup_token = secrets.token_urlsafe(32)

    if payload.category not in _VALID_CATEGORIES:
        raise HTTPException(422, f"Category must be one of: {', '.join(_VALID_CATEGORIES)}")
    if payload.priority not in _VALID_PRIORITIES:
        raise HTTPException(422, f"Priority must be one of: {', '.join(_VALID_PRIORITIES)}")

    ticket = ComplaintTicket(
        ticket_ref=ticket_ref,
        lookup_token=lookup_token,
        **payload.model_dump(),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "ticket_ref": ticket_ref,
        "lookup_token": lookup_token,
        "status": ticket.status,
        "message": (
            "Your complaint has been registered. "
            "Save your ticket reference and lookup token — you'll need both to check status. "
            "Do not share your lookup token with others."
        ),
    }


@router.post("/lookup", response_model=ComplaintPublicOut)
def lookup_ticket(payload: ComplaintStatusLookup, db: Session = Depends(get_db)):
    """
    Public ticket status lookup.
    Requires BOTH ticket_ref and lookup_token — prevents guessable ID attacks.
    """
    ticket = (
        db.query(ComplaintTicket)
        .filter(
            ComplaintTicket.ticket_ref == payload.ticket_ref,
            ComplaintTicket.lookup_token == payload.lookup_token,
        )
        .first()
    )
    if not ticket:
        raise HTTPException(
            404,
            "No ticket found with those credentials. Check your reference and token."
        )
    return ComplaintPublicOut(
        ticket_ref=ticket.ticket_ref,
        status=ticket.status,
        created_at=ticket.created_at,
        category=ticket.category,
    )


@router.get("", response_model=PaginatedResponse)
def list_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: list all complaint tickets."""
    q = db.query(ComplaintTicket)
    if status:
        q = q.filter(ComplaintTicket.status == status)
    if priority:
        q = q.filter(ComplaintTicket.priority == priority)
    total = q.count()
    items = (
        q.order_by(ComplaintTicket.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ComplaintAdminOut.model_validate(t) for t in items],
    )


@router.get("/{ticket_id}", response_model=ComplaintAdminOut)
def get_complaint(
    ticket_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: get a single complaint ticket."""
    t = db.get(ComplaintTicket, ticket_id)
    if not t:
        raise HTTPException(404, "Ticket not found.")
    return ComplaintAdminOut.model_validate(t)


@router.patch("/{ticket_id}", response_model=ComplaintAdminOut)
def update_complaint(
    ticket_id: int,
    payload: ComplaintUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: update complaint status, assignment, or resolution."""
    t = db.get(ComplaintTicket, ticket_id)
    if not t:
        raise HTTPException(404, "Ticket not found.")
    if payload.status is not None:
        if payload.status not in _VALID_STATUSES:
            raise HTTPException(422, f"Status must be one of: {', '.join(_VALID_STATUSES)}")
        t.status = payload.status
    if payload.assigned_agent is not None:
        t.assigned_agent = payload.assigned_agent
    if payload.resolution_notes is not None:
        t.resolution_notes = payload.resolution_notes
    if payload.admin_notes is not None:
        t.admin_notes = payload.admin_notes
    db.commit()
    db.refresh(t)
    return ComplaintAdminOut.model_validate(t)
