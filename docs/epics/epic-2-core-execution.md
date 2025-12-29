# Epic 2: Core Test Management & Execution
**Status**: Planned
**Owner**: Bob (SM)

## Description
This epic focuses on delivering the core value of WebuiTester: the ability to create test cases via the UI and execute them using the AI Agent. It bridges the gap between the static database/UI foundation (Epic 1) and a functional testing tool.

## Goals
1.  **Test Case Editor**: A fully functional UI for creating, editing, and managing test cases (connecting Frontend to Backend CRUD).
2.  **Agent Execution Engine**: Implement the core `Agent` class that can interpret steps and drive the browser using Playwright.
3.  **Real-time Feedback**: Stream execution logs ("Thought", "Action") and screenshots from Backend to Frontend via WebSockets.
4.  **Configuration**: Allow users to configure LLM settings (OpenAI/Ollama) via the UI.

## User Stories
| ID | Title | Priority | Status |
| :--- | :--- | :--- | :--- |
| **2.1** | [Test Case Editor UI](../stories/2.1.test-case-editor.story.md) | High | **Pending** |
| **2.2** | [Agent Execution Engine (V1)](../stories/2.2.agent-execution-engine.story.md) | High | **Pending** |
| **2.3** | [Real-time Log Streaming](../stories/2.3.log-streaming.story.md) | Medium | **Pending** |
| **2.4** | [Settings & Configuration](../stories/2.4.settings-configuration.story.md) | Low | **Pending** |

## Risks & Dependencies
*   **Risk**: WebSocket stability for real-time logs.
*   **Risk**: AI Agent reliability (parsing instructions correctly).
*   **Dependency**: Epic 1 (Backend API & Frontend Layout) must be stable.

## Definition of Done (DoD)
*   [ ] Users can create a multi-step test case in the UI.
*   [ ] Users can click "Run" and watch the agent execute the test.
*   [ ] Execution logs are visible in the "Console" panel.
*   [ ] Screenshots are captured and displayed after each step.
