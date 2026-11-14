"""
FAQ API routes — public search and admin management.
"""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FAQ, AdminUser
from ..schemas import (
    FAQCreate, FAQUpdate, FAQOut, FAQPublicOut, PaginatedResponse
)
from ..security import get_current_admin

router = APIRouter(prefix="/api/faqs", tags=["faqs"])


@router.get("/search")
def search_faqs(
    q: str = Query(min_length=2, max_length=200),
    db: Session = Depends(get_db),
):
    """
    Public FAQ search — returns only published FAQs.
    Searches question and answer text.
    """
    query_words = q.strip().split()
    results = []

    for word in query_words[:5]:  # Limit to 5 terms
        faqs = (
            db.query(FAQ)
            .filter(
                FAQ.is_published == True,
                or_(
                    FAQ.question.ilike(f"%{word}%"),
                    FAQ.answer.ilike(f"%{word}%"),
                    FAQ.category.ilike(f"%{word}%"),
                ),
            )
            .all()
        )
        for f in faqs:
            if f not in results:
                results.append(f)

    return [FAQPublicOut.model_validate(f) for f in results[:10]]


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """Public: list available FAQ categories."""
    cats = (
        db.query(FAQ.category)
        .filter(FAQ.is_published == True)
        .distinct()
        .all()
    )
    return [c[0] for c in cats]


@router.get("", response_model=PaginatedResponse)
def list_faqs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    published_only: bool = Query(False),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: list all FAQs with filters."""
    q = db.query(FAQ)
    if category:
        q = q.filter(FAQ.category == category)
    if published_only:
        q = q.filter(FAQ.is_published == True)
    total = q.count()
    items = (
        q.order_by(FAQ.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[FAQOut.model_validate(f) for f in items],
    )


@router.post("", status_code=201, response_model=FAQOut)
def create_faq(
    payload: FAQCreate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: create a new FAQ entry."""
    if db.query(FAQ).filter(FAQ.faq_code == payload.faq_code).first():
        raise HTTPException(409, f"FAQ code '{payload.faq_code}' already exists.")
    faq = FAQ(**payload.model_dump())
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return FAQOut.model_validate(faq)


@router.get("/{faq_id}", response_model=FAQOut)
def get_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: get a single FAQ."""
    f = db.get(FAQ, faq_id)
    if not f:
        raise HTTPException(404, "FAQ not found.")
    return FAQOut.model_validate(f)


@router.patch("/{faq_id}", response_model=FAQOut)
def update_faq(
    faq_id: int,
    payload: FAQUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: update an FAQ entry."""
    f = db.get(FAQ, faq_id)
    if not f:
        raise HTTPException(404, "FAQ not found.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(f, field, value)
    f.last_checked = datetime.now(timezone.utc)
    db.commit()
    db.refresh(f)
    return FAQOut.model_validate(f)


@router.delete("/{faq_id}", status_code=204)
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin: delete an FAQ entry."""
    f = db.get(FAQ, faq_id)
    if not f:
        raise HTTPException(404, "FAQ not found.")
    db.delete(f)
    db.commit()
