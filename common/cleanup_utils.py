"""测试数据清理工具（适配 RuoYi v3.9.2 原版表结构）。

清理范围严格限定为本轮运行前缀 TEST_RUN_PREFIX，避免并发运行时清理其它轮次 auto 数据。
优化：一次数据库连接、一个事务执行全部清理 SQL，避免每条 SQL 建立连接。
"""
from common.config import cfg
from common.logger import log
from common.random_utils import TEST_RUN_PREFIX
import pymysql


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
    conn = pymysql.connect(
        host=cfg.db_host, port=cfg.db_port, user=cfg.db_user,
        password=cfg.db_pwd, database=cfg.db_name,
        charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    try:
        with conn.cursor() as cur:
            for sql, params in statements:
                cur.execute(sql, params)
                log.info("DB 清理: %s params=%s -> 影响 %d 行", sql, params, cur.rowcount)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
