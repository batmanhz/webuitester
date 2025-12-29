# Project Brief: WebuiTester

## 1. Executive Summary (项目摘要)
WebuiTester 是一款基于 Web 的本地化 AI 测试代理工具，专为 QA 工程师设计。它利用大语言模型（LLM）将自然语言编写的自由文本测试用例转化为实际的 Web 界面操作。核心目标是解决传统自动化测试脚本（Selenium/Playwright）因 UI 元素变动导致的高维护成本问题，实现“维护文本即维护测试”的愿景。

## 2. Problem Statement (问题陈述)
*   **脆弱的自动化脚本**：传统的自动化测试严重依赖 CSS/XPath 选择器。一旦前端开发修改了页面布局或类名，测试脚本就会失败，导致 QA 需花费大量时间修复代码。
*   **技术门槛高**：编写和维护自动化脚本需要 QA 具备一定的编码能力。
*   **维护成本高**：随着项目迭代，维护庞大的脚本库比开发新功能还累。

## 3. Proposed Solution (解决方案)
*   **核心理念**：No-Code, Just Text。
*   **工作流**：
    1.  用户在 Web 界面输入/导入自由格式的文本用例（如：“1. 打开首页，2. 输入账号 admin...”）。
    3.  Python 后端 Agent (基于 Playwright) 解析意图。
    4.  Agent 动态识别页面元素并执行操作（无需预定义 Selector）。
    5.  执行结束后自动进行断言验证，并输出图文报告。
*   **部署形态**：本地/内网部署的 Web 工具，数据安全，响应快。

## 4. Target Users (目标用户)
*   **主要用户**：QA 测试工程师。
*   **需求特征**：有测试逻辑思维，但希望摆脱繁琐的代码维护工作；需要频繁进行回归测试。

## 5. MVP Scope (MVP 范围)
**In Scope (包含):**
*   **文本用例解析**：支持多步骤的自然语言指令解析。
*   **表单与基础交互**：支持输入框填写、按钮点击、下拉选择、链接跳转等（重点覆盖登录、新增商品等场景）。
*   **混合模型支持**：后端优先支持 OpenAI/Claude API，架构上预留 Ollama/LocalAI 本地模型接口。
*   **可视化执行**：用户能在浏览器或服务器端看到（或通过截图看到）执行过程。
*   **基础报告**：Pass/Fail 状态及关键步骤截图。

**Out of Scope (不包含 - 后续迭代):**
*   复杂的跨系统/多 Tab 交互。
*   复杂的验证码识别（除非模型原生支持）。
*   大规模并发执行/集群管理。
*   测试用例的版本管理系统（Git 集成）。

## 6. Technical Preferences (技术偏好)
*   **Backend**: Python (FastAPI/Django) - 利用其强大的 AI 生态。
*   **Core Engine**: Playwright (Python ver) + LangChain/Browser-use (Agent 逻辑)。
*   **LLM Integration**: 支持 Cloud API (OpenAI/DeepSeek) + Local API (Ollama)。
*   **Frontend**: 建议使用现代轻量级框架 (React/Vue) 或 Python 快速构建方案 (Streamlit/Gradio - 若追求 MVP 速度)。

## 7. Risks & Challenges (风险与挑战)
*   **幻觉 (Hallucination)**：AI 可能会误报成功或失败。需要设计“验证机制”（Verifier Agent）。
*   **执行速度**：LLM 推理需要时间，比传统脚本慢，需优化 Token 使用。
*   **成本**：如果是 API 模式，高频运行回归测试会导致 Token 费用上升。
