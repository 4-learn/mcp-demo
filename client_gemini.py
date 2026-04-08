"""示範：用 Gemini 搭配同一個 MCP Server——Server 不用改任何一行"""
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

gemini_client = genai.Client()


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 從 MCP Server 取得 tool 定義，轉成 Gemini function 格式
            mcp_tools = await session.list_tools()
            gemini_tools = []
            for tool in mcp_tools.tools:
                gemini_tools.append(types.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.inputSchema,
                ))

            # 用 Gemini 決定要呼叫哪個 tool
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents="scaffold-03 目前狀態如何？有什麼問題？",
                config=types.GenerateContentConfig(
                    tools=[types.Tool(function_declarations=gemini_tools)],
                ),
            )

            # 執行 Gemini 決定的 tool call → 透過 MCP 呼叫
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fc = part.function_call
                    print(f"Gemini 決定呼叫：{fc.name}")
                    print(f"參數：{dict(fc.args)}")

                    result = await session.call_tool(
                        fc.name,
                        arguments=dict(fc.args),
                    )
                    print(f"MCP 回傳：\n{result.content[0].text}\n")


asyncio.run(main())
