"""RuoYi-Vue-Pro 测试数据清理工具。

清理范围严格限定为本轮运行前缀 TEST_RUN_PREFIX，避免并发运行时清理其它轮次 auto 数据。
优化：一次数据库连接、一个事务执行全部清理 SQL，避免每条 SQL 建立连接。
"""
from common.db_utils import get_connection
from common.logger import log
from common.random_utils import TEST_RUN_PREFIX, TEST_USER_PREFIX


def _like():
    return f"{TEST_RUN_PREFIX}%"


def cleanup_auto_data():
    prefix = _like()
    user_prefix = f"{TEST_USER_PREFIX}%"
    statements = [
        # 先清理授权、岗位和登录令牌关系，避免失败用例留下孤儿数据。
        ("UPDATE system_user_role SET deleted=1 WHERE user_id IN "
         "(SELECT id FROM system_users WHERE username LIKE %s) OR role_id IN "
         "(SELECT id FROM system_role WHERE name LIKE %s OR code LIKE %s)",
         (user_prefix, prefix, prefix)),
        ("UPDATE system_role_menu SET deleted=1 WHERE role_id IN "
         "(SELECT id FROM system_role WHERE name LIKE %s OR code LIKE %s) OR menu_id IN "
         "(SELECT id FROM system_menu WHERE name LIKE %s OR path LIKE %s)",
         (prefix, prefix, prefix, prefix)),
        ("UPDATE system_user_post SET deleted=1 WHERE user_id IN "
         "(SELECT id FROM system_users WHERE username LIKE %s) OR post_id IN "
         "(SELECT id FROM system_post WHERE name LIKE %s OR code LIKE %s)",
         (user_prefix, prefix, prefix)),
        ("UPDATE system_oauth2_access_token SET deleted=1 WHERE user_id IN "
         "(SELECT id FROM system_users WHERE username LIKE %s)", (user_prefix,)),
        ("UPDATE system_oauth2_refresh_token SET deleted=1 WHERE user_id IN "
         "(SELECT id FROM system_users WHERE username LIKE %s)", (user_prefix,)),
        ("UPDATE system_dict_data SET deleted=1 WHERE label LIKE %s OR value LIKE %s", (prefix, prefix)),
        ("UPDATE system_dict_type SET deleted=1 WHERE name LIKE %s OR type LIKE %s", (prefix, prefix)),
        ("UPDATE system_users SET deleted=1 WHERE username LIKE %s", (user_prefix,)),
        ("UPDATE system_role SET deleted=1 WHERE name LIKE %s OR code LIKE %s", (prefix, prefix)),
        ("UPDATE system_menu SET deleted=1 WHERE name LIKE %s OR path LIKE %s", (prefix, prefix)),
        ("UPDATE system_dept SET deleted=1 WHERE name LIKE %s", (prefix,)),
        ("UPDATE system_post SET deleted=1 WHERE name LIKE %s OR code LIKE %s", (prefix, prefix)),
    ]
    conn = get_connection(autocommit=False)
    try:
        affected_total = 0
        with conn.cursor() as cur:
            for sql, params in statements:
                cur.execute(sql, params)
                affected_total += cur.rowcount
        conn.commit()
        if affected_total:
            log.info("本轮 auto 测试数据清理完成，共影响 %d 行", affected_total)
        return affected_total
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
