# Backlog Refinement — Sprint 2

Date       : 2026-05-12
Attendees  : Kerem Ataç
Duration   : 30 minutes
Format     : Solo compressed sprint evidence

## Stories Discussed

### US-J — Tutoring Flow
- Current understanding: The tutoring flow must show activity text, ask one question at a time, store conversation history, and block ENDED activities.
- Decision: Implement deterministic tutoring fallback suitable for tests and future LLM integration.
- Re-estimate if changed: no change.

### US-K — Objective Scoring
- Current understanding: Scoring must award +1 only the first time each objective is achieved and prevent duplicate points.
- Decision: Use achieved_objectives in student_progress and score_logs metadata.
- Re-estimate if changed: no change.

### TECH — Password Management API Completion
- Current understanding: Some required API contract functions were still skeletons.
- Decision: Add TSK-72 as a Sprint 2 technical completion task.
- Re-estimate if changed: +1 SP using Sprint 2 buffer.

## Changes Made to Backlog

| Change | Story/Task | From | To | Reason |
|--------|------------|------|----|--------|
| Add task | TSK-72 | Not planned | Sprint 2 backlog | Required API functions were still not implemented |
| Complete | TSK-69-71 | To Do | Done | Export score CSV needed for instructor workflow |
