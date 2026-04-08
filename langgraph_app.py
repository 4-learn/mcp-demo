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
