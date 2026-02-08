# Feature Specification: FastAPI Todo Backend

**Feature Branch**: `003-fastapi-todo-backend`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "# Objective
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
- Protected route handlers in `routes/`."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Task Management (Priority: P1)

As an authenticated user, I want to securely create, view, update, and delete my personal tasks so that I can manage my to-do list while ensuring my data remains private from other users.

**Why this priority**: This is the core functionality of the todo application. Without secure CRUD operations for tasks, the application has no value to users.

**Independent Test**: Can be fully tested by logging in as a user, creating tasks, viewing them, updating them, and deleting them. The system should prevent access to other users' tasks even if the user knows the task ID.

**Acceptance Scenarios**:

1. **Given** user is authenticated with valid JWT token, **When** user requests to create a new task, **Then** the task is created and associated with the user's ID
2. **Given** user is authenticated with valid JWT token, **When** user requests to view their tasks, **Then** only tasks belonging to that user are returned
3. **Given** user is authenticated with valid JWT token, **When** user attempts to access another user's task by guessing the ID, **Then** the system returns a 403 Forbidden error

---

### User Story 2 - Task Completion Toggle (Priority: P2)

As an authenticated user, I want to mark my tasks as completed or incomplete so that I can track my progress and organize my todo list.

**Why this priority**: This is a fundamental feature of todo applications that enhances user experience by allowing task status management.

**Independent Test**: Can be fully tested by creating a task, toggling its completion status, and verifying the status change is persisted.

**Acceptance Scenarios**:

1. **Given** user has a task, **When** user sends PATCH request to toggle completion status, **Then** the task's completion status is flipped and saved

---

### User Story 3 - Secure Authentication Integration (Priority: P3)

As a user of the application, I want the backend to properly validate my JWT token so that my identity is verified before performing any operations.

**Why this priority**: Security is critical to protect user data. Without proper authentication, the entire system is vulnerable.

**Independent Test**: Can be tested by sending requests with valid tokens (should succeed), invalid tokens (should fail with 401), and missing tokens (should fail with 401).

**Acceptance Scenarios**:

1. **Given** user has a valid JWT token, **When** user makes API request with Authorization header, **Then** the request is processed with the user's identity established
2. **Given** user has an invalid or expired JWT token, **When** user makes API request with Authorization header, **Then** the system returns a 401 Unauthorized error

---

### Edge Cases

- What happens when a user attempts to access a non-existent task ID?
- How does the system handle malformed JWT tokens?
- What occurs when the database is temporarily unavailable?
- How does the system behave when a user attempts to modify another user's task using their own token?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST verify JWT tokens from the Authorization: Bearer <token> header using the BETTER_AUTH_SECRET
- **FR-002**: System MUST extract user_id from validated JWT tokens and use it for request context
- **FR-003**: System MUST store task data with id, user_id, title, description, completed status, created_at, and updated_at fields
- **FR-004**: System MUST allow users to create tasks via POST /api/{user_id}/tasks endpoint
- **FR-005**: System MUST allow users to retrieve their tasks via GET /api/{user_id}/tasks endpoint
- **FR-006**: System MUST allow users to update task details via PUT /api/{user_id}/tasks/{id} endpoint
- **FR-007**: System MUST allow users to delete tasks via DELETE /api/{user_id}/tasks/{id} endpoint
- **FR-008**: System MUST allow users to toggle task completion via PATCH /api/{user_id}/tasks/{id}/complete endpoint
- **FR-009**: System MUST enforce user isolation by filtering all queries by user_id
- **FR-010**: System MUST return appropriate HTTP status codes (401 for auth failure, 403 for forbidden access, 404 for not found)
- **FR-011**: System MUST validate request bodies using Pydantic models
- **FR-012**: System MUST configure CORS to allow requests from http://localhost:3000
- **FR-013**: System MUST use Neon PostgreSQL database with SQLModel ORM

### Key Entities *(include if feature involves data)*

- **Task**: Represents a user's to-do item with properties: id (unique identifier), user_id (foreign key linking to user), title (task name), description (optional details), completed (boolean status), created_at (timestamp), updated_at (timestamp)
- **User**: Represents an authenticated user with user_id (unique identifier) that serves as foreign key for tasks

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can securely create, read, update, and delete their own tasks with 99% success rate
- **SC-002**: System prevents unauthorized access to other users' tasks with 100% success rate (zero data leakage between users)
- **SC-003**: API responds to authenticated requests in under 1 second for 95% of requests
- **SC-004**: Authentication validation occurs in under 200ms for 95% of requests
- **SC-005**: Frontend application can successfully integrate with all backend endpoints with zero CORS errors
