"""
Chat API routes.
"""
from __future__ import annotations
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Conversation, ChatMessage, FAQ, HumanHandover
from ..schemas import ChatRequest, ChatResponse, SuggestedAction as SuggestedActionSchema
from ..chatbot import answer, BotResult

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _get_published_faqs(db: Session) -> list[dict]:
    faqs = db.query(FAQ).filter(FAQ.is_published == True).all()
    return [
        {
            "id": f.id,
            "faq_code": f.faq_code,
            "category": f.category,
            "question": f.question,
            "answer": f.answer,
            "source_type": f.source_type,
            "verification_status": f.verification_status,
        }
        for f in faqs
    ]


@router.post("", response_model=ChatResponse)
def send_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a chat message and receive a bot reply.
    Creates or continues a conversation session identified by session_token.
    """
    # Resolve or create conversation
    conversation = None
    if payload.session_token:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.session_token == payload.session_token)
            .first()
        )

    if conversation is None:
        session_token = secrets.token_urlsafe(32)
        conversation = Conversation(
            session_token=session_token,
            channel="website",
            customer_name=payload.customer_name,
            customer_phone=payload.customer_phone,
            consent_to_contact=payload.consent_to_contact,
        )
        db.add(conversation)
        db.flush()
    else:
        # Update contact info if provided in this message
        if payload.customer_name and not conversation.customer_name:
            conversation.customer_name = payload.customer_name
        if payload.customer_phone and not conversation.customer_phone:
            conversation.customer_phone = payload.customer_phone
        if payload.consent_to_contact:
            conversation.consent_to_contact = True

    # Existing handover conversation — still record and notify
    if conversation.status == "human_handover":
        db.add(ChatMessage(
            conversation_id=conversation.id,
            sender="customer",
            body=payload.message,
            intent="handover",
        ))
        db.commit()
        return ChatResponse(
            session_token=conversation.session_token,
            reply=(
                "Your conversation is waiting for staff follow-up.\n\n"
                "Please contact Future Vision Classes directly if your matter is urgent."
            ),
            intent="handover",
            handover=True,
            suggested_actions=[],
        )

    # Save customer message
    db.add(ChatMessage(
        conversation_id=conversation.id,
        sender="customer",
        body=payload.message,
    ))

    # Generate response
    published_faqs = _get_published_faqs(db)

    # Get recent conversation history for LLM context
    recent_history = []
    if conversation:
        past_msgs = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(6)
            .all()
        )
        recent_history = [
            {"sender": m.sender, "body": m.body}
            for m in reversed(past_msgs)
        ]

    result: BotResult = answer(
        payload.message,
        published_faqs=published_faqs,
        conversation_history=recent_history,
        use_llm=True,
    )

    # Save bot reply
    db.add(ChatMessage(
        conversation_id=conversation.id,
        sender="bot",
        body=result.reply,
        intent=result.intent,
    ))

    # Handle handover
    if result.handover:
        conversation.status = "human_handover"
        # Create handover record
        summary_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation.id)
            .order_by(ChatMessage.created_at)
            .all()
        )
        summary = " | ".join(
            f"{m.sender}: {m.body[:100]}" for m in summary_messages[-6:]
        )
        handover = HumanHandover(
            conversation_id=conversation.id,
            customer_name=conversation.customer_name,
            customer_phone=conversation.customer_phone,
            preferred_contact_method="phone" if conversation.customer_phone else "callback",
            conversation_summary=summary,
            last_intent=result.intent,
            status="pending",
        )
        db.add(handover)

    db.commit()

    return ChatResponse(
        session_token=conversation.session_token,
        reply=result.reply,
        intent=result.intent,
        handover=result.handover,
        suggested_actions=[
            SuggestedActionSchema(label=a.label, message=a.message)
            for a in result.suggested_actions
        ],
    )


@router.get("/history/{session_token}")
def get_history(session_token: str, db: Session = Depends(get_db)):
    """Return chat history for a session. Session token must be known by the caller."""
    conv = (
        db.query(Conversation)
        .filter(Conversation.session_token == session_token)
        .first()
    )
    if not conv:
        raise HTTPException(404, "Session not found.")
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conv.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return {
        "session_token": session_token,
        "status": conv.status,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender,
                "body": m.body,
                "intent": m.intent,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }
