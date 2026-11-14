"""
SQLAlchemy 2.x ORM models for Future Vision Classes Support Chatbot.
All personal data fields are minimal and consent-tracked.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, Text, DateTime, ForeignKey, Boolean, Integer, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Admin / auth
# ---------------------------------------------------------------------------

class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# Conversations / messages
# ---------------------------------------------------------------------------

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(20), default="website")
    status: Mapped[str] = mapped_column(String(30), default="bot_active")
    customer_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    # Phone stored for follow-up only; never returned in chat responses
    customer_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    consent_to_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at"
    )
    handovers: Mapped[list["HumanHandover"]] = relationship(back_populates="conversation")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="conversation")

    __table_args__ = (
        Index("ix_conv_status", "status"),
        Index("ix_conv_created", "created_at"),
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    sender: Mapped[str] = mapped_column(String(20))          # "customer" | "bot"
    body: Mapped[str] = mapped_column(Text)
    intent: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


# ---------------------------------------------------------------------------
# FAQs
# ---------------------------------------------------------------------------

class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    faq_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str] = mapped_column(String(60), default="unverified")
    verification_status: Mapped[str] = mapped_column(String(30), default="pending")
    last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_faq_category", "category"),
        Index("ix_faq_published", "is_published"),
    )


# ---------------------------------------------------------------------------
# Enquiries (admission / callback)
# ---------------------------------------------------------------------------

class Enquiry(Base):
    __tablename__ = "enquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    course_interest: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    preferred_callback_time: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consent_to_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(30), default="new")
    # Admin internal notes
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_enquiry_status", "status"),
        Index("ix_enquiry_created", "created_at"),
    )


# ---------------------------------------------------------------------------
# Demo / counselling requests
# ---------------------------------------------------------------------------

class DemoRequest(Base):
    __tablename__ = "demo_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    course_interest: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    preferred_date: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    preferred_time: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consent_to_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(30), default="requested")
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_demo_status", "status"),
        Index("ix_demo_created", "created_at"),
    )


# ---------------------------------------------------------------------------
# Complaint tickets
# ---------------------------------------------------------------------------

class ComplaintTicket(Base):
    __tablename__ = "complaint_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_ref: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    # Lookup token shared with customer — not guessable
    lookup_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    category: Mapped[str] = mapped_column(String(60), default="general")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[str] = mapped_column(String(30), default="open")
    assigned_agent: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        Index("ix_ticket_status", "status"),
        Index("ix_ticket_created", "created_at"),
    )


# ---------------------------------------------------------------------------
# Human handover
# ---------------------------------------------------------------------------

class HumanHandover(Base):
    __tablename__ = "human_handovers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conversations.id"), nullable=True, index=True
    )
    customer_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    preferred_contact_method: Mapped[str] = mapped_column(String(30), default="phone")
    conversation_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_intent: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    conversation: Mapped[Optional["Conversation"]] = relationship(back_populates="handovers")

    __table_args__ = (
        Index("ix_handover_status", "status"),
        Index("ix_handover_created", "created_at"),
    )


# ---------------------------------------------------------------------------
# User feedback
# ---------------------------------------------------------------------------

class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conversations.id"), nullable=True
    )
    message_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chat_messages.id"), nullable=True
    )
    rating: Mapped[str] = mapped_column(String(10))  # "helpful" | "not_helpful"
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unanswered_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    conversation: Mapped[Optional["Conversation"]] = relationship(back_populates="feedback")


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_username: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    __table_args__ = (
        Index("ix_audit_created", "created_at"),
        Index("ix_audit_admin", "admin_username"),
    )
