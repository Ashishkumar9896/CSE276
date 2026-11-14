"""
Future Vision Classes — Customer Support Chatbot.
Hybrid AI Chatbot: Deterministic intent routing + Verified Knowledge Base
+ Optional LLM (Gemini / OpenAI / Groq) for warm, natural counseling replies.
"""
from __future__ import annotations
import os
import re
import pathlib
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Ensure .env is loaded
_env_path = pathlib.Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SuggestedAction:
    label: str
    message: str


@dataclass
class BotResult:
    reply: str
    intent: str
    handover: bool = False
    suggested_actions: list[SuggestedAction] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Intent definitions
# ---------------------------------------------------------------------------

_INTENT_PATTERNS: dict[str, list[str]] = {
    "greeting": [
        "hello", "hi", "hey", "namaste", "namaskar", "good morning",
        "good afternoon", "good evening", "helo", "hii", "heyyy", "pranam",
        "greetings",
    ],
    "handover": [
        "human", "person", "staff", "call me", "talk to someone",
        "agent", "counsellor", "counselor", "speak to", "connect me",
        "real person", "live agent", "koi baat kare", "baat karni hai",
        "counseling", "counselling", "representative", "contact person",
    ],
    "complaint": [
        "complaint", "problem", "issue", "unhappy", "refund", "dissatisfied",
        "not working", "cannot access", "can't access", "bad experience",
        "shikayat", "problem hai", "pareshaan", "ticket", "grievance",
        "feedback", "cancel admission",
    ],
    "demo_request": [
        "demo", "demo class", "trial", "trial class", "free trial", "free class",
        "visit", "demo book", "counselling session", "counseling session",
        "demo chahiye", "trial chahiye", "trial session", "free demo",
        "attend demo", "try class",
    ],
    "enquiry": [
        "admission", "admissions", "enrol", "enroll", "enrolment", "enrollment",
        "register", "registration", "join", "callback", "call back", "contact me",
        "get in touch", "admission form", "application", "apply", "admission open",
        "admission kab", "how to join", "how to take admission",
    ],
    "fees": [
        "fee", "fees", "price", "cost", "payment", "kitne paise",
        "charge", "charges", "how much", "kitna lagega", "scholarship", "scholarships",
        "discount", "concession", "installment", "paisa", "paise", "fee structure",
        "1.75 lakh", "1.75", "90k", "90000", "10k", "20k", "per subject",
        "10th pass fee", "two year fee", "1 year fee", "rate",
    ],
    "timings": [
        "time", "timing", "timings", "batch", "batches", "schedule", "when",
        "time table", "timetable", "kab", "morning batch", "evening batch",
        "class time", "class kab", "hours", "kitne baje", "days", "weekend",
    ],
    "location": [
        "address", "location", "where", "direction", "sector 15",
        "sector 16", "sonipat", "kahan", "kahan hai", "near",
        "rangoli", "sco", "reach", "how to reach", "map", "office",
        "centre kahan hai", "center kahan hai", "landmark",
    ],
    "contact": [
        "contact", "phone number", "email", "website", "whatsapp",
        "number", "helpline", "reach out", "sampark", "phone", "mobile",
    ],
    "courses": [
        "course", "courses", "subject", "subjects", "classes",
        "teach", "jee", "iit", "neet", "medical", "engineering",
        "preparation", "syllabus", "curriculum", "which class", "konsa class",
        "neet coaching", "jee coaching", "coaching classes", "foundation", "boards", "cbse",
        "9th", "10th", "11th", "12th", "dropper", "repeater", "kya padhate ho",
        "pcm", "pcb", "physics", "chemistry", "maths", "math", "biology",
        "science", "english", "class 9", "class 10", "class 11", "class 12",
        "10th pass", "10th passed", "2 year batch", "1 year batch",
    ],
    "existing_enquiry": [
        "my enquiry", "enquiry status", "ticket status", "my complaint",
        "follow up", "meri enquiry", "status check", "track ticket",
    ],
}

