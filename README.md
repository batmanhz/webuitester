# WebuiTester

WebuiTester 是一个本地优先的、AI 驱动的 Web 自动化测试工具。它允许 QA 工程师使用自然语言描述测试用例，并由 AI Agent 自动执行，无需编写复杂的选择器脚本。

## 🚀 功能特性

*   **自然语言测试用例**：通过简单的文本指令（如“点击登录按钮”、“输入用户名”）定义测试步骤。
*   **AI 智能执行**：内置 Agent 自动解析指令，动态定位页面元素，适应 UI 变化。
*   **可视化执行反馈**：实时查看执行日志和每一步的屏幕截图。
*   **隐身模式**：内置反爬虫规避机制，支持对复杂网站（如百度）的自动化操作。
*   **灵活配置**：支持配置 LLM 后端（OpenAI / 智谱 AI / Ollama）和浏览器参数。

## 🛠️ 技术栈

*   **Backend**: Python FastAPI, Tortoise ORM, SQLite
*   **Frontend**: Vue 3, Element Plus, Pinia, WebSocket
*   **Core Engine**: Playwright (Python), OpenAI SDK
*   **LLM Support**: Compatible with OpenAI API format (Tested with Zhipu AI GLM-4.6v)

## 📂 项目结构

```
webuitester/
├── backend/            # 后端服务
│   ├── app/            # 核心业务逻辑
│   │   ├── agent/      # AI Agent 执行引擎 (基于 browser-use)
│   │   ├── api/        # REST API & WebSocket
│   │   ├── core/       # 配置与数据库
│   │   └── models/     # 数据库模型
│   ├── config.yaml     # 系统配置文件
│   └── main.py         # FastAPI 入口
├── frontend/           # 前端应用
│   ├── src/
│   │   ├── components/ # 组件
│   │   ├── views/      # 页面
│   │   └── stores/     # 状态管理
├── tests/              # 自动化测试脚本
├── docs/               # 项目文档 (PRD, Stories)
├── web-bundles/        # 预置 Agent 和 Team 配置
├── start.bat           # Windows 启动脚本
└── stop.bat            # Windows 停止脚本
```

## ⚡ 快速开始

### 1. 环境准备
*   Python 3.10+
*   Node.js 16+
*   Playwright 浏览器依赖

### 2. 后端启动

```bash
# 1. 创建并激活虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 2. 安装依赖
pip install -r backend/requirements.txt
playwright install

# 3. 配置 LLM
# 编辑 backend/config.yaml，填入你的 API Key (默认配置为智谱AI)

# 4. 启动服务
python backend/server.py
# 服务将运行在 http://localhost:19000
```

### 3. 前端启动

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

## 📖 使用指南

1.  **打开应用**：访问前端页面。
2.  **创建测试用例**：
    *   点击 "New Case"。
    *   输入目标 URL（例如 `https://www.baidu.com`）。
    *   添加测试步骤（例如：1. 输入 'WebuiTester' 2. 点击搜索按钮）。
    *   保存用例。
3.  **运行测试**：
    *   在编辑器页面点击 "Run" 按钮。
    *   右侧面板将显示实时的执行日志和屏幕截图。

## ✅ 已实现功能状态 (PRD 对照)

| 模块 | 功能点 | 状态 | 说明 |
| :--- | :--- | :--- | :--- |
| **测试管理** | 用例增删改查 (CRUD) | ✅ 已完成 | 支持结构化步骤编辑 |
| **执行引擎** | Playwright 浏览器控制 | ✅ 已完成 | 支持 Headless/Headed 模式 |
| | 自然语言指令解析 | ✅ 已完成 | 基于 LLM 的语义定位 |
| | 反爬虫规避 (Stealth) | ✅ 已完成 | 自动隐藏 WebDriver 特征 |
| **实时反馈** | WebSocket 日志流 | ✅ 已完成 | 实时传输文本日志 |
| | 实时截图流 | ✅ 已完成 | 每步操作后自动截图 |
| **配置管理** | 配置文件 (config.yaml) | ✅ 已完成 | 支持热加载配置 |
| **部署** | 基础部署文档 | ✅ 已完成 | 见上文 |

## 🤝 贡献
欢迎提交 Issue 和 Pull Request！
