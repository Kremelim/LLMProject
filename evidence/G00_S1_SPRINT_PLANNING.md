# Sprint 1 Planning Record

Date       : 2026-05-11
Duration   : 1 hour
Attendees  : Kerem Ataç
Facilitator: Kerem Ataç
Location   : Individual / local setup

## Sprint Goal
By the end of Sprint 1, the system can authenticate instructors and students,
enforce server-side role and course authorization, allow instructors to manage
basic activities, and allow students to access activity content only while the
activity is ACTIVE.

## Stories Selected for This Sprint

| Story | Description | SP | Owner | ClickUp Task IDs |
|-------|-------------|----|-------|------------------|
| US-A | Instructor auth | 3 | Kerem Ataç | ClickUp task/subtasks created |
| US-B | Student auth | 3 | Kerem Ataç | ClickUp task/subtasks created |
| US-C | Role/course authorization | 5 | Kerem Ataç | ClickUp task/subtasks created |
| US-D | List assigned courses | 3 | Kerem Ataç | ClickUp task/subtasks created |
| US-E | List activities | 3 | Kerem Ataç | ClickUp task/subtasks created |
| US-F | Create activity | 5 | Kerem Ataç | ClickUp task/subtasks created |
| US-H | Start/end activity | 5 | Kerem Ataç | ClickUp task/subtasks created |
| US-I | Student ACTIVE activity access | 5 | Kerem Ataç | ClickUp task/subtasks created |

## Task Breakdown Summary

### Setup
- Create required repository structure.
- Create app/, tests/, instructor_tests/, evidence/ folders.
- Add requirements.txt, .gitignore, .env.example, README.md.
- Add initial FastAPI app in app/main.py.
- Add required API function signatures in app/services.py.
- Add smoke test under tests/.

### US-A Instructor Auth
- Create users table in Supabase.
- Seed instructor users.
- Implement setInstructorPassword().
- Implement instructorLogin().
- Add tests for valid and invalid instructor login.

### US-B Student Auth
- Seed student users.
- Implement setStudentPassword().
- Implement studentLogin().
- Add tests for valid and invalid student login.

### US-C Role/Course Authorization
- Create courses and course_enrollments tables.
- Implement helper functions for credential validation.
- Implement server-side role checks.
- Implement server-side course access checks.
- Test unauthorized access.

### US-D List Assigned Courses
- Implement listMyCourses().
- Return only courses assigned to the instructor.
- Reject invalid credentials.

### US-E List Activities
- Create activities table.
- Implement listActivities().
- Return activity_no and status in deterministic order.

### US-F Create Activity
- Implement createActivity().
- Validate required fields.
- Reject duplicate activity_no in same course.

### US-H Start/End Activity
- Implement startActivity().
- Implement endActivity().
- Ensure ENDED activities cannot accept score logs.

### US-I Student ACTIVE Activity Access
- Implement getActivity().
- Allow only ACTIVE activities.
- Hide learning_objectives from student response.
- Reject non-enrolled student.

## Decisions Made
- The project will use Python, FastAPI, PostgreSQL/Supabase, and pytest.
- Business logic will be placed in app/services.py.
- FastAPI app object will be exposed from app/main.py.
- Secrets will be stored locally in .env and never committed.
- Initial Sprint 1 commitment is 32 SP, leaving 3 SP buffer.

## Definition of Done Confirmed
Confirmed by: Kerem Ataç
