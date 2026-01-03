
import asyncio
from browser_use import Agent, ChatOpenAI
from browser_use.browser import BrowserProfile

# 1. 配置连接 LM Studio 的 LLM
# 注意：LM Studio 的 API 通常不需要真实的 API Key，但 LangChain 强制要求填一个，随便填即可

llm = ChatOpenAI(
    base_url="http://localhost:8000/v1",  # 务必加上 /v1
    api_key="lm-studio",  # 占位符，随便填
    model="qwen3-vl-8b-instruct",  # 填你在 LM Studio 中加载的模型名称（可以在 Server 日志里看到）
    temperature=0.0,  # 设为 0 以保证输出格式稳定，减少 JSON 错误
)


"""
llm = ChatOpenAI(
    base_url= "https://open.bigmodel.cn/api/paas/v4",  # 务必加上 /v1
    api_key="5fdb0d4bbbb24692b15469a73ad23ac1.DWeb93wnlCVcrwyx",  # 占位符，随便填
    model="glm-4.6",  # 填你在 LM Studio 中加载的模型名称（可以在 Server 日志里看到）
    temperature=0.0,  # 设为 0 以保证输出格式稳定，减少 JSON 错误
)



llm = ChatOpenAI(
    base_url= "https://dashscope.aliyuncs.com/compatible-mode/v1",  # 务必加上 /v1
    api_key="sk-0fed776a32284f699f15ceaf1893f77a",  # 占位符，随便填
    model="qwen3-max", # 填你在 LM Studio 中加载的模型名称（可以在 Server 日志里看到）
    temperature=0.0,  # 设为 0 以保证输出格式稳定，减少 JSON 错误
)
"""

# 2. 浏览器配置 - 使用 BrowserProfile 代替旧的 Browser/BrowserConfig
browser_profile = BrowserProfile(
    headless=False,  # 显示浏览器界面，方便调试
)


async def main():
    # 3. 定义任务
    # 针对 Qwen 本地模型的 Prompt 优化：
    # 如果你发现模型总是报错说格式不对，可以在 Prompt 里再次强调
    task_prompt = """
    Go to google.com and search for 'OpenAI'.

    IMPORTANT: You must respond with a valid JSON format. 
    Example: {"action": "search_google", "query": "OpenAI"}
    """

    agent = Agent(
        task="打开携程网站搜索杭州到北京1月2日的机票信息",
        llm=llm,
        browser_profile=browser_profile,  # 使用 browser_profile 代替 browser
        use_vision='auto',  # 关键点：如果你用的不是 VL (视觉) 模型，必须设为 False
    )

    # 4. 运行
    try:
        history = await agent.run()
        print("Final Result:", history.final_result())
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())