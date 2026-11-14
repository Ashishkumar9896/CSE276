"""
Feedback API routes.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Feedback, Conversation, ChatMessage
from ..schemas import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", status_code=201, response_model=FeedbackOut)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit helpful/not-helpful feedback for a bot response."""
    conversation = None
    if payload.session_token:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.session_token == payload.session_token)
            .first()
        )

    fb = Feedback(
        conversation_id=conversation.id if conversation else None,
        message_id=payload.message_id,
        rating=payload.rating,
        comment=payload.comment,
        unanswered_question=payload.unanswered_question,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return FeedbackOut.model_validate(fb)
