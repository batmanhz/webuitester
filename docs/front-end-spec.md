# WebuiTester UI/UX Specification

## 1. Introduction
This document defines the user experience, visual design, and interface specifications for **WebuiTester**. It guides the frontend implementation using **Vue 3** and **Element Plus**.

## 2. Design Principles
*   **Efficiency First**: Minimize clicks. Allow QAs to paste a text block and start testing immediately via "Smart Formatting".
*   **Visual Confirmation**: Every AI action must have a visual proof (screenshot) and a textual explanation (log).
*   **Modern Professional**: Dark mode default to reduce eye strain, with vibrant accents to indicate active AI states.

## 3. Visual Identity
*   **Theme Mode**: Dark Mode (Default/Only).
*   **Primary Color**: **Vibrant Purple** (`#8B5CF6` / `el-color-primary`). Used for primary actions (Run, Save) and active states.
*   **Status Colors**:
    *   Success: `#10B981` (Green)
    *   Error/Fail: `#EF4444` (Red)
    *   Thinking/Processing: `#F59E0B` (Amber/Yellow)
*   **Typography**: Inter or Roboto (System Default San-serif) for UI; Fira Code for Logs/Steps.

## 4. Information Architecture (Site Map)
graph TD
    A[App Root] --> B[Sidebar Nav]
    B --> C[Test Cases (Home)]
    B --> D[Test History / Runs]
    B --> E[Settings (LLM Config)]
    
    C --> C1[Case List]
    C --> C2[Split View Editor]
    
    C2 --> C2a[Left: Editor Panel]
    C2 --> C2b[Right: Execution Panel]

## 5. Key Screen Layouts
### 5.1 Main Split View (The "IDE" View)
*   **Layout**: 50% Left (Edit), 50% Right (Run). Resizable divider.
*   **Left Panel**: The Smart Editor
    *   **Header**:
        *   Input: Target URL (Full width).
        *   Input: Case Name (Optional).
    *   **Smart Input Area** (The "2B" Feature):
        *   Component: Large Textarea with "Smart Format" toggle.
        *   **State A (Raw Text)**: Large textarea for pasting unstructured test steps (e.g., "1. Open login, 2. type admin...").
        *   **Action**: "✨ AI Format" Button triggers parsing.
        *   **State B (Structured List)**: Sortable/Draggable Cards.
            *   Content: Step Number, Action Description (Editable), Expected Result (Optional).
            *   Actions: Delete Step, Add Step Between, Drag to Reorder.
    *   **Footer**:
        *   Primary Button: **Run Test** (Purple, Large, with Play Icon).
*   **Right Panel**: Execution & Feedback
    *   **Screenshot Viewer** (Top 60%):
        *   **State 1 (Idle)**: Placeholder with "Ready to Start" illustration.
        *   **State 2 (Running)**: Shows latest screenshot pushed by backend.
            *   *Overlay*: "Loading..." spinner or "Thinking..." badge when Agent is planning.
            *   *Annotation*: Bounding boxes drawn on interacted elements (e.g., red box around clicked button).
        *   **State 3 (Done)**: Shows final state screenshot with Result Badge (PASS/FAIL).
    *   **Live Console** (Bottom 40%):
        *   Style: Terminal-like, Monospace font (Fira Code), Dark background.
        *   Content: Streaming structured logs.
        *   **Colors**:
            *   `[THOUGHT]`: Blue (Agent internal reasoning/planning).
            *   `[ACTION]`: Purple (Browser interactions: Click, Type, Scroll).
            *   `[INFO]`: Grey (System status, navigation).
            *   `[PASS]`: Green (Assertion success).
            *   `[FAIL]`: Red (Assertion failure/Error).

### 5.2 Settings Modal
*   **LLM Provider**: Toggle (Cloud / Local).
    *   **Cloud**: API Key (Password input), Base URL (e.g., OpenAI, Anthropic).
    *   **Local**: Ollama URL (Default: `http://localhost:11434`).
*   **Browser Config**:
    *   Toggle: Headless Mode (Run without visible browser window).
    *   Input: Viewport Size (Default: 1280x720).
## 6. Interaction Flows
Smart Paste Flow:
User creates new Case -> Pastes raw text block -> Clicks "Format" -> App parses text by newlines/numbers -> Populates Step List.
Execution Flow:
User clicks Run -> Right panel clears -> Spinner appears -> First log "Initializing Agent..." -> First Screenshot appears -> Steps highlight in Left Panel as they are executed (Syncing Left/Right) -> Final Result Overlay (Pass/Fail).
## 7. Component Library (Element Plus)
Buttons: el-button (Primary, Text).
Inputs: el-input (Text, Textarea).
Lists: vuedraggable (for steps) + el-card.
Logs: Custom scrollable div with pre-formatted text.
Splitter: Splitpanes (Vue library).