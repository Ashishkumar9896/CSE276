# Coaching Centre Customer Support Chatbot

A starter MVP using Python, FastAPI, SQLAlchemy and PostgreSQL-compatible storage. The browser chat, demo booking requests, complaint tickets, basic admin summary, and inbound WhatsApp webhook receiver are implemented.

## Important honesty / production notes

- No coaching-centre facts are fabricated. Fees, timings and location answers explicitly say verified information has not yet been added.
- Booking records are requests, not confirmed appointments. There is no slot inventory yet; staff must confirm availability.
- The WhatsApp endpoint supports Meta webhook verification and stores inbound text messages. It does **not** send outbound WhatsApp replies and does not yet validate Meta webhook signatures. Do not publish it as production-ready until these are implemented.
- `/api/admin/summary`, booking/complaint listing, and complaint updates have no authentication in this MVP. Keep the service private during development. Add admin authentication, role checks, rate limits, CORS policy, request logging policy, and webhook signature validation before public deployment.
- Do not collect personal data without a clear purpose and notice. Collect phone numbers only when needed for a requested follow-up, record consent, and set a retention/deletion policy.

## Local setup

Requires Python 3.11+ (3.12 recommended).

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # Windows; on macOS/Linux use: cp .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and API docs at http://127.0.0.1:8000/docs. SQLite is used locally by default.

## PostgreSQL

Create a database and set this environment variable (prefer a managed secret setting in deployment, not a committed `.env`):

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
```

Then restart the application. For a serious deployment, use Alembic migrations instead of `create_all()` at startup.

## Tests

```bash
pytest -q
```

Tests use a local SQLite test database and exercise health, FAQ fallback, booking request, complaint ticket, and validation. Delete `test_chatbot.db` before re-running if you want a clean state.

## Collect genuine business data

1. Ask the owner for permission to interview them and collect anonymized, genuine queries.
2. Use `docs/owner_interview.md` and `docs/query_collection.csv` as collection templates.
3. Verify every fee, course, schedule, policy, address, and refund statement with the owner.
4. Replace placeholder FAQ responses in `app/chatbot.py` only with approved content.
5. Label source and date for every approved answer. Keep raw customer logs private; remove names and phone numbers from the research dataset unless explicitly needed and consented to.
6. Get owner feedback using `POST /api/owner-feedback` and document what changed as a result. Do not claim owner approval until it actually happens.

## WhatsApp integration

1. Create/configure a Meta WhatsApp Business Cloud API app and public HTTPS webhook URL.
2. Set `WHATSAPP_VERIFY_TOKEN` in the host's environment.
3. Configure the GET callback URL `/whatsapp/webhook` and subscribe to message events.
4. Before going live: validate `X-Hub-Signature-256` using the app secret, handle duplicate webhook deliveries, send replies using the Cloud API, respect the 24-hour customer-service window and approved template rules, add retry/idempotency, and test with a dedicated number. Follow current Meta policies.
5. The inbound webhook only stores messages in this starter version; it does not send a WhatsApp response.

## Deployment outline

- Deploy this repository as a Docker web service on a Python-capable host such as Render.
- Provision managed PostgreSQL; configure `DATABASE_URL` as a secret environment variable.
- Set `WHATSAPP_VERIFY_TOKEN`; use a unique random secret.
- Configure health check `/health`.
- Add authentication and HTTPS before public use. Configure backups, logs without message contents where possible, monitoring, and data retention.
- A static Vercel frontend is not required because FastAPI serves a basic HTML page. If you later split the React frontend onto Vercel, configure a strict allowed-origin CORS list and the API base URL.

## Main API endpoints

- `GET /health`
- `POST /api/chat`
- `POST /api/bookings`
- `GET /api/bookings` (protect before deployment)
- `POST /api/complaints`
- `GET /api/complaints` (protect before deployment)
- `PATCH /api/complaints/{ticket_id}?status=in_progress`
- `POST /api/owner-feedback`
- `GET /api/admin/summary` (protect before deployment)
- `GET|POST /whatsapp/webhook`

## Project structure

```text
app/
  chatbot.py       # intent rules and safe fallback
  database.py      # SQLAlchemy engine/session
  main.py          # API, website, WhatsApp inbound receiver
  models.py        # database models
  schemas.py       # request validation
tests/
  test_app.py
docs/
  project_proposal.md
  owner_interview.md
  evaluation_plan.md
  query_collection.csv
```


## Public-source prototype dataset (Future Vision Classes, Sonipat)

This project includes `data/public_faq_dataset.csv`, a small seed dataset based on a third-party directory listing for Future Vision Classes in Sonipat:
- https://instiwise.com/sonipat/coaching/future-vision-classes-sector-16-sonipat

Important: the user specified Sector 15, but the listing found is Sector 16. Verify with the business owner whether this is the intended centre before treating the address as correct. The dataset records source URLs, verification date, and an owner-verification status. It is **not owner-approved** and does not imply a partnership. The `data/synthetic_test_queries.csv` file contains synthetic questions written for software testing. They are **not genuine customer conversations** and must not be reported as collected customer queries. The prototype is not connected to the centre's booking, complaint, or support systems.
