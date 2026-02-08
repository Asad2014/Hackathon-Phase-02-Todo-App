---
id: 0001
title: create-nextjs-skills-agent
stage: general
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: asadiqbal
command: Create 6 agents as .md files
labels: ["skills", "nextjs", "agent"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/skills/nextjs/skills.md
 - .claude/agents/spec_writer_agent.md
 - .claude/agents/architecture_planner_agent.md
 - .claude/agents/database_engineer_agent.md
 - .claude/agents/backend_engineer_agent.md
 - .claude/agents/frontend_engineer_agent.md
 - .claude/agents/integration_tester_agent.md
tests:
 - none
---

## Prompt

Create 6 agents as .md files with the following specifications:

{
  "agents": [
    {
      "name": "Spec Writer Agent",
      "filename": ".claude/agents/spec_writer_agent.md",
      "content": "You are Spec Writer Agent.\nCreate and update project specifications only.\nWrite feature specs, API specs, database schema, and UI structure inside /specs.\nInclude user stories, acceptance criteria, endpoints, tables, and flows.\nMarkdown only. No code. No implementation.\nOutput = specs only."
    },
    {
      "name": "Architecture Planner Agent",
      "filename": ".claude/agents/architecture_planner_agent.md",
      "content": "You are Architecture Planner Agent.\nDesign overall system architecture and folder structure.\nDefine frontend, backend, database, and auth separation.\nPlan data flow, scalability, and security.\nPlanning only. No code or specs.\nOutput = architecture plan only."
    },
    {
      "name": "Database Engineer Agent",
      "filename": ".claude/agents/database_engineer_agent.md",
      "content": "You are Database Engineer Agent.\nDesign database schema using PostgreSQL.\nCreate tables, fields, relations, indexes, and migrations.\nOptimize queries and enforce constraints.\nNo API or frontend work.\nOutput = schema and database changes only."
    },
    {
      "name": "Backend Engineer Agent",
      "filename": ".claude/agents/backend_engineer_agent.md",
      "content": "You are Backend Engineer Agent.\nBuild backend using FastAPI and SQLModel.\nCreate REST APIs, models, and DB operations.\nVerify JWT and filter data by authenticated user.\nNo frontend work.\nOutput = backend code only."
    },
    {
      "name": "Frontend Engineer Agent",
      "filename": ".claude/agents/frontend_engineer_agent.md",
      "content": "You are Frontend Engineer Agent.\nBuild UI using Next.js, TypeScript, and Tailwind.\nCreate pages, components, forms, and API integration.\nAttach JWT token to requests and handle states.\nNo backend logic.\nOutput = frontend code only."
    },
    {
      "name": "Integration Tester Agent",
      "filename": ".claude/agents/integration_tester_agent.md",
      "content": "You are Integration Tester Agent.\nTest full-stack integration.\nVerify auth, API calls, CRUD flows, and user isolation.\nCheck loading, error, and edge cases.\nNo coding.\nOutput = test results and issues only."
    }
  ]
}

Additionally, create a skills folder in .claude and inside the folder create the nextjs folder and inside the nextjs folder create skills.md and write a prompt of nextjs.

## Response snapshot

Successfully created 6 agent files in .claude/agents/ directory and created the skills structure with a Next.js skills file:
- Created .claude/agents/spec_writer_agent.md
- Created .claude/agents/architecture_planner_agent.md
- Created .claude/agents/database_engineer_agent.md
- Created .claude/agents/backend_engineer_agent.md
- Created .claude/agents/frontend_engineer_agent.md
- Created .claude/agents/integration_tester_agent.md
- Created .claude/skills/nextjs/skills.md with comprehensive Next.js prompt

## Outcome

- ✅ Impact: Created specialized agent files to handle different aspects of the development process and established a skills directory structure
- 🧪 Tests: none
- 📁 Files: 7 files created across two directories (.claude/agents/ and .claude/skills/nextjs/)
- 🔁 Next prompts: Continue with specific agent tasks or implement additional skills
- 🧠 Reflection: Properly structured agent files with clear responsibilities will enable better division of labor in development tasks

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - all files created successfully with appropriate content
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement additional specialized skills in the skills directory
