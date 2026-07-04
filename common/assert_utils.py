"""统一断言工具：封装若依接口的通用断言逻辑。

设计说明：
- 若依统一响应 { code, data, msg }，code==0 才算业务成功。
- 避免每条用例重复写 assert body["code"] == 0。
"""
from common.logger import log


def assert_api_ok(body, msg=""):
    """断言 RuoYi-Vue-Pro 接口业务成功（code == 0）。"""
    assert body.get("code") == 0, f"{msg} 业务失败 code={body.get('code')} msg={body.get('msg')} body={body}"


def assert_api_fail(body, msg=""):
    """断言接口业务失败（code != 0）。"""
    assert body.get("code") != 0, f"{msg} 期望失败但成功了 body={body}"


def assert_field(actual, expected, field_name=""):
    """断言某字段值等于预期。"""
    assert actual == expected, f"字段 {field_name} 期望 {expected!r} 实际 {actual!r}"
    log.info("断言通过: %s == %r", field_name, expected)
