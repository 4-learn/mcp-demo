"""示範：用 OpenAI 搭配 MCP Server 做設備查詢助手"""
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

openai_client = OpenAI()


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 從 MCP Server 取得 tool 定義，轉成 OpenAI function 格式
            mcp_tools = await session.list_tools()
            openai_tools = []
            for tool in mcp_tools.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                })

            # 用 OpenAI 決定要呼叫哪個 tool
            messages = [
                {"role": "system", "content": "你是工地設備管理助手，使用提供的工具回答問題。"},
                {"role": "user", "content": "目前有哪些設備需要檢修？狀態如何？"},
            ]

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=openai_tools,
            )

            # 執行 OpenAI 決定的 tool call → 透過 MCP 呼叫
            for tool_call in response.choices[0].message.tool_calls:
                print(f"OpenAI 決定呼叫：{tool_call.function.name}")
                print(f"參數：{tool_call.function.arguments}")

                result = await session.call_tool(
                    tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments),
                )
                print(f"MCP 回傳：\n{result.content[0].text}\n")


asyncio.run(main())
