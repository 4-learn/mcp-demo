from mcp.server.fastmcp import FastMCP

mcp = FastMCP("工地設備查詢系統")

EQUIPMENT_DB = {
    "crane-01": {"name": "塔式起重機 A", "location": "B 棟工區", "status": "運轉中", "issues": []},
    "scaffold-03": {"name": "鷹架組 C", "location": "A 棟外牆", "status": "待檢修", "issues": ["固定扣件鬆動", "防墜網破損"]},
}


@mcp.tool()
def get_equipment_status(equipment_id: str) -> str:
    """查詢指定設備的目前狀態。"""
    equip = EQUIPMENT_DB.get(equipment_id)
    if not equip:
        return f"找不到設備 {equipment_id}"
    issues_text = "、".join(equip["issues"]) if equip["issues"] else "無"
    return f"設備：{equip['name']}\n位置：{equip['location']}\n狀態：{equip['status']}\n異常：{issues_text}"


@mcp.tool()
def list_equipment_by_status(status: str) -> str:
    """依狀態篩選設備清單。"""
    results = [f"- {eid}: {e['name']}（{e['location']}）" for eid, e in EQUIPMENT_DB.items() if e["status"] == status]
    if not results:
        return f"沒有狀態為「{status}」的設備"
    return f"狀態為「{status}」的設備：\n" + "\n".join(results)


if __name__ == "__main__":
    mcp.run(transport="sse")
