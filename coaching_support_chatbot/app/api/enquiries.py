"""
Enquiry (admission / callback) API routes.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Enquiry, AdminUser
from ..schemas import (
    EnquiryCreate, EnquiryOut, EnquiryAdminOut, EnquiryUpdate, PaginatedResponse
)
from ..security import get_current_admin

router = APIRouter(prefix="/api/enquiries", tags=["enquiries"])

_VALID_STATUSES = {"new", "contacted", "follow_up", "resolved", "closed"}


@router.post("", status_code=201)
def create_enquiry(payload: EnquiryCreate, db: Session = Depends(get_db)):
    """Submit an admission enquiry or callback request."""
    enquiry = Enquiry(**payload.model_dump())
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    return {
        "id": enquiry.id,
        "status": enquiry.status,
        "message": (
            "Your enquiry has been recorded. This is a prototype — "
            "a staff member will be asked to contact you if this system "
            "is connected to the centre's operations."
        ),
    }


@router.get("", response_model=PaginatedResponse)
def list_enquiries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: list all enquiries with pagination and optional status filter."""
    q = db.query(Enquiry)
    if status:
        q = q.filter(Enquiry.status == status)
    total = q.count()
    items = (
        q.order_by(Enquiry.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[EnquiryAdminOut.model_validate(e) for e in items],
    )


@router.get("/{enquiry_id}", response_model=EnquiryAdminOut)
def get_enquiry(
    enquiry_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: get a single enquiry by ID."""
    e = db.get(Enquiry, enquiry_id)
    if not e:
        raise HTTPException(404, "Enquiry not found.")
    return EnquiryAdminOut.model_validate(e)


@router.patch("/{enquiry_id}", response_model=EnquiryAdminOut)
def update_enquiry(
    enquiry_id: int,
    payload: EnquiryUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Admin: update enquiry status or notes."""
    e = db.get(Enquiry, enquiry_id)
    if not e:
        raise HTTPException(404, "Enquiry not found.")
    if payload.status is not None:
        if payload.status not in _VALID_STATUSES:
            raise HTTPException(422, f"Status must be one of: {', '.join(_VALID_STATUSES)}")
        e.status = payload.status
    if payload.admin_notes is not None:
        e.admin_notes = payload.admin_notes
    db.commit()
    db.refresh(e)
    return EnquiryAdminOut.model_validate(e)
