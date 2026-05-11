# Sprint 2 Planning Record

Date       : 2026-05-11
Duration   : 1 hour
Attendees  : Kerem Ataç
Facilitator: Kerem Ataç
Location   : Individual / local setup
Format     : Solo compressed sprint evidence

## Sprint Goal
By the end of Sprint 2, the system can update activities, support the student tutoring flow,
score objectives only once, export scores, support manual grading, and reset activities safely.

## Stories Selected for This Sprint

| Story | Description | SP | Owner | ClickUp Task IDs |
|-------|-------------|----|-------|------------------|
| US-G | Update activity | 5 | Kerem Ataç | TSK-41 to TSK-45 |
| US-J | Tutoring flow | 8 | Kerem Ataç | TSK-46 to TSK-52 |
| US-K | Objective scoring | 8 | Kerem Ataç | TSK-53 to TSK-59 |
| US-L | Manual grading | 5 | Kerem Ataç | TSK-60 to TSK-63 |
| US-M | Reset activity | 5 | Kerem Ataç | TSK-64 to TSK-68 |
| Export | Export scores | 3 | Kerem Ataç | TSK-69 to TSK-71 |

## Task Breakdown Summary

### US-G Update Activity
- TSK-41 Implement updateActivity()
- TSK-42 Allow only activity_text and learning_objectives patch
- TSK-43 Reject empty patch
- TSK-44 Reject non-existent activity
- TSK-45 Test update cases

### US-J Tutoring Flow
- TSK-46 Create student_progress table
- TSK-47 Store conversation history
- TSK-48 Implement first tutoring response
- TSK-49 Implement one-question-at-a-time logic
- TSK-50 Integrate OpenRouter/LLM call
- TSK-51 Block tutoring if activity ENDED
- TSK-52 Test tutoring flow manually

### US-K Objective Scoring
- TSK-53 Create score_logs table
- TSK-54 Track achieved objectives
- TSK-55 Implement +1 first-time objective scoring
- TSK-56 Prevent duplicate objective scoring
- TSK-57 Add mini-lesson response
- TSK-58 Add completion celebration
- TSK-59 Test score and duplicate cases

### US-L Manual Grading
- TSK-60 Implement manual grade helper
- TSK-61 Log manual grading event
- TSK-62 Enforce instructor authorization
- TSK-63 Test manual grade unauthorized case

### US-M Reset Activity
- TSK-64 Implement resetActivity()
- TSK-65 Delete score_logs for activity
- TSK-66 Delete/reset student_progress
- TSK-67 Set activity ENDED
- TSK-68 Test reset blocks new score logs

### Export Scores
- TSK-69 Implement exportScores()
- TSK-70 Generate CSV string or file path
- TSK-71 Test exported columns

## Decisions Made
- Sprint 2 will build on the completed Sprint 1 activity lifecycle.
- Update/reset/export are implemented in services.py first, with FastAPI routes in main.py.
- Objective scoring will be deterministic enough for tests and can later be connected to LLM tutoring.
- Prompt changes will be documented only if the baseline tutoring prompt is modified.

## Definition of Done Confirmed
Confirmed by: Kerem Ataç
