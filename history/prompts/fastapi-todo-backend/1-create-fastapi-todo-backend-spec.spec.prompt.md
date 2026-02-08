---
id: 1
title: create-fastapi-todo-backend-spec
stage: spec
date_iso: 2026-01-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: fastapi-todo-backend
branch: 003-fastapi-todo-backend
user: claude
command: /sp.specify
labels: ["specification", "fastapi", "backend", "todo-app"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - specs/003-fastapi-todo-backend/spec.md
  - specs/003-fastapi-todo-backend/checklists/requirements.md
tests_yaml: []
---

# Create FastAPI Todo Backend Specification

## Prompt Text
```
# Objective
Implement a robust, secure, and production-ready FastAPI backend for Phase II: Full-Stack Todo Application. The backend must integrate seamlessly with the existing Next.js frontend and the Neon PostgreSQL database.

# Technical Stack & Environment
- **Framework:** FastAPI (Python).
- **ORM:** SQLModel (for Pydantic + SQLAlchemy synergy).
- **Database:** Neon Serverless PostgreSQL (using provided NEON_DB_URL).
- **Auth Strategy:** JWT-based stateless authentication compatible with Better Auth.
- **Environment Variables:**
  - `DATABASE_URL`: postgresql://neondb_owner:npg_oesqnFNCt12u@ep-billowing-lab-a13iu7ll-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
  - `BETTER_AUTH_SECRET`: 5mhHToIaFowGOPHmN7LJcgW4xE9fM05E
  - `BETTER_AUTH_URL`: http://localhost:3000/

# Core Backend Features
1. **JWT Verification Middleware:**
   - Create a dependency to extract the JWT from the `Authorization: Bearer <token>` header.
   - Use the `BETTER_AUTH_SECRET` to verify the token signature.
   - Extract `user_id` and inject it into the request context.

2. **Database Schema (SQLModel):**
   - **User Table:** (Reference for foreign keys).
   - **Task Table:** Must include `id`, `user_id` (String/UUID), `title`, `description`, `completed` (Boolean), `created_at`, and `updated_at`.

3. **RESTful API Endpoints (Strictly Followed):**
   - `GET /api/{user_id}/tasks`: List only the tasks belonging to the authenticated user.
   - `POST /api/{user_id}/tasks`: Create a task linked to the authenticated user.
   - `PUT /api/{user_id}/tasks/{id}`: Update task details (Verify ownership first).
   - `DELETE /api/{user_id}/tasks/{id}`: Remove task (Verify ownership first).
   - `PATCH /api/{user_id}/tasks/{id}/complete`: Toggle completion status.

# Integration & Security Rules
- **User Isolation:** EVERY query must explicitly filter by `user_id`. Prevent any user from accessing another's data even if they guess the Task ID.
- **CORS Configuration:** Allow requests from `http://localhost:3000`.
- **Error Handling:** Use standard HTTP status codes (401 for Auth failure, 403 for Forbidden access, 404 for Not Found).
- **Validation:** Use Pydantic models for strict request body validation.

# Deliverables
- Fully functional FastAPI server in the `/backend` directory.
- Database connection logic in `db.py`.
- SQLModel definitions in `models.py`.
- Protected route handlers in `routes/`.
```

## Response Text
Created feature branch `003-fastapi-todo-backend` and developed a comprehensive specification for the FastAPI Todo Backend. The spec includes user scenarios, functional requirements, key entities, and success criteria focusing on secure task management with JWT authentication and user isolation. A quality checklist was also created to validate the specification.

## Outcome
Successfully created the feature specification for the FastAPI Todo Backend with all required sections including user stories, functional requirements, and measurable success criteria. The specification is ready for the planning phase.