# Default suggested actions presented after each response
_COMMON_ACTIONS = [
    SuggestedAction("Course Info", "What courses do you offer?"),
    SuggestedAction("Demo Class", "How can I book a demo class?"),
    SuggestedAction("Talk to Staff", "I want to talk to a staff member"),
]

# ---------------------------------------------------------------------------
# Rule-based response templates (Genuine, Realistic, Grounded)
# ---------------------------------------------------------------------------

_TEMPLATES: dict[str, str] = {
    "greeting": (
        "Hello and welcome to Future Vision Classes! 🎓\n\n"
        "We are Sonipat's premier coaching institute specializing in IIT-JEE, NEET-UG, and Board foundation for Classes 9 to 12.\n\n"
        "How can I help you today? You can ask me about:\n"
        "• 📚 **Courses & Subjects** (Class 9–10 Science/Maths/English, 11–12 PCM/PCB, JEE & NEET)\n"
        "• 💰 **Fee Structure** (2-Year @ ₹1.75L, 1-Year @ ₹90k, Modular @ ₹10k/₹20k per subject)\n"
        "• ⏰ **Batch Timings** (Morning & Evening sessions)\n"
        "• 🎯 **Free Demo Class** booking\n"
        "• 📍 **Center Location** & Counseling hours"
    ),
    "courses": (
        "Future Vision Classes provides structured, result-oriented coaching for Classes 9 to 12 along with IIT-JEE and NEET-UG preparation:\n\n"
        "1. 🎓 **2-Year Integrated Batch (Class 10 Passed / Moving to 11th):**\n"
        "   Complete 2-year preparation for IIT-JEE (Main & Advanced) or NEET-UG covering Class 11th & 12th syllabus, DPPs, and national mock tests (Total Fee: ₹1.75 Lakh for 2 years).\n\n"
        "2. 🎯 **1-Year Target & Dropper Batch (JEE & NEET):**\n"
        "   High-intensity 1-year coaching for Class 12th appearing and dropper/repeater students (Fee: ₹90,000 / year).\n\n"
        "3. 📘 **Classes 11th & 12th (PCM & PCB Streams):**\n"
        "   Board & Competitive subject coaching in Physics, Chemistry, Mathematics, and Biology (Fee: ₹20,000 per subject / year).\n\n"
        "4. 📗 **Classes 9th & 10th (Foundation & Boards):**\n"
        "   Core conceptual coaching in **Science, Maths, and English** (Fee: ₹10,000 per subject / year, or ₹30,000 for all three subjects).\n\n"
        "Would you like to book a free demo class or speak with our academic counselor?"
    ),
    "fees": (
        "Here is the verified fee structure for Future Vision Classes:\n\n"
        "• 🎓 **2-Year Integrated Batch (Class 10 Passed / Moving to 11th):**\n"
        "  **₹1.75 Lakh (₹1,75,000)** total for the 2-year JEE or NEET program.\n\n"
        "• 🎯 **1-Year Intensive Batch (Class 12th & Droppers):**\n"
        "  **₹90,000 / year** for comprehensive JEE or NEET preparation.\n\n"
        "• 📘 **Classes 11th & 12th (Individual Subjects - PCM / PCB):**\n"
        "  **₹20,000 per subject / year** (Physics, Chemistry, Maths, Biology).\n\n"
        "• 📗 **Classes 9th & 10th (Foundation & Boards):**\n"
        "  **₹10,000 per subject / year** for **Science**, **Maths**, and **English** (₹30,000 for all three subjects).\n\n"
        "💡 *Installment options and merit scholarships are available.* "
        "Please **contact our admissions desk** or click **'Admission Enquiry'** above for enrollment and batch allocations!"
    ),
    "timings": (
        "Future Vision Classes operates structured batches designed to complement school hours:\n\n"
        "• **Morning Batches:** 8:00 AM – 12:00 PM (Focused sessions for Target & Dropper batches)\n"
        "• **Evening Batches:** 4:00 PM – 7:30 PM (Tailored for school-going students in Classes 9, 10, 11, 12)\n"
        "• **Weekend Sessions:** 9:00 AM – 2:00 PM (Dedicated Doubt Clinics & Mock Tests)\n\n"
        "Please **contact our center** or request a trial class to check verified slot availability for your specific grade."
    ),
    "location": (
        "📍 **Future Vision Classes** is located at:\n\n"
        "**SCO No. 21–22, Rangoli Green, Sector 16, Sonipat, Haryana 131001**\n"
        "*(Conveniently situated near Sector 15 and main arterial roads).*\n\n"
        "🕒 **Visiting Hours:**\n"
        "• Monday – Saturday: 9:00 AM – 7:00 PM\n"
        "• Sunday: 10:00 AM – 2:00 PM\n\n"
        "You are welcome to visit our campus to meet the faculty and tour our classrooms!"
    ),
    "contact": (
        "You can connect with Future Vision Classes through the following verified options:\n\n"
        "• 📍 **Campus Address:** SCO No. 21–22, Rangoli Green, Sector 16, Sonipat, Haryana\n"
        "• 📋 **Admission Enquiry:** Submit our online form for a prompt callback from our admissions team\n"
        "• 🎯 **Trial Class:** Reserve a seat via the 'Book Free Demo' option\n"
        "• 💬 **Academic Counseling:** Click 'Talk to Staff' below to request a 1-on-1 counselor consultation\n\n"
        "Our team will be delighted to guide you with any queries!"
    ),
    "enquiry": (
        "Admissions for the upcoming academic session are currently open! 🎓\n\n"
        "We offer specialized coaching for Classes 9–10 (Science, Maths, English), Classes 11–12 (PCM/PCB), and dedicated JEE/NEET batches.\n\n"
        "👉 Please use the **Admission Enquiry** button above to share your details, or leave your phone number here. Our senior academic counselor will get in touch with you shortly."
    ),
    "demo_request": (
        "Experience our teaching methodology firsthand with a **Free Demo Class**! 🎯\n\n"
        "You can attend a live lecture with our expert faculty in Science, Maths, English, Physics, Chemistry, or Biology and see how we teach.\n\n"
        "👉 Click the **'Book Free Demo'** button above to choose your preferred subject and date, and our admissions team will reserve your seat."
    ),
    "complaint": (
        "We are committed to maintaining the highest standards of student learning and support. 🛡️\n\n"
        "Please use the **'Support & Tickets'** form above to submit your concern. You will immediately receive a unique **Ticket Reference ID** and lookup token so you can track resolution progress in real time.\n\n"
        "Our student grievance team will review and address your issue with high priority."
    ),
    "handover": (
        "I am connecting your request to our academic counseling desk. 👨‍🏫\n\n"
        "Please provide your name and phone number (or submit an enquiry form above), and an experienced counselor from Future Vision Classes will reach out to assist you personally."
    ),
    "existing_enquiry": (
        "To check the status of an existing support ticket or enquiry:\n\n"
        "1. Click on **'Support & Tickets'** in the navigation bar above.\n"
        "2. Switch to the **'Lookup Ticket'** tab.\n"
        "3. Enter your **Ticket Reference Number** and **Lookup Token**.\n\n"
        "If you submitted an admission enquiry, our counseling team typically calls back within 24 business hours."
    ),
    "unknown": (
        "Thank you for reaching out to Future Vision Classes! 🎓\n\n"
        "We specialize in coaching for Classes 9 & 10 (Science, Maths, English), Classes 11 & 12 (PCM/PCB), and IIT-JEE / NEET-UG entrance exams.\n\n"
        "• Ask about our **2-Year Integrated (₹1.75L) or 1-Year (₹90k) batches**\n"
        "• Ask about **subject-wise fees (₹10k for 9-10th, ₹20k for 11-12th)**\n"
        "• Click **'Book Free Demo'** or **'Talk to Staff'** to speak with our counselors directly!"
    ),
}

