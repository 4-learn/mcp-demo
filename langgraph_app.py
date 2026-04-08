import asyncio
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END, add_messages
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# === MCP Client 包裝 ===
# 把 MCP 的連線邏輯包成一個 class，讓 LangGraph 的 Node 可以方便呼叫

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


# === State 定義 ===
# LangGraph 的核心：所有 Node 共用的白板

class SafetyState(TypedDict):
    category: str                              # 輸入：違規類別
    regulation: str                            # 法規 Node 寫入的查詢結果
    messages: Annotated[list, add_messages]     # 流程紀錄


# === MCP Client 實例 ===
# 指向同一個目錄下的 server.py（法規查詢 MCP Server）

regulation_client = MCPToolClient("python", ["server.py"])


# === Node 定義 ===
# 每個 Node 就是一個函式：讀 State → 做事 → 回傳要更新的 State

async def lookup_regulation(state: SafetyState) -> dict:
    """法規查詢 Node：透過 MCP Server 查詢法規"""
    category = state["category"]
    result = await regulation_client.call_tool(
        "search_regulation",
        {"category": category},
    )
    return {
        "regulation": result,
        "messages": [f"📋 法規查詢完成：{category}"],
    }


def summarize(state: SafetyState) -> dict:
    """摘要 Node：把查詢結果整理成一句話（純邏輯，不用 LLM）"""
    regulation = state.get("regulation", "查無資料")
    first_line = regulation.split("\n")[0] if regulation else "查無資料"
    return {
        "messages": [f"📝 摘要：{first_line}"],
    }


# === 建構 Graph ===
# START → lookup_regulation → summarize → END

graph = StateGraph(SafetyState)

graph.add_node("lookup_regulation", lookup_regulation)
graph.add_node("summarize", summarize)

graph.add_edge(START, "lookup_regulation")    # 起點 → 查法規
graph.add_edge("lookup_regulation", "summarize")  # 查法規 → 摘要
graph.add_edge("summarize", END)              # 摘要 → 結束

app = graph.compile()


# === 執行測試 ===
if __name__ == "__main__":

    async def main():
        print("=== LangGraph + MCP 整合測試 ===\n")

        # 因為 lookup_regulation 是 async function，所以要用 ainvoke
        result = await app.ainvoke({
            "category": "高處墜落",
            "messages": [],
        })

        print("--- 流程紀錄 ---")
        for msg in result["messages"]:
            print(f"  {msg}")

        print(f"\n--- 法規查詢結果 ---\n{result['regulation']}")

    asyncio.run(main())
