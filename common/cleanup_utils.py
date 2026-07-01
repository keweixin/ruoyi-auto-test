"""测试数据清理工具（适配 RuoYi v3.9.2 原版表结构）。

清理范围严格限定为本轮运行前缀 TEST_RUN_PREFIX，避免并发运行时清理其它轮次 auto 数据。
"""
from common import db_utils
from common.logger import log
from common.random_utils import TEST_RUN_PREFIX


def _like():
    return f"{TEST_RUN_PREFIX}%"


def cleanup_auto_data():
    prefix = _like()
    statements = [
        ("DELETE FROM sys_dict_data WHERE dict_label LIKE %s OR dict_value LIKE %s", (prefix, prefix)),
        ("DELETE FROM sys_dict_type WHERE dict_name LIKE %s OR dict_type LIKE %s", (prefix, prefix)),
        ("UPDATE sys_user SET del_flag='2' WHERE user_name LIKE %s", (prefix,)),
        ("UPDATE sys_role SET del_flag='2' WHERE role_name LIKE %s OR role_key LIKE %s", (prefix, prefix)),
        ("DELETE FROM sys_menu WHERE menu_name LIKE %s OR path LIKE %s", (prefix, prefix)),
        ("UPDATE sys_dept SET del_flag='2' WHERE dept_name LIKE %s", (prefix,)),
        ("DELETE FROM sys_post WHERE post_name LIKE %s OR post_code LIKE %s", (prefix, prefix)),
    ]
    for sql, params in statements:
        try:
            db_utils.execute(sql, params)
        except Exception as exc:
            log.warning("兜底清理失败: %s params=%s err=%s", sql, params, exc)
