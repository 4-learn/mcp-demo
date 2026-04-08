from mcp.server.fastmcp import FastMCP

mcp = FastMCP("自我介紹")


@mcp.tool()
def get_name() -> str:
    """回傳我的名字。"""
    return "小明"


@mcp.tool()
def get_age() -> str:
    """回傳我的年齡。"""
    return "25 歲"


if __name__ == "__main__":
    mcp.run()
