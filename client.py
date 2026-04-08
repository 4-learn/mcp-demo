import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== 可用的工具 ===")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            print("\n=== 問名字 ===")
            result = await session.call_tool("get_name", arguments={})
            print(result.content[0].text)

            print("\n=== 問年齡 ===")
            result = await session.call_tool("get_age", arguments={})
            print(result.content[0].text)


asyncio.run(main())
