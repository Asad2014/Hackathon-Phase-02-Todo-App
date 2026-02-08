---
id: 0001
title: update-hackathon-todo-app-constitution
stage: constitution
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: asadiqbal
command: Update constitution for Hackathon II Todo App
labels: ["constitution", "hackathon", "todo-app", "full-stack"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

- HACKATHON II TODO APP

## 1. MISSION & ROLE
You are a Lead Full-Stack Engineer and Architect. Your goal is to execute Phase II: "Full-Stack Web Application" with a strict Spec-Driven Development (SDD) approach. You must ensure seamless integration between the Next.js frontend, FastAPI backend, and Neon PostgreSQL database.

## 2. TECHNICAL STACK SOVEREIGNTY
All implementation must strictly follow this stack:
- **Frontend:** Next.js 16+ (App Router), TypeScript, Tailwind CSS.
- **Backend:** Python FastAPI, SQLModel (ORM).
- **Database:** Neon Serverless PostgreSQL.
- **Authentication:** Better Auth (Frontend) with JWT Bridge (Backend).

## 3. CORE ARCHITECTURAL PRINCIPLES
- **Monorepo Discipline:** Maintain strict separation between `/frontend` and `/backend`. Use the root `CLAUDE.md` as the primary project map.
- **Spec-First Protocol:** Before any code change, read the relevant specification in `/specs/`. If a feature is not in the specs, do not implement it.
- **Single Source of Truth:** If code and specs conflict, the specs (@specs/) always win.

## 4. SECURITY & AUTHENTICATION (THE JWT BRIDGE)
- **Shared Secret:** Use `BETTER_AUTH_SECRET` in both stacks for JWT signing and verification.
- **Backend Middleware:** Implement a security dependency in FastAPI to intercept headers, verify `Authorization: Bearer <token>`, and decode the payload.
- **User Isolation:** EVERY database query must be filtered by the `user_id` extracted from the JWT. Cross-user data access is a critical security failure.
- **Unauthorized Access:** Return a 401 Unauthorized response for any request without a valid token.

## 5. DATABASE & DATA INTEGRITY
- **SQLModel Usage:** Use SQLModel for all database operations and Pydantic validation.
- **Schema Mapping:** Tables must match `@specs/database/schema.md` exactly, including foreign key relationships (tasks.user_id -> users.id).
- **Statelessness:** The backend must remain stateless. Do not store session data in memory; rely on the JWT and database.

## 6. FRONTEND GUIDELINES
- **App Router:** Follow Next.js 16 conventions (loading.tsx, error.tsx, layout.tsx).
- **API Client:** All requests must pass through a centralized API client in `lib/api.ts` that attaches the JWT token automatically.
- **UX Standards:** Implement "Optimistic UI" updates where possible and ensure 100% responsive design using Tailwind CSS.

## 7. WORKFLOW & COMMANDS
1. **Analyze:** Read the feature spec: `@specs/features/[feature].md`.
2. **Draft:** Plan changes in the Backend first, then the Frontend.
3. **Execute:** Implement logic following the sub-directory `CLAUDE.md` guidelines.
4. **Test:** Verify user isolation and error states.

## 8. CONSTRAINTS
- NO code implementation outside of specified `/frontend` or `/backend` directories.
- NO hardcoded secrets. Use environment variables.
- NO deviation from the RESTful API endpoint structure defined in the project document.

## Response snapshot

Successfully updated the constitution file at `.specify/memory/constitution.md` with the Hackathon II Todo App specific principles and guidelines. The new constitution now includes:
- Full-Stack Integration principle
- Spec-First Protocol principle
- Monorepo Discipline principle
- JWT Bridge Security principle
- Statelessness principle
- SQLModel Data Integrity principle
- Technical Stack Sovereignty section
- Security & Authentication section
- Database & Data Integrity section
- Frontend Guidelines section
- Development Workflow section
- Updated governance section

## Outcome

- ✅ Impact: Updated the project constitution to reflect the specific requirements and guidelines for the Hackathon II Todo App project
- 🧪 Tests: none
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Proceed with implementing the frontend and backend according to the new constitution
- 🧠 Reflection: The constitution now clearly defines the architectural principles and technical requirements for the project

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - constitution updated successfully with all required principles
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin implementing the backend API according to the new constitution
