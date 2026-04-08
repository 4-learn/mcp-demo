import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolClient:
    """包裝 MCP Client，讓 LangGraph 的 Node 可以方便呼叫"""

    def __init__(self, server_command: str, server_args: list[str]):
        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args,
        )

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                return result.content[0].text


regulation_client = MCPToolClient("python", ["server.py"])


async def lookup_regulation(state: dict) -> dict:
    """查詢法規——MCP 版本"""
    category = state["category"]
    result = await regulation_client.call_tool(
        "search_regulation",
        {"category": category},
    )
    return {
        "regulation": result,
        "messages": [f"📋 法規查詢結果：\n{result}"],
    }


# 單獨執行測試：python langgraph_app.py
if __name__ == "__main__":

    async def test():
        # 模擬一個 LangGraph state，測試 lookup_regulation 這個 Node
        fake_state = {"category": "高處墜落"}
        print(f"測試輸入：category = {fake_state['category']}\n")

        result = await lookup_regulation(fake_state)

        print("=== Node 回傳的 State ===")
        print(f"regulation:\n{result['regulation']}\n")
        print(f"messages:\n{result['messages'][0]}")

    asyncio.run(test())
