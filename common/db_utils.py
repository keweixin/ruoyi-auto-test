"""数据库工具：用 pymysql 直连 MySQL，做数据库校验与兜底清理。

设计说明：
- 接口返回成功 ≠ 数据正确落库。本工具用于验证数据真的落库、字段正确。
- 用 %s 占位防 SQL 注入，绝不字符串拼接。
- DictCursor 让查询结果返回 dict，便于按字段名取值。
"""
import pymysql
from common.config import cfg
from common.logger import log


def _conn():
    """建立数据库连接。"""
    return pymysql.connect(
        host=cfg.db_host,
        port=cfg.db_port,
        user=cfg.db_user,
        password=cfg.db_pwd,
        database=cfg.db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def query_one(sql, params=None):
    """查询单条记录，返回 dict 或 None。

    示例：
        row = query_one(
            "SELECT name, status, deleted FROM system_dict_type WHERE type=%s",
            ("auto_dict_123",)
        )
        assert row["deleted"] == 0
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()
    finally:
        conn.close()


def query_all(sql, params=None):
    """查询多条记录，返回 list[dict]。"""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql, params=None):
    """执行写操作（INSERT/UPDATE/DELETE），返回受影响行数。主要用于兜底清理。"""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            n = cur.execute(sql, params or ())
        conn.commit()
        log.info("DB 执行: %s -> 影响 %d 行", sql, n)
        return n
    finally:
        conn.close()