# ---------------------------------------------------------------------------
# Suggested actions per intent
# ---------------------------------------------------------------------------

_INTENT_ACTIONS: dict[str, list[SuggestedAction]] = {
    "greeting": [
        SuggestedAction("Courses", "What courses do you offer?"),
        SuggestedAction("Admissions", "How can I get admitted?"),
        SuggestedAction("Book Demo", "I want to book a demo class"),
        SuggestedAction("Fees", "What are the fees?"),
    ],
    "courses": [
        SuggestedAction("Fee Structure", "What are the fees?"),
        SuggestedAction("Book Demo", "I want a demo class"),
        SuggestedAction("Class Timings", "What are the class timings?"),
        SuggestedAction("Admissions", "How do I get admitted?"),
    ],
    "fees": [
        SuggestedAction("Admission Enquiry", "I want to apply for admission"),
        SuggestedAction("Book Demo", "I want to book a demo class"),
        SuggestedAction("Talk to Staff", "I want to talk to a staff member"),
    ],
    "timings": [
        SuggestedAction("Book Demo", "I want a demo class"),
        SuggestedAction("Course Info", "What courses do you offer?"),
        SuggestedAction("Talk to Staff", "I want to talk to a staff member"),
    ],
    "location": [
        SuggestedAction("Contact Info", "How can I contact you?"),
        SuggestedAction("Book Demo", "I want to visit for a demo class"),
        SuggestedAction("Talk to Staff", "I want to talk to a staff member"),
    ],
    "enquiry": [
        SuggestedAction("Book Demo", "I want a demo class"),
        SuggestedAction("Course Info", "What courses do you offer?"),
        SuggestedAction("Talk to Staff", "I want to talk to a staff member"),
    ],
    "demo_request": [
        SuggestedAction("Course Info", "What courses do you offer?"),
        SuggestedAction("Admission Enquiry", "I want to enquire about admission"),
        SuggestedAction("Talk to Staff", "I want to talk to a staff member"),
    ],
    "complaint": [
        SuggestedAction("Track Ticket", "What is the status of my ticket?"),
        SuggestedAction("Talk to Staff", "I want to talk to a staff member"),
    ],
    "handover": [
        SuggestedAction("Book Demo", "I want to book a demo class"),
        SuggestedAction("Course Info", "Tell me about courses"),
    ],
    "unknown": [
        SuggestedAction("Course Info", "What courses do you offer?"),
        SuggestedAction("Fee Details", "What are the fees?"),
        SuggestedAction("Book Demo", "I want to book a demo class"),
    ],
}


