# Evaluation Plan and Owner Feedback

## Data sources
1. Genuine anonymized queries gathered with owner permission.
2. Owner-approved FAQ and policies.
3. Clearly labelled synthetic test cases for edge cases only.
4. Automated functional tests.

Never merge synthetic cases into the genuine-query count.

## Test record template

| Test ID | Source (genuine/synthetic) | Expected intent | Expected outcome | Actual outcome | Pass? | Notes |
|---|---|---|---|---|---|---|
| T001 | [fill] | [fill] | [fill] | [fill] | [fill] | [fill] |

## Metrics
- Intent accuracy: correct intent predictions / labelled test messages.
- FAQ grounding rate: answers supported by verified source / FAQ answers audited.
- Safe fallback rate: unsupported queries correctly escalated / unsupported queries tested.
- Booking request success: valid booking requests persisted / valid booking requests submitted.
- Complaint creation success: valid complaints receiving ticket IDs / valid complaints submitted.
- Human handover correctness: cases requiring staff that are marked for handover / such cases tested.
- Median response time and error rate.
- Owner rating (1–5) and qualitative feedback.

Report counts and denominators. For a small convenience sample, state that results are exploratory and not representative of all customers.

## Owner review form
- Owner / staff role: [fill]
- Review date: [fill]
- Tasks demonstrated: [fill]
- Ease of use (1–5): [fill]
- Usefulness (1–5): [fill]
- Accuracy of answers (1–5): [fill]
- Confidence in handover (1–5): [fill]
- Most useful feature: [fill]
- Incorrect or missing answer: [fill]
- Requested changes: [fill]
- Changes made after feedback: [fill]
- Owner permission to quote anonymized feedback: [Yes/No]

Do not pre-fill ratings or write positive feedback on behalf of the owner.
