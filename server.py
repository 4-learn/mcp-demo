# FastMCP 是 MCP 官方提供的快速建立 Server 的工具
from mcp.server.fastmcp import FastMCP

# 建立一個 MCP Server，名字叫「自我介紹」
# 這個名字會被 Client 看到，讓 Client 知道這個 Server 是做什麼的
mcp = FastMCP("自我介紹")


# @mcp.tool() 把這個函式「註冊」成 MCP 工具
# 註冊後，任何連上來的 Client 都能發現並呼叫這個函式
# docstring（三引號裡的說明）非常重要——LLM 會靠這段文字決定什麼時候該呼叫這個工具
@mcp.tool()
def get_name() -> str:
    """回傳我的名字。"""
    return "小明"


@mcp.tool()
def get_age() -> str:
    """回傳我的年齡。"""
    return "25 歲"


if __name__ == "__main__":
    # 啟動 Server，預設使用 stdio 傳輸
    # stdio 模式下，Server 透過 stdin/stdout 跟 Client 溝通
    # 所以直接跑 python server.py 會看到空白畫面——這是正常的，它在等 Client 連線
    mcp.run()