# ---------------------------------------------------------------------------
# Intent classifier
# ---------------------------------------------------------------------------

def classify_intent(message: str) -> str:
    """
    Deterministic keyword-based intent classifier.
    Returns one of the defined intent keys, defaulting to 'unknown'.
    """
    text = message.casefold().strip()

    # Priority order: specific actions & clear queries first
    for intent in [
        "handover", "complaint", "demo_request", "existing_enquiry", "enquiry",
        "fees", "timings", "location", "contact", "courses", "greeting",
    ]:
        patterns = _INTENT_PATTERNS.get(intent, [])
        for pattern in patterns:
            # Word-boundary matching
            if re.search(r'\b' + re.escape(pattern) + r'\b', text):
                return intent

    return "unknown"


# ---------------------------------------------------------------------------
# FAQ search with stop-word filtering & intent weighting
# ---------------------------------------------------------------------------

_STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "in", "of", "to", "do", "for",
    "with", "on", "at", "by", "from", "about", "tell", "me", "your", "you",
    "can", "how", "why", "who", "which", "will", "i", "my", "we", "our",
    "offer", "offers", "provide", "provides", "give", "gives", "have", "has",
}


def _normalize_token(token: str) -> str:
    t = token.lower()
    if t in {"fees", "fee"}:
        return "fee"
    if t in {"9th", "9"}:
        return "9"
    if t in {"10th", "10"}:
        return "10"
    if t in {"11th", "11"}:
        return "11"
    if t in {"12th", "12"}:
        return "12"
    if t.endswith("s") and len(t) > 3:
        return t[:-1]
    return t


