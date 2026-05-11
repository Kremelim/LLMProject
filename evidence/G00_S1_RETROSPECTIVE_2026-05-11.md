# Sprint 1 Retrospective

Date       : 2026-05-11
Attendees  : Kerem Ataç
Facilitator: Kerem Ataç
Duration   : 30 minutes
Format     : Solo compressed sprint evidence

## What Went Well
- Core Sprint 1 product scope was completed: auth, authorization, course listing, activity listing, activity creation, start/end, and ACTIVE-only student access.
- Tests were added for each major backend behavior.
- GitHub branch and PR workflow was used instead of only committing directly to main.
- Supabase schema supported all Sprint 1 stories.

## What Went Badly
- Initial database connection blocked progress because direct connection was hanging.
- Early evidence used temporary task IDs before being aligned with ClickUp TSK IDs.
- Some evidence cleanup happened after implementation instead of immediately after each task transition.

## Root Causes
- Database issue happened because the direct Supabase connection was not reliable in the local environment.
- Temporary task ID mismatch happened because ClickUp task IDs were finalized after the first evidence draft.
- Evidence cleanup lag happened because implementation work moved faster than process documentation.

## Action Items for Next Sprint

| Action | Owner | How We Will Verify It |
|--------|-------|-----------------------|
| Use ClickUp TSK IDs from the start of Sprint 2 | Kerem Ataç | Sprint 2 backlog and scope log use TSK-41+ consistently |
| Update Scope Change Log immediately after each task transition | Kerem Ataç | Check scope log before every commit |
| Keep using feature branches and PR descriptions with tests listed | Kerem Ataç | GitHub PR evidence file will reference each PR |
| Create Sprint 2 evidence files before implementation starts | Kerem Ataç | Sprint 2 planning, backlog, and scope log files exist before coding |

## Team Agreements
- Maintain branch names, commit messages, and PR titles with story/task references.
- Keep .env local and never commit secrets.
- Run python -m pytest before every PR.
- Do not expose learning objectives in student-facing responses.
