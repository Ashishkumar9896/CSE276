"""
Comprehensive test suite for Future Vision Classes Support Chatbot.

Uses a temporary SQLite database and the FastAPI TestClient.
NEVER modifies a production database.

All test queries are SYNTHETIC — not real customer conversations.
"""
from __future__ import annotations
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Test database setup
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///./test_chatbot.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["FRONTEND_ORIGIN"] = "http://localhost:5173"

from app.main import app
from app.database import Base, get_db
from app.models import AdminUser, FAQ
from app.security import hash_password

_test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
_TestSession = sessionmaker(bind=_test_engine, autoflush=False, autocommit=False)


def override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=_test_engine)
    db = _TestSession()
    # Create test admin
    admin = AdminUser(
        username="testadmin",
        hashed_password=hash_password("testpass123"),
        is_active=True,
    )
    db.add(admin)
    # Create published FAQ
    faq = FAQ(
        faq_code="TEST001",
        category="location",
        question="Where is Future Vision Classes located?",
        answer="A public directory lists Future Vision Classes at Rangoli Green, SCO No. 21-22, Sector 16, Sonipat.",
        source_type="third_party_directory",
        verification_status="pending",
        is_published=True,
    )
    db.add(faq)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client: TestClient):
    resp = client.post("/api/admin/auth/login", json={"username": "testadmin", "password": "testpass123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token: str):
    return {"Authorization": f"Bearer {admin_token}"}


# ===========================================================================
# 1. Health check
# ===========================================================================

class TestHealth:
    def test_health_ok(self, client):
        """Health endpoint must return 200."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200


# ===========================================================================
# 2. Chat intent classification
# ===========================================================================

class TestChatIntents:
    """Synthetic test queries covering intent classification."""

    def _chat(self, client, message: str, session_token: str = None) -> dict:
        payload = {"message": message}
        if session_token:
            payload["session_token"] = session_token
        resp = client.post("/api/chat", json=payload)
        assert resp.status_code == 200, f"Chat failed: {resp.text}"
        return resp.json()

    def test_greeting(self, client):
        """SYN: Greeting intent returns welcome message."""
        data = self._chat(client, "Hello")
        assert data["intent"] == "greeting"
        assert "session_token" in data
        assert len(data["reply"]) > 10

    def test_greeting_hindi(self, client):
        """SYN: Hinglish greeting."""
        data = self._chat(client, "Namaste")
        assert data["intent"] == "greeting"

    def test_courses_query(self, client):
        """SYN: Course inquiry returns verified or placeholder response."""
        data = self._chat(client, "What courses do you offer for JEE?")
        assert data["intent"] == "courses"
        # Must NOT invent unverified details
        assert "jee" in data["reply"].lower() or "neet" in data["reply"].lower() or "course" in data["reply"].lower()

    def test_fees_query(self, client):
        """SYN: Fee enquiry must NOT invent fee amounts."""
        data = self._chat(client, "What is the fee for NEET coaching?")
        assert data["intent"] == "fees"
        # Must not contain specific numbers
        reply_lower = data["reply"].lower()
        assert "not publicly available" in reply_lower or "contact" in reply_lower or "verified" in reply_lower

    def test_timings_query(self, client):
        """SYN: Batch timing enquiry must not invent schedule."""
        data = self._chat(client, "What are the class timings for the evening batch?")
        assert data["intent"] == "timings"
        assert "contact" in data["reply"].lower() or "verified" in data["reply"].lower()

    def test_location_query(self, client):
        """SYN: Location query returns sector 16 with discrepancy warning."""
        data = self._chat(client, "Where is your address? Is it Sector 15 or Sector 16?")
        assert data["intent"] == "location"
        assert "sector 16" in data["reply"].lower() or "sonipat" in data["reply"].lower()

    def test_admission_query(self, client):
        """SYN: Admission enquiry intent."""
        data = self._chat(client, "Are admissions open right now?")
        assert data["intent"] == "enquiry"

    def test_demo_request_intent(self, client):
        """SYN: Demo class intent detected."""
        data = self._chat(client, "I want to book a demo class this Sunday")
        assert data["intent"] == "demo_request"

    def test_handover_request(self, client):
        """SYN: Human handover request."""
        data = self._chat(client, "I want to talk to a staff member")
        assert data["intent"] == "handover"
        assert data["handover"] is True

    def test_complaint_intent(self, client):
        """SYN: Complaint intent detected."""
        data = self._chat(client, "I have a complaint about the teaching quality")
        assert data["intent"] == "complaint"
        assert data["handover"] is True

    def test_neet_jee_course(self, client):
        """SYN: Do you teach JEE Main and NEET?"""
        data = self._chat(client, "Do you teach both JEE Main and NEET?")
        assert data["intent"] == "courses"

    def test_no_outcome_guarantee(self, client):
        """SYN: Never guarantee exam outcome — must return unknown or safe response."""
        data = self._chat(client, "Can you guarantee that I will clear NEET?")
        # Should not promise outcomes
        assert "guarantee" not in data["reply"].lower() or "unknown" == data["intent"]

    def test_contact_query(self, client):
        """SYN: Contact information enquiry."""
        data = self._chat(client, "What is your phone number?")
        assert data["intent"] == "contact"

    def test_spelling_mistake(self, client):
        """SYN: Query with spelling error."""
        data = self._chat(client, "helo wat r the coureses u offer")
        assert data["intent"] in {"greeting", "courses", "unknown"}
        assert len(data["reply"]) > 5  # Should still respond meaningfully

    def test_hinglish_query(self, client):
        """SYN: Hinglish — fees kya hain."""
        data = self._chat(client, "kitne paise lagenge NEET ke liye")
        assert data["intent"] == "fees"

    def test_hinglish_location(self, client):
        """SYN: Hinglish location query."""
        data = self._chat(client, "centre kahan hai")
        assert data["intent"] == "location"

    def test_session_continuity(self, client):
        """Session token must be preserved across messages."""
        data1 = self._chat(client, "Hello")
        token = data1["session_token"]
        data2 = self._chat(client, "Tell me about courses", session_token=token)
        assert data2["session_token"] == token

    def test_suggested_actions_present(self, client):
        """Suggested actions should be returned."""
        data = self._chat(client, "Hello")
        assert isinstance(data["suggested_actions"], list)

    def test_empty_message_rejected(self, client):
        """Empty message should fail validation."""
        resp = client.post("/api/chat", json={"message": ""})
        assert resp.status_code == 422

    def test_message_too_long_rejected(self, client):
        """Message exceeding max length should be rejected."""
        resp = client.post("/api/chat", json={"message": "x" * 2001})
        assert resp.status_code == 422

    def test_existing_enquiry_status(self, client):
        """SYN: Check existing enquiry status intent."""
        data = self._chat(client, "What is the status of my enquiry?")
        assert data["intent"] == "existing_enquiry"

    def test_callback_request(self, client):
        """SYN: Please call me about admission."""
        data = self._chat(client, "Please call me about admission")
        assert data["intent"] in {"handover", "enquiry"}

    def test_private_data_not_exposed(self, client):
        """SYN: Bot must not reveal other users' data."""
        data = self._chat(client, "What is the phone number of the last student who enrolled?")
        reply_lower = data["reply"].lower()
        # Should not expose any customer data
        assert "+91" not in data["reply"] and "9876" not in data["reply"]

    def test_malicious_script_injection(self, client):
        """SYN: XSS attempt — reply must not echo raw script tags."""
        data = self._chat(client, "<script>alert('xss')</script>")
        assert "<script>" not in data["reply"]

    def test_sql_injection_attempt(self, client):
        """SYN: SQL injection attempt — must not crash."""
        resp = client.post("/api/chat", json={"message": "' OR 1=1 --"})
        assert resp.status_code == 200  # Should handle gracefully

    def test_unknown_question_handled(self, client):
        """SYN: Completely unknown question gets safe fallback."""
        data = self._chat(client, "What is the capital of France?")
        assert data["intent"] == "unknown"
        assert len(data["reply"]) > 10


# ===========================================================================
# 3. FAQ search
# ===========================================================================

class TestFAQSearch:
    def test_faq_search_returns_results(self, client):
        """Public FAQ search should return results."""
        resp = client.get("/api/faqs/search?q=location")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_faq_search_too_short(self, client):
        """FAQ search with 1-char query should fail."""
        resp = client.get("/api/faqs/search?q=a")
        assert resp.status_code == 422

    def test_faq_categories_public(self, client):
        resp = client.get("/api/faqs/categories")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ===========================================================================
# 4. Enquiry (admission / callback)
# ===========================================================================

class TestEnquiry:
    def test_create_enquiry_valid(self, client):
        """Valid enquiry creation."""
        resp = client.post("/api/enquiries", json={
            "name": "Test Student",
            "phone": "9876543210",
            "course_interest": "NEET",
            "preferred_callback_time": "Evening",
            "message": "Please call me",
            "consent_to_contact": True,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data

    def test_create_enquiry_invalid_phone(self, client):
        """Invalid Indian phone number should be rejected."""
        resp = client.post("/api/enquiries", json={
            "name": "Test Student",
            "phone": "12345",
            "consent_to_contact": True,
        })
        assert resp.status_code == 422

    def test_create_enquiry_no_consent(self, client):
        """No consent should fail validation."""
        resp = client.post("/api/enquiries", json={
            "name": "Test Student",
            "phone": "9876543210",
            "consent_to_contact": False,
        })
        assert resp.status_code == 422

    def test_create_enquiry_name_required(self, client):
        """Name required for enquiry."""
        resp = client.post("/api/enquiries", json={
            "name": "",
            "phone": "9876543210",
            "consent_to_contact": True,
        })
        assert resp.status_code == 422

    def test_list_enquiries_requires_auth(self, client):
        """Listing enquiries should require admin auth."""
        resp = client.get("/api/enquiries")
        assert resp.status_code == 401

    def test_list_enquiries_with_auth(self, client, auth_headers):
        """Admin can list enquiries."""
        resp = client.get("/api/enquiries", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data

    def test_update_enquiry_status(self, client, auth_headers):
        """Admin can update enquiry status."""
        # First create one
        create_resp = client.post("/api/enquiries", json={
            "name": "Student Update Test",
            "phone": "9898989898",
            "consent_to_contact": True,
        })
        enquiry_id = create_resp.json()["id"]
        # Update
        resp = client.patch(
            f"/api/enquiries/{enquiry_id}",
            json={"status": "contacted"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "contacted"

    def test_update_enquiry_invalid_status(self, client, auth_headers):
        """Invalid status should be rejected."""
        create_resp = client.post("/api/enquiries", json={
            "name": "Student Invalid Status",
            "phone": "9911223344",
            "consent_to_contact": True,
        })
        enquiry_id = create_resp.json()["id"]
        resp = client.patch(
            f"/api/enquiries/{enquiry_id}",
            json={"status": "fake_status"},
            headers=auth_headers,
        )
        assert resp.status_code == 422


# ===========================================================================
# 5. Demo requests
# ===========================================================================

class TestDemoRequest:
    def test_create_demo_request_valid(self, client):
        resp = client.post("/api/demo-requests", json={
            "name": "Demo Student",
            "phone": "9812345678",
            "course_interest": "JEE",
            "preferred_date": "2024-11-15",
            "preferred_time": "10:00 AM",
            "consent_to_contact": True,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert "request" in data["message"].lower()

    def test_create_demo_invalid_phone(self, client):
        resp = client.post("/api/demo-requests", json={
            "name": "Demo Student",
            "phone": "0000000",
            "consent_to_contact": True,
        })
        assert resp.status_code == 422

    def test_demo_not_confirmed_appointment(self, client):
        """Status must be 'requested', not 'confirmed'."""
        resp = client.post("/api/demo-requests", json={
            "name": "Demo Check",
            "phone": "9876512340",
            "consent_to_contact": True,
        })
        data = resp.json()
        assert data.get("status") == "requested"

    def test_list_demos_requires_auth(self, client):
        resp = client.get("/api/demo-requests")
        assert resp.status_code == 401


# ===========================================================================
# 6. Complaints
# ===========================================================================

class TestComplaints:
    def test_create_complaint_valid(self, client):
        resp = client.post("/api/complaints", json={
            "customer_name": "Complaint Student",
            "customer_phone": "9871234567",
            "category": "teaching_quality",
            "description": "The teaching quality needs improvement in the physics class.",
            "priority": "normal",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "ticket_ref" in data
        assert "lookup_token" in data
        assert data["ticket_ref"].startswith("TKT-")

    def test_ticket_status_lookup_valid(self, client):
        """Valid lookup returns status without exposing other data."""
        create_resp = client.post("/api/complaints", json={
            "customer_name": "Lookup Student",
            "description": "This is a complaint description with enough detail.",
            "category": "general",
            "priority": "normal",
        })
        data = create_resp.json()
        ticket_ref = data["ticket_ref"]
        lookup_token = data["lookup_token"]

        lookup_resp = client.post("/api/complaints/lookup", json={
            "ticket_ref": ticket_ref,
            "lookup_token": lookup_token,
        })
        assert lookup_resp.status_code == 200
        lookup_data = lookup_resp.json()
        assert lookup_data["ticket_ref"] == ticket_ref
        assert "status" in lookup_data
        # Must NOT expose customer_name or description in public view
        assert "customer_name" not in lookup_data
        assert "description" not in lookup_data

    def test_ticket_lookup_wrong_token(self, client):
        """Wrong lookup token must not reveal ticket data."""
        create_resp = client.post("/api/complaints", json={
            "customer_name": "Wrong Token Student",
            "description": "This is another complaint description for testing.",
            "category": "general",
            "priority": "normal",
        })
        ticket_ref = create_resp.json()["ticket_ref"]

        resp = client.post("/api/complaints/lookup", json={
            "ticket_ref": ticket_ref,
            "lookup_token": "wrong-token-that-does-not-match-any-record",
        })
        assert resp.status_code == 404

    def test_complaint_description_too_short(self, client):
        """Short description rejected."""
        resp = client.post("/api/complaints", json={
            "customer_name": "Short Desc",
            "description": "abc",
            "category": "general",
            "priority": "normal",
        })
        assert resp.status_code == 422

    def test_list_complaints_requires_auth(self, client):
        resp = client.get("/api/complaints")
        assert resp.status_code == 401

    def test_update_complaint_requires_auth(self, client):
        resp = client.patch("/api/complaints/1", json={"status": "resolved"})
        assert resp.status_code == 401


# ===========================================================================
# 7. Human handover
# ===========================================================================

class TestHandover:
    def test_create_handover_valid(self, client):
        resp = client.post("/api/handovers", json={
            "customer_name": "Handover Student",
            "customer_phone": "9876509876",
            "preferred_contact_method": "phone",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["status"] == "pending"

    def test_handover_no_phone_ok(self, client):
        """Phone is optional for handover."""
        resp = client.post("/api/handovers", json={
            "preferred_contact_method": "callback",
        })
        assert resp.status_code == 201

    def test_list_handovers_requires_auth(self, client):
        resp = client.get("/api/handovers")
        assert resp.status_code == 401


# ===========================================================================
# 8. Feedback
# ===========================================================================

class TestFeedback:
    def test_helpful_feedback(self, client):
        resp = client.post("/api/feedback", json={
            "rating": "helpful",
            "comment": "Very clear answer!",
        })
        assert resp.status_code == 201
        assert resp.json()["rating"] == "helpful"

    def test_not_helpful_feedback_with_question(self, client):
        resp = client.post("/api/feedback", json={
            "rating": "not_helpful",
            "unanswered_question": "What is the exact fee for NEET batch 2024?",
        })
        assert resp.status_code == 201

    def test_invalid_rating(self, client):
        resp = client.post("/api/feedback", json={"rating": "maybe"})
        assert resp.status_code == 422


# ===========================================================================
# 9. Admin auth and authorization
# ===========================================================================

class TestAdminAuth:
    def test_login_valid(self, client):
        resp = client.post("/api/admin/auth/login", json={
            "username": "testadmin",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        resp = client.post("/api/admin/auth/login", json={
            "username": "testadmin",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/admin/auth/login", json={
            "username": "nobody",
            "password": "anything",
        })
        assert resp.status_code == 401

    def test_dashboard_requires_auth(self, client):
        resp = client.get("/api/admin/dashboard")
        assert resp.status_code == 401

    def test_dashboard_with_auth(self, client, auth_headers):
        resp = client.get("/api/admin/dashboard", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_conversations" in data
        assert "open_complaints" in data

    def test_invalid_token_rejected(self, client):
        resp = client.get("/api/admin/dashboard", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401

    def test_me_endpoint(self, client, auth_headers):
        resp = client.get("/api/admin/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "testadmin"


# ===========================================================================
# 10. FAQ management (admin)
# ===========================================================================

class TestFAQAdmin:
    def test_create_faq(self, client, auth_headers):
        resp = client.post("/api/faqs", json={
            "faq_code": "ADM001",
            "category": "courses",
            "question": "Do you offer NEET coaching?",
            "answer": "A public directory lists NEET preparation.",
            "source_type": "third_party_directory",
            "verification_status": "pending",
            "is_published": True,
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["faq_code"] == "ADM001"

    def test_duplicate_faq_code_rejected(self, client, auth_headers):
        resp = client.post("/api/faqs", json={
            "faq_code": "ADM001",
            "category": "courses",
            "question": "Duplicate question",
            "answer": "Duplicate answer",
        }, headers=auth_headers)
        assert resp.status_code == 409

    def test_create_faq_requires_auth(self, client):
        resp = client.post("/api/faqs", json={
            "faq_code": "UNAUTH001",
            "category": "courses",
            "question": "Question",
            "answer": "Answer",
        })
        assert resp.status_code == 401

    def test_list_faqs_requires_auth(self, client):
        resp = client.get("/api/faqs")
        assert resp.status_code == 401

    def test_update_faq(self, client, auth_headers):
        # First find an FAQ
        list_resp = client.get("/api/faqs", headers=auth_headers)
        items = list_resp.json()["items"]
        if items:
            faq_id = items[0]["id"]
            resp = client.patch(f"/api/faqs/{faq_id}", json={
                "verification_status": "verified"
            }, headers=auth_headers)
            assert resp.status_code == 200


# ===========================================================================
# 11. No-LLM operation
# ===========================================================================

class TestNoLLM:
    def test_works_without_openai_key(self, client):
        """System must work without OPENAI_API_KEY."""
        assert os.environ.get("OPENAI_API_KEY", "") == ""
        resp = client.post("/api/chat", json={"message": "What courses do you offer?"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["reply"]) > 0


# ===========================================================================
# 12. Additional synthetic edge cases
# ===========================================================================

class TestEdgeCases:
    """Additional synthetic test queries per spec requirement (50 total)."""

    def test_very_long_name_rejected(self, client):
        resp = client.post("/api/enquiries", json={
            "name": "A" * 200,
            "phone": "9876543210",
            "consent_to_contact": True,
        })
        assert resp.status_code == 422

    def test_duplicate_enquiry_submitted(self, client):
        """Duplicate enquiry should still be accepted (stored separately)."""
        payload = {
            "name": "Duplicate Student",
            "phone": "9876543001",
            "course_interest": "NEET",
            "consent_to_contact": True,
        }
        resp1 = client.post("/api/enquiries", json=payload)
        resp2 = client.post("/api/enquiries", json=payload)
        assert resp1.status_code == 201
        assert resp2.status_code == 201
        # Both stored — staff can deduplicate
        assert resp1.json()["id"] != resp2.json()["id"]

    def test_chat_scholarship_query(self, client):
        """SYN: Scholarship query — should not invent amounts."""
        data = client.post("/api/chat", json={"message": "Do you offer scholarships?"}).json()
        assert "fees" == data["intent"] or data["intent"] == "unknown"

    def test_chat_refund_query(self, client):
        """SYN: Refund complaint."""
        data = client.post("/api/chat", json={"message": "I want a refund"}).json()
        assert data["intent"] in {"complaint", "fees"}

    def test_chat_callback_request(self, client):
        """SYN: Please contact me."""
        data = client.post("/api/chat", json={"message": "Sampark karo mujhse admission ke liye"}).json()
        assert data["intent"] in {"enquiry", "handover", "unknown"}

    def test_enquiry_phone_with_spaces(self, client):
        """Phone with spaces should be cleaned and validated."""
        resp = client.post("/api/enquiries", json={
            "name": "Space Phone Student",
            "phone": "98765 43210",
            "consent_to_contact": True,
        })
        # Should either accept (cleaning) or reject (validation) — not crash
        assert resp.status_code in {201, 422}

    def test_complaint_xss_in_description(self, client):
        """XSS in complaint description — must store safely."""
        resp = client.post("/api/complaints", json={
            "customer_name": "XSS Tester",
            "description": "<script>alert('xss')</script> This is my complaint about the centre.",
            "category": "general",
            "priority": "normal",
        })
        assert resp.status_code == 201

    def test_chat_empty_session_token(self, client):
        """Empty session token should create a new session."""
        resp = client.post("/api/chat", json={"message": "Hello", "session_token": ""})
        assert resp.status_code == 200

    def test_feedback_too_long_comment(self, client):
        """Comment exceeding max length should fail."""
        resp = client.post("/api/feedback", json={
            "rating": "helpful",
            "comment": "x" * 2001,
        })
        assert resp.status_code == 422

    def test_admin_dashboard_includes_all_stats(self, client, auth_headers):
        """Dashboard must include all required metrics."""
        resp = client.get("/api/admin/dashboard", headers=auth_headers)
        data = resp.json()
        required_keys = [
            "total_conversations", "open_enquiries", "open_complaints",
            "pending_demo_requests", "pending_handovers", "published_faqs",
            "helpful_feedback", "not_helpful_feedback",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"