def search_faq_in_memory(
    query: str,
    faqs: list[dict],
    intent: Optional[str] = None,
) -> Optional[dict]:
    """
    Search over the in-memory FAQ list using normalized content words and category relevance.
    """
    if not faqs:
        return None

    query_tokens = [
        _normalize_token(w)
        for w in re.findall(r'\b\w+\b', query.casefold())
        if w not in _STOP_WORDS
    ]
    if not query_tokens:
        return None
    query_set = set(query_tokens)

    best_score = 0
    best_faq = None

    for faq in faqs:
        q_text = faq.get("question", "").casefold()
        a_text = faq.get("answer", "").casefold()
        category = faq.get("category", "").casefold()

        q_tokens = {
            _normalize_token(w)
            for w in re.findall(r'\b\w+\b', q_text)
            if w not in _STOP_WORDS
        }
        a_tokens = {
            _normalize_token(w)
            for w in re.findall(r'\b\w+\b', a_text)
            if w not in _STOP_WORDS
        }

        # Weight question matches 2x higher than answer matches
        q_overlap = len(query_set & q_tokens)
        a_overlap = len(query_set & a_tokens)
        overlap = (q_overlap * 2) + a_overlap

        # Boost score if category matches detected intent
        if intent and (category == intent or (intent == "demo_request" and category == "booking")):
            overlap += 2

        if overlap > best_score:
            best_score = overlap
            best_faq = faq

    # Require at least 2 content-points match
    if best_score >= 2:
        return best_faq
    return None


# ---------------------------------------------------------------------------
# LLM Integration (Google Gemini, OpenAI, or Groq)
# Generates genuine, empathetic, authentic counselor answers
# ---------------------------------------------------------------------------

