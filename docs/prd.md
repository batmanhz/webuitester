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

*   **FR1: Structured Test Case Management**
    *   The system must provide a structured editor for creating and editing test cases.
    *   **Input Structure Definition**:
        1.  **Pre-conditions (前置输入)**: Must capture Target URL (Required) and optional context (Cookies/Tokens).
        2.  **Test Steps (测试步骤)**: An ordered list of natural language instructions (e.g., "Step 1: Input 'admin' in username field").
        3.  **Expected Result (预期结果)**: A clear descriptive statement for validation (e.g., "Success notification appears").
    *   Data persistence using a local database (SQLite).

*   **FR2: Agent Configuration**
    *   Support configuration of LLM Backend:
        *   **Cloud Mode**: API Key + Base URL (OpenAI standard).
        *   **Local Mode**: Ollama Base URL.
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
