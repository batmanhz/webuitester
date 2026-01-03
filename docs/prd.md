# WebuiTester Product Requirements Document (PRD)

## 1. Goals and Background Context

### 1.1 Goals
*   **Reduce Maintenance Costs**: Enable QA engineers to maintain test cases in structured natural language (text), eliminating the need to update code/selectors when UI implementation details change.
*   **Lower Barrier to Entry**: Provide a web-based interface where users can simply input text instructions to run automated tests without Python/Playwright knowledge.
*   **Hybrid Model Flexibility**: Support both commercial APIs (OpenAI/DeepSeek) for high-precision tasks and local models (Ollama) for data privacy/offline use.
*   **Visual Feedback & Verification**: Provide clear, visual test reports (screenshots/logs) for every step, specifically verifying "Pass/Fail" states automatically based on expected results.

### 1.2 Background Context
Traditional automation frameworks like Selenium or Playwright rely heavily on rigid selectors (CSS/XPath). In agile development, frequent UI changes break these scripts, causing "flaky tests" and high maintenance overhead. **WebuiTester** solves this by using an AI Agent as the execution engine. The Agent interprets the intent of a text-based test case and dynamically interacts with the Web UI, adapting to changes in real-time. This project aims to deliver a local, secure, and user-friendly tool to streamline regression testing.

### 1.3 Change Log
| Date       | Version | Description                          | Author    |
| :--------- | :------ | :----------------------------------- | :-------- |
| 2025-12-27 | 1.0     | Initial Baseline (Structured Inputs) | John (PM) |

## 2. Requirements

### 2.1 Functional Requirements (FR)

*   **FR1: 2-Step Test Case Creation Workflow (New)**
    *   **Phase 1: Intent Definition**:
        *   User inputs a natural language description of the test intent (e.g., "Login to Gmail and check the first email").
        *   User inputs the Target URL.
    *   **Phase 2: AI-Assisted Generation**:
        *   System calls an AI Agent to analyze the intent and automatically generate structured test steps.
        *   **Output**: A structured test case (Name, URL, List of Steps with Instructions and Expected Results).
    *   **Phase 3: Manual Refinement**:
        *   User reviews the generated steps in a structured editor.
        *   User can manually add, edit, reorder, or delete steps.
        *   User saves the final test case to the database.

*   **FR2: Agent Configuration**
    *   Support configuration of LLM Backend:
        *   **Generic OpenAI Compatible**: Configurable `api_key`, `base_url`, `model_name` to support Cloud (OpenAI, DeepSeek) or Local (Ollama, LM Studio) providers.
    *   Support Browser Mode toggling: Headless (fast) vs Headed (visible).

*   **FR3: Intelligent Execution Engine**
    *   The Agent must parse the structured steps sequentially.
    *   **Capabilities**:
        *   Navigate to URLs.
        *   Locate elements semantically (buttons, inputs, links) without pre-defined selectors.
        *   Perform actions: Click, Type, Select, Scroll.
        *   Auto-retry mechanism: If an action fails, analyze DOM and retry once.

*   **FR4: Verification & Reporting**
    *   **Step-by-Step Visualization**: Capture screenshots after each step execution.
    *   **Assertion**: At the end of execution, compare the final page state (text/screenshot) against the "Expected Result" using the LLM.
    *   **Streaming Logs**: Display real-time "Thought" and "Action" logs from the Agent.

### 2.2 Non-Functional Requirements (NFR)

*   **NFR1: Responsiveness**: AI inference time per step should aim for <5s (Cloud) or reasonable latency (Local). UI must show loading states during execution.
*   **NFR2: Deployability**: Support Docker containerization for one-click local deployment. Support standard Python source deployment.
*   **NFR3: Data Privacy**: API Keys and test case data must remain local (SQLite/LocalStorage). No external upload except necessary LLM API calls.

## 3. User Interface Design Goals

*   **Layout Strategy**: Split-View (Left: Editor / Right: Execution & Feedback).
*   **Theme**: Professional Dark Mode (IDE/Developer Tool aesthetic).
*   **Interaction**: Real-time log streaming (Console style) and image updates.
*   **Input Style**: Form-based structure (not free-form text block) to ensure test stability.

## 4. Technical Assumptions

*   **Frontend**: Vue 3 + Element Plus (or Naive UI).
*   **Backend**: Python FastAPI.
*   **Database**: SQLite (via SQLAlchemy or Tortoise ORM).
*   **Core Engine**: Playwright (Python) + LangChain/Browser-use.
*   **LLM Interface**: OpenAI SDK compatible (supports both OpenAI and Ollama).