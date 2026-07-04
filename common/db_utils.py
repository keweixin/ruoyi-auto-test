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
    """建立数据库连接（内部使用，外部请用 get_connection）。"""
    return get_connection()


def get_connection(autocommit=False):
    """建立数据库连接，返回 pymysql.Connection。

    autocommit=True 时自动提交（适合单条写操作）；
    autocommit=False 时需手动 commit/rollback（适合事务性批量操作）。
    """
    conn = pymysql.connect(
        host=cfg.db_host,
        port=cfg.db_port,
        user=cfg.db_user,
        password=cfg.db_pwd,
        database=cfg.db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=autocommit,
    )
    return conn


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


def assert_db_exists(sql, params=None):
    row = query_one(sql, params)
    assert row is not None, f"数据库未查到预期记录: sql={sql!r} params={params!r}"
    return row


def assert_db_field(sql, params, field, expected):
    row = assert_db_exists(sql, params)
    assert row.get(field) == expected, \
        f"数据库字段 {field} 期望 {expected!r}，实际 {row.get(field)!r}"
    return row


def assert_db_record(table, entity_id, fields, label="数据库记录"):
    """db_check 用例的高层 helper：查记录 + 断言 deleted==0 + 附加到 Allure。

    用法：
        assert_db_record("system_dept", new_id, {"name": name}, "部门")

    table: 表名（如 system_dept）
    entity_id: 记录主键 id
    fields: 期望匹配的字段 {field: expected_value}（不含 deleted，deleted 自动断言为 0）
    label: Allure 附件名称

    返回查询到的 row（dict）。
    """
    field_names = list(fields.keys()) + ["deleted + 0 AS deleted"]
    sql = f"SELECT {', '.join(field_names)} FROM {table} WHERE id=%s"
    row = assert_db_exists(sql, (entity_id,))
    # 断言逻辑删除标记
    assert row["deleted"] == 0, f"{label} deleted 期望 0，实际 {row['deleted']}"
    # 断言指定字段
    for field, expected in fields.items():
        assert row[field] == expected, \
            f"{label} 字段 {field} 期望 {expected!r}，实际 {row[field]!r}"
    # 附加到 Allure
    try:
        from common.allure_utils import attach_text
        attach_text(label, str(row))
    except Exception:
        pass
    return row
