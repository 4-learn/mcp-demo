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
            print("=== 可用 Tools ===")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            print("\n=== 查詢 scaffold-03 ===")
            result = await session.call_tool(
                "get_equipment_status",
                arguments={"equipment_id": "scaffold-03"},
            )
            print(result.content[0].text)

            print("\n=== 列出待檢修設備 ===")
            result = await session.call_tool(
                "list_equipment_by_status",
                arguments={"status": "待檢修"},
            )
            print(result.content[0].text)


asyncio.run(main())
