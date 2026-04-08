import asyncio

# ClientSession：負責跟 Server 對話的「翻譯員」，幫你處理 MCP 協議細節
# StdioServerParameters：告訴 Client「怎麼啟動 Server」的設定
from mcp import ClientSession, StdioServerParameters

# stdio_client：透過 stdin/stdout 連線到 Server 的工具
from mcp.client.stdio import stdio_client


async def main():
    # 設定要連線的 Server
    # command + args = Client 會執行 "python server.py" 來啟動 Server
    # 你不需要自己跑 python server.py，Client 會幫你啟動
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    # === 第一層：建立連線管道 ===
    # stdio_client 會：
    #   1. 啟動 "python server.py" 子程序
    #   2. 接管它的 stdin 和 stdout
    #   3. 回傳 read（讀 Server 回應）和 write（寫入請求給 Server）
    # 就像打電話接通了，拿到「聽筒」和「話筒」
    # async with 確保離開時自動斷線、關閉 Server 子程序
    async with stdio_client(server_params) as (read, write):

        # === 第二層：建立對話 ===
        # 把 read/write 管道交給 ClientSession
        # ClientSession 是「翻譯員」——你只要說「幫我呼叫 get_name」，
        # 它會幫你把請求轉成 MCP 協議格式（JSON-RPC），送出去，再把回應解析回來
        # 你不需要自己組 JSON，ClientSession 全部處理好了
        async with ClientSession(read, write) as session:

            # 跟 Server 握手：確認雙方都支援 MCP 協議、交換版本資訊
            await session.initialize()

            # 問 Server：「你有哪些工具可以用？」
            # Server 會回傳所有用 @mcp.tool() 註冊的函式清單
            tools = await session.list_tools()
            print("=== 可用的工具 ===")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # 呼叫工具：call_tool("工具名稱", arguments={參數})
            # 這裡的 get_name 不需要參數，所以 arguments 是空的 {}
            # Client 送出請求 → Server 執行 get_name() → 回傳結果
            print("\n=== 問名字 ===")
            result = await session.call_tool("get_name", arguments={})
            # result.content 是一個列表，content[0].text 取出文字結果
            print(result.content[0].text)

            print("\n=== 問年齡 ===")
            result = await session.call_tool("get_age", arguments={})
            print(result.content[0].text)

    # 離開 async with 後：
    # - ClientSession 自動關閉
    # - stdio_client 自動結束 Server 子程序
    # 不需要手動 .close() 或 kill process


# asyncio.run() 是 Python 執行非同步函式的入口
# 因為 MCP 的 Client/Server 通訊是非同步的（async/await），所以需要這行來啟動
asyncio.run(main())
