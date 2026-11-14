"""
Demo class / counselling request API routes.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DemoRequest, AdminUser
from ..schemas import (
    DemoRequestCreate, DemoRequestOut, DemoRequestAdminOut,
    DemoRequestUpdate, PaginatedResponse
)
from ..security import get_current_admin

router = APIRouter(prefix="/api/demo-requests", tags=["demo-requests"])

_VALID_STATUSES = {"requested", "confirmed", "cancelled", "completed"}


@router.post("", status_code=201)
def create_demo_request(payload: DemoRequestCreate, db: Session = Depends(get_db)):
    """Submit a demo class or counselling session request."""
    req = DemoRequest(**payload.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return {
        "id": req.id,
        "status": req.status,
        "message": (
            "Your demo class request has been recorded. "
            "This is a request, not a confirmed appointment. "
            "The centre's staff must confirm your preferred date and time. "
            "Please do not assume a slot is available until you receive confirmation."
        ),
    }


@router.get("", response_model=PaginatedResponse)
def list_demo_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: list all demo requests."""
    q = db.query(DemoRequest)
    if status:
        q = q.filter(DemoRequest.status == status)
    total = q.count()
    items = (
        q.order_by(DemoRequest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[DemoRequestAdminOut.model_validate(r) for r in items],
    )


@router.get("/{request_id}", response_model=DemoRequestAdminOut)
def get_demo_request(
    request_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: get a single demo request."""
    r = db.get(DemoRequest, request_id)
    if not r:
        raise HTTPException(404, "Demo request not found.")
    return DemoRequestAdminOut.model_validate(r)


@router.patch("/{request_id}", response_model=DemoRequestAdminOut)
def update_demo_request(
    request_id: int,
    payload: DemoRequestUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: update demo request status or notes."""
    r = db.get(DemoRequest, request_id)
    if not r:
        raise HTTPException(404, "Demo request not found.")
    if payload.status is not None:
        if payload.status not in _VALID_STATUSES:
            raise HTTPException(422, f"Status must be one of: {', '.join(_VALID_STATUSES)}")
        r.status = payload.status
    if payload.admin_notes is not None:
        r.admin_notes = payload.admin_notes
    db.commit()
    db.refresh(r)
    return DemoRequestAdminOut.model_validate(r)
