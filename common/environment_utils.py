"""按业务含义查询测试环境中的稳定基础数据，避免硬编码 ID。"""
from common import db_utils


def get_root_dept_id():
    row = db_utils.query_one(
        "SELECT id FROM system_dept WHERE parent_id=0 AND deleted=0 ORDER BY id LIMIT 1"
    )
    if not row:
        raise RuntimeError("测试环境缺少可用的根部门")
    return row["id"]


def get_assignable_menu_ids(count=3):
    rows = db_utils.query_all(
        "SELECT id FROM system_menu WHERE deleted=0 AND status=0 AND type IN (1, 2) "
        "ORDER BY id LIMIT %s",
        (int(count),),
    )
    ids = [row["id"] for row in rows]
    if len(ids) < count:
        raise RuntimeError(f"测试环境可分配菜单不足 {count} 个")
    return ids
