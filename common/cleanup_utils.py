"""测试数据清理工具（适配 RuoYi v3.9.2 原版表结构）。

原版逻辑删除字段差异：
- sys_user / sys_role / sys_dept / sys_dict_type 部分表用 del_flag（'0'正常 '2'删除）
- sys_menu / sys_post / sys_dict_data 无 del_flag，是物理删除
为避免误报，清理失败只记录日志，不掩盖真实测试失败。
"""
from common import db_utils
from common.logger import log


def cleanup_auto_data():
    statements = [
        ("DELETE FROM sys_dict_data WHERE dict_label LIKE %s OR dict_value LIKE %s", ("auto%", "auto%")),
        ("DELETE FROM sys_dict_type WHERE dict_name LIKE %s OR dict_type LIKE %s", ("auto%", "auto%")),
        ("UPDATE sys_user SET del_flag='2' WHERE user_name LIKE %s", ("auto%",)),
        ("UPDATE sys_role SET del_flag='2' WHERE role_name LIKE %s OR role_key LIKE %s", ("auto%", "auto%")),
        ("DELETE FROM sys_menu WHERE menu_name LIKE %s OR path LIKE %s", ("auto%", "auto%")),
        ("UPDATE sys_dept SET del_flag='2' WHERE dept_name LIKE %s", ("auto%",)),
        ("DELETE FROM sys_post WHERE post_name LIKE %s OR post_code LIKE %s", ("auto%", "auto%")),
    ]
    for sql, params in statements:
        try:
            db_utils.execute(sql, params)
        except Exception as exc:
            log.warning("兜底清理失败: %s params=%s err=%s", sql, params, exc)
