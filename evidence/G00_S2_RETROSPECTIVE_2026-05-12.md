# Sprint 2 Retrospective

Date       : 2026-05-12
Attendees  : Kerem Ataç
Facilitator: Kerem Ataç
Duration   : 30 minutes
Format     : Solo compressed sprint evidence

## What Went Well
- Sprint 2 completed all remaining product behavior.
- Tests covered update, tutoring, scoring, manual grading, reset, export, and password management.
- The Sprint 1 foundation made Sprint 2 implementation faster.
- Objective scoring was implemented in a deterministic testable way.

## What Went Badly
- Password management functions were noticed late.
- Sprint 2 evidence and code moved quickly, so scope log cleanup needed extra attention.
- LLM integration was implemented as deterministic fallback rather than full OpenRouter production behavior.

## Root Causes
- Password functions were in the API contract but not tied to main user stories early enough.
- The compressed solo workflow made implementation faster than process documentation.
- External LLM dependency was intentionally minimized to keep tests reliable.

## Action Items Before Submission

| Action | Owner | How We Will Verify It |
|--------|-------|-----------------------|
| Run full pytest before final ZIP | Kerem Ataç | Terminal output shows all tests passed |
| Fill test evidence matrix | Kerem Ataç | G00_TEST_EVIDENCE_MATRIX_2026-05-12.csv exists |
| Fill commit traceability | Kerem Ataç | G00_GITHUB_COMMIT_TRACEABILITY_2026-05-12.md exists |
| Create sprint-2 git tag | Kerem Ataç | GitHub tag list includes sprint-2 |
| Prepare REPO_INFO.txt | Kerem Ataç | Submission ZIP contains repository URL and tags |

## Team Agreements
- Keep final submission honest about solo compressed sprint format.
- Do not commit .env or Supabase secrets.
- Preserve instructor_tests/ folder.
- Keep all required services.py function signatures unchanged.
