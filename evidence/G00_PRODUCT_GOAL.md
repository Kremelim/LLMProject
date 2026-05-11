# Product Goal

## System Name
InClass LLM Platform

## Product Goal Statement
Build and deliver a working classroom activity system where instructors can create,
manage, start, end, and reset activities for their assigned courses; students can
access only authorized and ACTIVE activities; and the system supports LLM-guided
tutoring with objective-based scoring that is logged correctly and transparently.

## Who It Serves
- Instructors: need to prepare, open, monitor, close, export, and reset class activities.
- Students: need to access active classroom activities and receive guided tutoring.

## What Success Looks Like
- Instructor can authenticate and list only assigned courses.
- Instructor can create, list, update, start, end, reset, and export activity scores.
- Student can authenticate and access activity content only while the activity is ACTIVE.
- Learning objectives are never exposed directly to students.
- Tutoring flow asks one guiding question at a time.
- First achievement of each objective gives exactly +1 score.
- Repeated achievement of the same objective does not increase score again.
- Every score change is logged with metadata.
- Instructor can export scores as CSV.
