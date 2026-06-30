"""测试数据清理工具。

用途：作为 UI/联动测试失败后的兜底清理，清理自动化创建的 auto_* 数据。
原则：
- 用例内优先接口清理；
- 本工具只兜底清理 auto 前缀数据，避免误删系统数据；
- 清理失败只记录日志，不掩盖真实测试失败。
"""
from common import db_utils
from common.logger import log


def cleanup_auto_data():
    """兜底清理 auto_* 测试数据。"""
    statements = [
        ("UPDATE system_dict_data SET deleted=1 WHERE label LIKE %s OR value LIKE %s", ("auto%", "auto%")),
        ("UPDATE system_dict_type SET deleted=1 WHERE name LIKE %s OR type LIKE %s", ("auto%", "auto%")),
        ("UPDATE system_users SET deleted=1 WHERE username LIKE %s", ("auto%",)),
        ("UPDATE system_role SET deleted=1 WHERE name LIKE %s OR code LIKE %s", ("auto%", "auto%")),
        ("UPDATE system_menu SET deleted=1 WHERE name LIKE %s OR path LIKE %s", ("auto%", "auto%")),
        ("UPDATE system_dept SET deleted=1 WHERE name LIKE %s", ("auto%",)),
        ("UPDATE system_post SET deleted=1 WHERE name LIKE %s OR code LIKE %s", ("auto%", "auto%")),
    ]
    for sql, params in statements:
        try:
            db_utils.execute(sql, params)
        except Exception as exc:
            log.warning("兜底清理失败: %s params=%s err=%s", sql, params, exc)
