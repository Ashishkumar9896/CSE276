# Project Proposal
## Customer Support Chatbot for a Real Small Business: Coaching Centre

**Student:** [Student name]  
**Programme:** B.Tech CSE / AI-ML  
**Guide / faculty:** [Name]  
**Prototype reference organisation:** Future Vision Classes, Sonipat (third-party public listing only; no partnership implied)

**Business partner for final evaluation:** [Fill only after an owner/authorised representative consents]  
**Status:** Proposal and starter implementation; business research and owner evaluation pending.

## 1. Abstract

This project proposes a hybrid customer-support chatbot for a real coaching centre, accessible through a website and WhatsApp. The chatbot will answer owner-approved frequently asked questions, collect demo-class requests, register complaints, persist conversations and tickets in PostgreSQL, and route uncertain or complex cases to staff. Deterministic rules will control business actions, while an AI language model and retrieval over verified centre information may help interpret questions and formulate answers. The project will be evaluated using anonymized genuine queries, functional tests, task completion measures, and documented owner feedback. No fees, timings, policies, or owner opinions will be represented as facts until verified.

## 2. Problem statement

Coaching-centre staff may repeatedly answer questions about courses, fees, batch schedules, admissions and demo classes. Questions can arrive through multiple channels, and complaints or follow-ups may be missed when they are handled manually. The project will investigate the partner centre's actual support process and build a small system that automates safe, repetitive tasks while retaining human control for uncertain cases.

## 3. Aim and objectives

- Interview the owner or designated staff member and collect genuine, anonymized query examples with permission.
- Categorize frequent intents and establish an owner-approved FAQ knowledge base.
- Build a website chat interface and WhatsApp inbound integration.
- Implement booking requests, complaint tickets, conversation history and staff handover.
- Store records in PostgreSQL with validation and appropriate access controls.
- Evaluate accuracy, task completion, fallback quality, usability and owner satisfaction.
- Document limitations, privacy considerations and future improvements.

## 4. Scope

### In scope
- FAQ responses grounded in verified business data.
- Intent classification and fallback/human handover.
- Demo-class request submission (staff confirms availability).
- Complaint ticket creation and status tracking.
- Website chat and WhatsApp integration.
- Database persistence and admin reporting.
- Testing with genuine, anonymized queries and owner review.

### Out of scope for the initial MVP
- Automatic confirmation of a real class slot before a staff-approved availability system exists.
- Payments, student grading or access to student academic records.
- Unsupervised AI decisions about refunds, discounts, admissions, or policy exceptions.
- Production WhatsApp outbound messaging until API sending, signature verification and policy checks are implemented.

## 5. Proposed architecture

1. Website or WhatsApp webhook receives the message.
2. FastAPI validates the request and stores the message.
3. Intent rules identify operational actions such as booking, complaint or handover.
4. FAQ questions retrieve approved business information; an optional LLM may rephrase only grounded content.
5. Uncertain questions are handed to staff rather than answered with invented facts.
6. PostgreSQL stores customers (only when needed), conversations, messages, bookings, complaints and owner feedback.
7. Staff review requests and resolve tickets through protected admin functions.

## 6. Technology stack

- Python 3.11+
- FastAPI and Pydantic
- SQLAlchemy ORM
- PostgreSQL with psycopg; SQLite for local quick-start
- HTML/CSS/JavaScript starter client; React may replace it later
- Pytest and FastAPI TestClient
- Docker and a Python-capable hosting service
- Meta WhatsApp Business Cloud API for WhatsApp integration

## 7. Data collection and ethics

For the initial prototype, a third-party directory listing for Future Vision Classes in Sonipat is used as a seed knowledge base. The user specified Sector 15, but the located listing is for Sector 16; this discrepancy must be confirmed with the owner. This does not imply a relationship with the centre. The owner of a local coaching centre or an authorised representative must still be asked for informed permission before interviews or private log review. Customer examples will be anonymized; no personal conversation logs will be copied without authorization. The collection sheet records a source category, date, anonymization status and owner verification. The project will collect only information needed for the stated purpose, explain how contact information is used, restrict access, and establish a retention/deletion process. Owner feedback will be recorded as actually received, including criticism and requested changes.

## 8. Evaluation plan

- Intent classification: per-intent precision/recall where labels and sample sizes permit.
- FAQ grounding: percentage of answers supported by an owner-approved source.
- Fallback: percentage of unsupported questions correctly handed over rather than guessed.
- Booking workflow: valid requests saved, invalid requests rejected, and staff confirmation clearly communicated.
- Complaint workflow: ticket creation and status update tests pass.
- Usability: owner/staff rating and qualitative comments.
- Operational: response latency, API errors, and duplicate webhook handling once implemented.

Numerical targets will be agreed after the initial interview and baseline. Results will not be fabricated; small datasets will be reported with their sample size and limitations.

## 9. Deliverables

- Source code and setup guide.
- Database schema and API documentation.
- Owner interview notes and anonymized query dataset.
- Test report and evaluation results.
- Screenshots/demo and deployment notes.
- Owner feedback record and change log.
- Final report including limitations and future work.

## 10. Risks and mitigations

- Incorrect AI answer: use approved sources, deterministic actions and fallback.
- Privacy exposure: minimize data, anonymize logs, protect admin endpoints and define retention.
- Double booking: current MVP records requests only; introduce transactional slot inventory before confirmations.
- WhatsApp webhook abuse: validate signatures, deduplicate events and use secrets before production.
- Low sample size: disclose it and supplement with clearly labelled synthetic functional tests, never relabel synthetic examples as genuine.

## 11. Proposed schedule

| Week | Work |
|---|---|
| 1 | Owner interview, permission, query collection and scope approval |
| 2 | Requirements, intent taxonomy, FAQ verification and schema |
| 3 | FastAPI endpoints, database models and validation |
| 4 | Chat logic, FAQ grounding and fallback/handover |
| 5 | Booking/complaint workflows and website UI |
| 6 | WhatsApp integration and security hardening |
| 7 | Functional tests and owner usability review |
| 8 | Improvements, evaluation, final report and demonstration |

Adjust this schedule to the course deadline and owner availability.

## 12. Current status and limitations

A starter codebase implements the website, rule-based hybrid baseline, persistent chat records, booking requests, complaint tickets, feedback capture and inbound WhatsApp webhook storage. It does not yet implement production admin authentication, outbound WhatsApp replies, signature verification, a real AI provider integration, slot inventory or migrations. Those gaps are explicitly documented and must be addressed before public deployment.


## Appendix A: Dataset provenance

`data/public_faq_dataset.csv` contains paraphrased answers based on official public pages at https://www.pw.live/faqs and https://www.pw.live/contact-us. Entries are marked public-source and must be rechecked before deployment. `data/synthetic_test_queries.csv` is a synthetic test set created for software validation. It is not evidence of real customer query collection. Genuine query collection and owner feedback remain pending.


## Appendix A: Dataset provenance

`data/public_faq_dataset.csv` contains a small seed dataset based on the third-party listing https://instiwise.com/sonipat/coaching/future-vision-classes-sector-16-sonipat. The user specified Sector 15, while the located listing is Sector 16; verify the intended branch and every business fact with the owner before deployment. `data/synthetic_test_queries.csv` contains synthetic functional test cases, not real customer conversations. Genuine query collection and owner feedback remain pending.
