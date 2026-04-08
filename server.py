from mcp.server.fastmcp import FastMCP

mcp = FastMCP("工地設備查詢系統")

EQUIPMENT_DB = {
    "crane-01": {
        "name": "塔式起重機 A",
        "location": "B 棟工區",
        "status": "運轉中",
        "last_inspection": "2026-04-01",
        "next_inspection": "2026-05-01",
        "issues": []
    },
    "scaffold-03": {
        "name": "鷹架組 C",
        "location": "A 棟外牆",
        "status": "待檢修",
        "last_inspection": "2026-03-15",
        "next_inspection": "2026-04-15",
        "issues": ["固定扣件鬆動", "防墜網破損"]
    },
    "excavator-02": {
        "name": "挖土機 B",
        "location": "地下室開挖區",
        "status": "停機",
        "last_inspection": "2026-03-28",
        "next_inspection": "2026-04-28",
        "issues": ["液壓管線漏油"]
    },
}


@mcp.tool()
def get_equipment_status(equipment_id: str) -> str:
    """查詢指定設備的目前狀態，包含位置、檢修紀錄和異常問題。

    Args:
        equipment_id: 設備編號，例如 'crane-01', 'scaffold-03'
    """
    equip = EQUIPMENT_DB.get(equipment_id)
    if not equip:
        return f"找不到設備 {equipment_id}，可用設備：{', '.join(EQUIPMENT_DB.keys())}"

    issues_text = "、".join(equip["issues"]) if equip["issues"] else "無"
    return (
        f"設備：{equip['name']}\n"
        f"位置：{equip['location']}\n"
        f"狀態：{equip['status']}\n"
        f"上次巡檢：{equip['last_inspection']}\n"
        f"下次巡檢：{equip['next_inspection']}\n"
        f"異常項目：{issues_text}"
    )


@mcp.tool()
def list_equipment_by_status(status: str) -> str:
    """依狀態篩選設備清單。

    Args:
        status: 設備狀態，可選值：'運轉中', '待檢修', '停機'
    """
    results = [
        f"- {eid}: {e['name']}（{e['location']}）"
        for eid, e in EQUIPMENT_DB.items()
        if e["status"] == status
    ]
    if not results:
        return f"沒有狀態為「{status}」的設備"
    return f"狀態為「{status}」的設備：\n" + "\n".join(results)


if __name__ == "__main__":
    mcp.run()