def generate_llm_reply(
    message: str,
    faqs: list[dict],
    history: Optional[list[dict]] = None,
) -> Optional[str]:
    """
    Generate a genuine, human-like, warm counselor response using Gemini, OpenAI, or Groq.
    Returns None if no API keys are configured or if the request fails.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    groq_key = os.getenv("GROQ_API_KEY", "").strip()

    if not (gemini_key or openai_key or groq_key):
        return None

    # Format FAQ knowledge base
    context_lines = [
        f"Q: {f.get('question', '')}\nA: {f.get('answer', '')}"
        for f in faqs
    ]
    faq_context = "\n\n".join(context_lines)

    system_prompt = (
        "You are Aakash / Neha, the friendly, experienced, and highly professional Senior Academic Counselor "
        "at Future Vision Classes, Sonipat, Haryana. You speak to students and parents with genuine warmth, "
        "reassurance, and encouraging advice.\n\n"
        "OFFICIAL KNOWLEDGE BASE (Follow strictly; never contradict these facts):\n"
        "• Classes 9 & 10: Foundation & Board preparation in Science, Maths, and English. Fee: ₹10,000 per subject / year (₹30,000 for all three).\n"
        "• Classes 11 & 12: Board & Competitive preparation in PCM (Physics, Chemistry, Maths) or PCB (Physics, Chemistry, Biology). Fee: ₹20,000 per subject / year.\n"
        "• 2-Year Integrated Batch (for Class 10 Passed students entering Class 11): Comprehensive IIT-JEE (Main & Adv) or NEET-UG preparation. Total Fee: ₹1.75 Lakh (₹1,75,000) for the 2 years.\n"
        "• 1-Year Intensive Batch (for Class 12th & Droppers): Target IIT-JEE or NEET-UG preparation. Fee: ₹90,000 / year.\n"
        "• Class Timings: Morning (8:00 AM – 12:00 PM) for droppers, Evening (4:00 PM – 7:30 PM) for school-going, Weekends for test series & doubts.\n"
        "• Campus: SCO No. 21–22, Rangoli Green, Sector 16, Sonipat, Haryana 131001 (convenient from Sector 15). Visiting hours: Mon–Sat 9am–7pm.\n"
        "• Free Demo: Students are encouraged to attend a free trial class before enrolling.\n"
        "• Scholarships: Merit-based scholarship concessions based on past school marks, plus flexible installment options.\n\n"
        f"VERIFIED FAQ CONTEXT:\n{faq_context}\n\n"
        "CONVERSATIONAL GUIDELINES:\n"
        "- Respond as a genuine, caring counselor. Be warm, polite, encouraging, and natural.\n"
        "- If user writes in English, reply in fluent, professional English.\n"
        "- If user writes in Hindi or Hinglish (e.g. 'fees kitni hai', 'demo chahiye'), reply in warm, polite Hinglish.\n"
        "- Use clean formatting (**bolding**, bullet points) so details are easy for parents/students to read.\n"
        "- Invite them warmly to book a free demo class or request an academic callback when appropriate.\n"
        "- Never hallucinate other prices or guarantee exam ranks."
    )

    try:
        import httpx

        # 1. Google Gemini (Fast & Free Tier via Google AI Studio)
        if gemini_key:
            try:
                # Try gemini-1.5-flash or gemini-2.0-flash
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                user_content = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nSTUDENT QUESTION:\n{message}"
                payload = {
                    "contents": [{"parts": [{"text": user_content}]}],
                    "generationConfig": {
                        "temperature": 0.35,
                        "maxOutputTokens": 450,
                    }
                }
                resp = httpx.post(url, json=payload, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
            except Exception:
                pass

        # 2. OpenAI (GPT-4o-mini)
        if openai_key:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
                messages = [{"role": "system", "content": system_prompt}]
                if history:
                    for h in history[-4:]:
                        role = "assistant" if h.get("sender") == "bot" else "user"
                        messages.append({"role": role, "content": h.get("body", "")})
                messages.append({"role": "user", "content": message})

                payload = {
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.35,
                    "max_tokens": 400,
                }
                resp = httpx.post(url, headers=headers, json=payload, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception:
                pass

        # 3. Groq (Llama-3.3-70b)
        if groq_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                    ],
                    "temperature": 0.35,
                    "max_tokens": 400,
                }
                resp = httpx.post(url, headers=headers, json=payload, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception:
                pass

    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# Main answer function
# ---------------------------------------------------------------------------

def answer(
    message: str,
    published_faqs: Optional[list[dict]] = None,
    conversation_history: Optional[list[dict]] = None,
    use_llm: bool = True,
) -> BotResult:
    """
    Generate a bot reply using:
    1. Deterministic intent classification (for actions & routing)
    2. Dynamic Generative AI via LLM (Gemini / OpenAI / Groq) if API key configured
    3. Grounded intent-weighted FAQ knowledge base
    4. Realistic conversational templates as reliable fallback
    """
    intent = classify_intent(message)
    handover = intent in {"handover", "complaint"}
    actions = _INTENT_ACTIONS.get(intent, _COMMON_ACTIONS)

    # 1. Try LLM if enabled and API key is present
    if use_llm and published_faqs:
        llm_reply = generate_llm_reply(message, published_faqs, conversation_history)
        if llm_reply:
            return BotResult(
                reply=llm_reply,
                intent=intent if intent != "unknown" else "general_enquiry",
                handover=handover,
                suggested_actions=actions,
            )

    # 2. Check FAQ knowledge base
    if published_faqs:
        matched_faq = search_faq_in_memory(message, published_faqs, intent=intent)
        if matched_faq:
            answer_text = matched_faq["answer"]
            return BotResult(
                reply=answer_text,
                intent=intent if intent != "unknown" else matched_faq.get("category", "unknown"),
                handover=handover,
                suggested_actions=actions,
            )

    # 3. Rule-based template response
    template = _TEMPLATES.get(intent, _TEMPLATES["unknown"])
    return BotResult(
        reply=template,
        intent=intent,
        handover=handover,
        suggested_actions=actions,
    )
