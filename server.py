import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("工安法規查詢系統")

DATA_PATH = Path(__file__).parent / "regulations.json"


def _load_regulations() -> list[dict]:
    """每次查詢時重新讀取，確保拿到最新資料"""
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)["regulations"]


@mcp.tool()
def search_regulation(category: str) -> str:
    """根據違規類別查詢對應的法規條文、摘要與罰則。

    Args:
        category: 違規類別，例如 '高處墜落', '電氣危害', '物體飛落', '缺氧危害'
    """
    regulations = _load_regulations()
    matches = [r for r in regulations if r["category"] == category]

    if not matches:
        categories = [r["category"] for r in regulations]
        return f"查無「{category}」相關法規。可查詢類別：{', '.join(set(categories))}"

    results = []
    for r in matches:
        results.append(
            f"📋 {r['law']} {r['article']}\n"
            f"   摘要：{r['summary']}\n"
            f"   罰則：{r['penalty']}\n"
            f"   更新日期：{r['updated']}"
        )
    return "\n\n".join(results)


@mcp.tool()
def list_all_categories() -> str:
    """列出所有可查詢的違規類別清單。"""
    regulations = _load_regulations()
    categories = sorted(set(r["category"] for r in regulations))
    return "可查詢的違規類別：\n" + "\n".join(f"  - {c}" for c in categories)


if __name__ == "__main__":
    mcp.run()
