import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client


async def main():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== 遠端 Server 的 Tools ===")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            print("\n=== 查詢 scaffold-03 ===")
            result = await session.call_tool(
                "get_equipment_status",
                arguments={"equipment_id": "scaffold-03"},
            )
            print(result.content[0].text)


asyncio.run(main())
