"""
Human handover API routes.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import HumanHandover, Conversation, AdminUser
from ..schemas import (
    HandoverCreate, HandoverOut, HandoverAdminOut, HandoverUpdate, PaginatedResponse
)
from ..security import get_current_admin

router = APIRouter(prefix="/api/handovers", tags=["handovers"])

_VALID_STATUSES = {"pending", "in_progress", "resolved", "cancelled"}


@router.post("", status_code=201, response_model=HandoverOut)
def create_handover(payload: HandoverCreate, db: Session = Depends(get_db)):
    """
    Request human assistance. Records a handover request.
    Does NOT notify centre staff automatically in this prototype.
    """
    conversation = None
    if payload.session_token:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.session_token == payload.session_token)
            .first()
        )
        if conversation:
            conversation.status = "human_handover"

    handover = HumanHandover(
        conversation_id=conversation.id if conversation else None,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        preferred_contact_method=payload.preferred_contact_method,
        status="pending",
    )
    db.add(handover)
    db.commit()
    db.refresh(handover)
    return HandoverOut.model_validate(handover)


@router.get("", response_model=PaginatedResponse)
def list_handovers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: list all handover requests."""
    q = db.query(HumanHandover)
    if status:
        q = q.filter(HumanHandover.status == status)
    total = q.count()
    items = (
        q.order_by(HumanHandover.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[HandoverAdminOut.model_validate(h) for h in items],
    )


@router.patch("/{handover_id}", response_model=HandoverAdminOut)
def update_handover(
    handover_id: int,
    payload: HandoverUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: update handover status or notes."""
    h = db.get(HumanHandover, handover_id)
    if not h:
        raise HTTPException(404, "Handover not found.")
    if payload.status is not None:
        if payload.status not in _VALID_STATUSES:
            raise HTTPException(422, f"Status must be one of: {', '.join(_VALID_STATUSES)}")
        h.status = payload.status
    if payload.admin_notes is not None:
        h.admin_notes = payload.admin_notes
    db.commit()
    db.refresh(h)
    return HandoverAdminOut.model_validate(h)
