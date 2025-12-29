# Epic 1: Initial Setup & Foundation
**Status**: In Progress
**Owner**: Bob (SM)

## Description
This epic establishes the technical foundation for WebuiTester. It includes setting up the monorepo structure, initializing the backend (FastAPI) and frontend (Vue 3) frameworks, defining the core database schema, and creating the basic UI shell.

## Goals
1.  **Project Skeleton**: A functional monorepo with Backend and Frontend running locally.
2.  **Database**: A local SQLite database with the core schema (`TestCase`, `TestRun`) ready for data persistence.
3.  **Frontend Shell**: The "IDE-like" split-view layout implemented and ready for feature development.
4.  **Agent Core**: Basic Python module structure for the AI agent.

## User Stories
| ID | Title | Status |
| :--- | :--- | :--- |
| **1.1** | [Project Skeleton & Core Dependencies](../stories/1.1.project-skeleton.story.md) | **Draft** |
| **1.2** | [Database Schema & Basic CRUD API](../stories/1.2.database-schema.story.md) | **Draft** |
| **1.3** | [Frontend Foundation & Layout](../stories/1.3.frontend-foundation.story.md) | **Draft** |

## Risks & Dependencies
*   **Risk**: Ensuring `playwright` installs correctly in the local environment (browsers can be heavy).
*   **Dependency**: None. This is the root dependency.

## Definition of Done (DoD)
*   [ ] All stories completed and verified.
*   [ ] Backend API is accessible at `http://localhost:19000/docs`.
*   [ ] Frontend is accessible at `http://localhost:5173`.
*   [ ] Database is initialized (`webuitester.db` exists).
*   [ ] CI/CD (local pre-commit) is configured.
