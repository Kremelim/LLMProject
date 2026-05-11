# Sprint 2 Review

Date       : 2026-05-12
Attendees  : Kerem Ataç
Facilitator: Kerem Ataç
Duration   : 45 minutes
Format     : Solo compressed sprint evidence

## Sprint Goal
By the end of Sprint 2, the system can update activities, support the student tutoring flow,
score objectives only once, export scores, support manual grading, and reset activities safely.

## Sprint Goal Achieved?
YES.

## Stories Completed

| Story | SP | Demo Notes |
|-------|----|------------|
| US-G | 5 | Instructor can update activity text and learning objectives. |
| US-J | 8 | Student tutoring flow stores conversation history and asks one question at a time. |
| US-K | 8 | Objective scoring gives +1 first time only, prevents duplicates, logs metadata, gives mini-lesson, and celebrates completion. |
| US-L | 5 | Instructor can manually grade exceptions with MANUAL score log event. |
| US-M | 5 | Instructor can reset activity, delete scores/progress, and set activity ENDED. |
| Export | 3 | Instructor can export score logs as CSV. |
| TECH | 1 | Password change and student password reset APIs were completed. |

## Stories Not Completed

| Story | SP | Reason | Action |
|-------|----|--------|--------|
| None | 0 | Sprint 2 committed scope completed. | No carry-over. |

## What Was Demo'd
- Instructor updates an activity.
- Student starts tutoring on ACTIVE activity.
- System asks exactly one question per step.
- Objective achievement gives +1 score.
- Repeating the same objective does not add another point.
- Score logs are written with metadata.
- Mini-lesson appears after earning a point.
- Completion celebration appears after all objectives are achieved.
- Manual grading creates MANUAL score log.
- Reset deletes progress/scores and sets activity ENDED.
- Export scores returns CSV columns.
- Password management APIs work.

## Board Screenshot
File: G00_S2_BOARD_FINAL_2026-05-12.png

## SP Summary

| | SP |
|--|----|
| Committed | 35 |
| Completed | 35 |
| Carried over | 0 |
