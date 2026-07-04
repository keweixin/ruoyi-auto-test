"""按业务含义查询测试环境中的稳定基础数据，避免硬编码 ID。"""
from functools import lru_cache

from common import db_utils


@lru_cache(maxsize=None)
def get_root_dept_id():
    row = db_utils.query_one(
        "SELECT id FROM system_dept WHERE parent_id=0 AND deleted=0 ORDER BY id LIMIT 1"
    )
    if not row:
        raise RuntimeError("测试环境缺少可用的根部门")
    return row["id"]


@lru_cache(maxsize=None)
def get_admin_role_id():
    row = db_utils.query_one(
        "SELECT id FROM system_role WHERE deleted=0 AND (code='super_admin' OR name='超级管理员') "
        "ORDER BY id LIMIT 1"
    )
    if not row:
        raise RuntimeError("测试环境缺少超级管理员角色")
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
