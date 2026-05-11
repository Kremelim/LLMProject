# Sprint 1 Review

Date       : 2026-05-11
Attendees  : Kerem Ataç
Facilitator: Kerem Ataç
Duration   : 45 minutes
Format     : Solo compressed sprint evidence

## Sprint Goal
By the end of Sprint 1, the system can authenticate instructors and students,
enforce server-side role and course authorization, allow instructors to manage
basic activities, and allow students to access activity content only while the
activity is ACTIVE.

## Sprint Goal Achieved?
YES.

## Stories Completed

| Story | SP | Demo Notes |
|-------|----|------------|
| US-A | 3 | Instructor password setup and login implemented and manually tested. |
| US-B | 3 | Student password setup and login implemented and manually tested. |
| US-C | 5 | Server-side role and course authorization helpers implemented. |
| US-D | 3 | Instructor can list only assigned courses. |
| US-E | 3 | Instructor can list activities in deterministic order. |
| US-F | 5 | Instructor can create activity with required validation and duplicate rejection. |
| US-H | 5 | Instructor can start/end activity; ENDED activity blocks score logging. |
| US-I | 5 | Student can access only ACTIVE activity and cannot see learning objectives. |

## Stories Not Completed

| Story | SP | Reason | Action |
|-------|----|--------|--------|
| US-G | 5 | Planned for Sprint 2 to keep Sprint 1 focused on core activity flow. | Move to Sprint 2 backlog. |
| US-J | 8 | Requires LLM tutoring flow and conversation state. | Move to Sprint 2 backlog. |
| US-K | 8 | Depends on tutoring/progress logic. | Move to Sprint 2 backlog. |
| US-L | 5 | Exception grading is less critical than Sprint 1 access control. | Move to Sprint 2 backlog. |
| US-M | 5 | Reset depends on score/progress behavior. | Move to Sprint 2 backlog. |

## What Was Demo'd
- Instructor login with valid and invalid credentials.
- Student login with valid and invalid credentials.
- Instructor listing assigned courses only.
- Instructor listing course activities.
- Instructor creating an activity.
- Instructor starting and ending an activity.
- Student accessing an ACTIVE activity.
- Student being blocked from NOT_STARTED, ENDED, and unauthorized activities.
- Student response does not expose learning objectives.

## Feedback / Observations
- Supabase pooler connection was more reliable than direct database connection.
- Keeping all business logic in services.py made tests easier.
- Scope log needed consistent TSK task IDs; this was corrected during Sprint 1.

## Board Screenshot
File: G00_S1_BOARD_FINAL_2026-05-11.png

## SP Summary

| | SP |
|--|----|
| Committed | 32 |
| Completed | 32 |
| Carried over | 0 from Sprint 1 scope |
