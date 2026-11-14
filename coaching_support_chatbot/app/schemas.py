"""
Pydantic v2 schemas for request/response validation.
"""
from __future__ import annotations
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_INDIAN_PHONE_RE = re.compile(r"^\+?[6-9]\d{9}$")


def _validate_indian_phone(v: str) -> str:
    cleaned = v.strip().replace(" ", "").replace("-", "")
    if not _INDIAN_PHONE_RE.match(cleaned):
        raise ValueError(
            "Please enter a valid 10-digit Indian mobile number (starting with 6-9)."
        )
    return cleaned


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_token: Optional[str] = Field(default=None, max_length=64)
    # Optional identity for follow-up; never required
    customer_name: Optional[str] = Field(default=None, max_length=120)
    customer_phone: Optional[str] = Field(default=None, max_length=30)
    consent_to_contact: bool = False

    @field_validator("customer_phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        return _validate_indian_phone(v)


class SuggestedAction(BaseModel):
    label: str
    message: str


class ChatResponse(BaseModel):
    session_token: str
    reply: str
    intent: str
    handover: bool = False
    suggested_actions: list[SuggestedAction] = []


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sender: str
    body: str
    intent: Optional[str]
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_token: str
    status: str
    created_at: datetime
    messages: list[MessageOut] = []


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

class FAQCreate(BaseModel):
    faq_code: str = Field(min_length=1, max_length=20)
    category: str = Field(min_length=1, max_length=60)
    question: str = Field(min_length=5, max_length=500)
    answer: str = Field(min_length=5, max_length=3000)
    source_url: Optional[str] = Field(default=None, max_length=500)
    source_type: str = Field(default="unverified", max_length=60)
    verification_status: str = Field(default="pending", max_length=30)
    is_published: bool = False
    internal_notes: Optional[str] = Field(default=None, max_length=2000)


class FAQUpdate(BaseModel):
    category: Optional[str] = Field(default=None, max_length=60)
    question: Optional[str] = Field(default=None, max_length=500)
    answer: Optional[str] = Field(default=None, max_length=3000)
    source_url: Optional[str] = Field(default=None, max_length=500)
    source_type: Optional[str] = Field(default=None, max_length=60)
    verification_status: Optional[str] = Field(default=None, max_length=30)
    is_published: Optional[bool] = None
    internal_notes: Optional[str] = Field(default=None, max_length=2000)


class FAQOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    faq_code: str
    category: str
    question: str
    answer: str
    source_url: Optional[str]
    source_type: str
    verification_status: str
    last_checked: Optional[datetime]
    is_published: bool
    internal_notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class FAQPublicOut(BaseModel):
    """Only expose safe public fields."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    faq_code: str
    category: str
    question: str
    answer: str
    verification_status: str


# ---------------------------------------------------------------------------
# Enquiry
# ---------------------------------------------------------------------------

class EnquiryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=10, max_length=30)
    course_interest: Optional[str] = Field(default=None, max_length=120)
    preferred_callback_time: Optional[str] = Field(default=None, max_length=120)
    message: Optional[str] = Field(default=None, max_length=2000)
    consent_to_contact: bool

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return _validate_indian_phone(v)

    @field_validator("consent_to_contact")
    @classmethod
    def must_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("You must consent to be contacted to submit an enquiry.")
        return v


class EnquiryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    phone: str
    course_interest: Optional[str]
    preferred_callback_time: Optional[str]
    message: Optional[str]
    consent_to_contact: bool
    status: str
    created_at: datetime
    updated_at: datetime


class EnquiryAdminOut(EnquiryOut):
    admin_notes: Optional[str]


class EnquiryUpdate(BaseModel):
    status: Optional[str] = Field(default=None, max_length=30)
    admin_notes: Optional[str] = Field(default=None, max_length=2000)


# ---------------------------------------------------------------------------
# Demo request
# ---------------------------------------------------------------------------

class DemoRequestCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=10, max_length=30)
    course_interest: Optional[str] = Field(default=None, max_length=120)
    preferred_date: Optional[str] = Field(default=None, max_length=30)
    preferred_time: Optional[str] = Field(default=None, max_length=60)
    message: Optional[str] = Field(default=None, max_length=2000)
    consent_to_contact: bool

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return _validate_indian_phone(v)

    @field_validator("consent_to_contact")
    @classmethod
    def must_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("You must consent to be contacted to submit a demo request.")
        return v


class DemoRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    phone: str
    course_interest: Optional[str]
    preferred_date: Optional[str]
    preferred_time: Optional[str]
    message: Optional[str]
    consent_to_contact: bool
    status: str
    created_at: datetime
    updated_at: datetime


class DemoRequestAdminOut(DemoRequestOut):
    admin_notes: Optional[str]


class DemoRequestUpdate(BaseModel):
    status: Optional[str] = Field(default=None, max_length=30)
    admin_notes: Optional[str] = Field(default=None, max_length=2000)


# ---------------------------------------------------------------------------
# Complaint ticket
# ---------------------------------------------------------------------------

class ComplaintCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    customer_phone: Optional[str] = Field(default=None, max_length=30)
    category: str = Field(default="general", max_length=60)
    description: str = Field(min_length=10, max_length=3000)
    priority: str = Field(default="normal", max_length=20)

    @field_validator("customer_phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        return _validate_indian_phone(v)


class ComplaintStatusLookup(BaseModel):
    ticket_ref: str = Field(min_length=1, max_length=20)
    lookup_token: str = Field(min_length=10, max_length=64)


class ComplaintPublicOut(BaseModel):
    """Public view — no other customers' data."""
    ticket_ref: str
    status: str
    created_at: datetime
    category: str


class ComplaintAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_ref: str
    customer_name: str
    customer_phone: Optional[str]
    category: str
    description: str
    priority: str
    status: str
    assigned_agent: Optional[str]
    resolution_notes: Optional[str]
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class ComplaintUpdate(BaseModel):
    status: Optional[str] = Field(default=None, max_length=30)
    assigned_agent: Optional[str] = Field(default=None, max_length=120)
    resolution_notes: Optional[str] = Field(default=None, max_length=3000)
    admin_notes: Optional[str] = Field(default=None, max_length=2000)


# ---------------------------------------------------------------------------
# Human handover
# ---------------------------------------------------------------------------

class HandoverCreate(BaseModel):
    session_token: Optional[str] = Field(default=None, max_length=64)
    customer_name: Optional[str] = Field(default=None, max_length=120)
    customer_phone: Optional[str] = Field(default=None, max_length=30)
    preferred_contact_method: str = Field(default="phone", max_length=30)

    @field_validator("customer_phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        return _validate_indian_phone(v)


class HandoverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    created_at: datetime


class HandoverAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_name: Optional[str]
    customer_phone: Optional[str]
    preferred_contact_method: str
    conversation_summary: Optional[str]
    last_intent: Optional[str]
    status: str
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class HandoverUpdate(BaseModel):
    status: Optional[str] = Field(default=None, max_length=30)
    admin_notes: Optional[str] = Field(default=None, max_length=2000)


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    session_token: Optional[str] = Field(default=None, max_length=64)
    message_id: Optional[int] = None
    rating: str = Field(pattern="^(helpful|not_helpful)$")
    comment: Optional[str] = Field(default=None, max_length=2000)
    unanswered_question: Optional[str] = Field(default=None, max_length=1000)


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rating: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Admin dashboard
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    total_conversations: int
    open_enquiries: int
    open_complaints: int
    pending_demo_requests: int
    pending_handovers: int
    published_faqs: int
    helpful_feedback: int
    not_helpful_feedback: int


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list
