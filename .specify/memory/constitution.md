<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Modified principles: All 6 principles completely redefined for Hackathon II Todo App
- Added sections: Technical Stack Sovereignty, Security & Authentication, Database & Data Integrity, Frontend Guidelines
- Removed sections: None (completely replaced template)
- Templates requiring updates: ⚠ pending - .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md
- Follow-up TODOs: None
-->

# Hackathon II Todo App Constitution

## Core Principles

### Full-Stack Integration
All implementation must strictly follow the designated technology stack: Next.js 16+ (App Router), TypeScript, Tailwind CSS for frontend; Python FastAPI, SQLModel (ORM) for backend; Neon Serverless PostgreSQL for database; Better Auth with JWT Bridge for authentication.

### Spec-First Protocol
Before any code change, read the relevant specification in `/specs/`. If a feature is not in the specs, do not implement it. If code and specs conflict, the specs (@specs/) always win.

### Monorepo Discipline
Maintain strict separation between `/frontend` and `/backend`. Use the root `CLAUDE.md` as the primary project map. NO code implementation outside of specified `/frontend` or `/backend` directories.

### JWT Bridge Security
Implement shared secret authentication using `BETTER_AUTH_SECRET` in both stacks for JWT signing and verification. Backend middleware must intercept headers, verify `Authorization: Bearer <token>`, and decode the payload. EVERY database query must be filtered by the `user_id` extracted from the JWT. Cross-user data access is a critical security failure.

### Statelessness
The backend must remain stateless. Do not store session data in memory; rely on the JWT and database. Return a 401 Unauthorized response for any request without a valid token.

### SQLModel Data Integrity
Use SQLModel for all database operations and Pydantic validation. Tables must match `@specs/database/schema.md` exactly, including foreign key relationships (tasks.user_id -> users.id).

## Technical Stack Sovereignty
- **Frontend:** Next.js 16+ (App Router), TypeScript, Tailwind CSS.
- **Backend:** Python FastAPI, SQLModel (ORM).
- **Database:** Neon Serverless PostgreSQL.
- **Authentication:** Better Auth (Frontend) with JWT Bridge (Backend).
- NO deviation from the RESTful API endpoint structure defined in the project document.

## Security & Authentication
- **Shared Secret:** Use `BETTER_AUTH_SECRET` in both stacks for JWT signing and verification.
- **Backend Middleware:** Implement a security dependency in FastAPI to intercept headers, verify `Authorization: Bearer <token>`, and decode the payload.
- **User Isolation:** EVERY database query must be filtered by the `user_id` extracted from the JWT. Cross-user data access is a critical security failure.
- **Unauthorized Access:** Return a 401 Unauthorized response for any request without a valid token.
- NO hardcoded secrets. Use environment variables.

## Database & Data Integrity
- **SQLModel Usage:** Use SQLModel for all database operations and Pydantic validation.
- **Schema Mapping:** Tables must match `@specs/database/schema.md` exactly, including foreign key relationships (tasks.user_id -> users.id).
- **Statelessness:** The backend must remain stateless. Do not store session data in memory; rely on the JWT and database.

## Frontend Guidelines
- **App Router:** Follow Next.js 16 conventions (loading.tsx, error.tsx, layout.tsx).
- **API Client:** All requests must pass through a centralized API client in `lib/api.ts` that attaches the JWT token automatically.
- **UX Standards:** Implement "Optimistic UI" updates where possible and ensure 100% responsive design using Tailwind CSS.

## Development Workflow
1. **Analyze:** Read the feature spec: `@specs/features/[feature].md`.
2. **Draft:** Plan changes in the Backend first, then the Frontend.
3. **Execute:** Implement logic following the sub-directory `CLAUDE.md` guidelines.
4. **Test:** Verify user isolation and error states.

## Governance
As a Lead Full-Stack Engineer and Architect, you must execute Phase II: "Full-Stack Web Application" with a strict Spec-Driven Development (SDD) approach. You must ensure seamless integration between the Next.js frontend, FastAPI backend, and Neon PostgreSQL database. All changes must be verified for compliance with these principles.

**Version**: 1.1.0 | **Ratified**: 2026-01-30 | **Last Amended**: 2026-01-30
