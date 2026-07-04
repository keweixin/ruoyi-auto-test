"""统一断言工具：封装若依接口的通用断言逻辑。

设计说明：
- 若依统一响应 { code, data, msg }，code==0 才算业务成功。
- 避免每条用例重复写 assert body["code"] == 0。
"""
from common.logger import log


def _response_body(response, action):
    assert response.status_code < 500, f"{action} HTTP 状态异常: {response.status_code}"
    try:
        body = response.json()
    except ValueError as exc:
        raise AssertionError(f"{action} 响应不是 JSON") from exc
    assert isinstance(body, dict), f"{action} JSON 响应不是对象: {body!r}"
    return body


def assert_response_ok(response, action=""):
    body = _response_body(response, action)
    assert_api_ok(body, action)
    return body


def assert_response_fail(response, action="", contains=""):
    body = _response_body(response, action)
    assert_api_fail(body, action)
    if contains:
        assert contains in body.get("msg", ""), \
            f"{action} 错误信息期望包含 {contains!r}，实际 {body.get('msg')!r}"
    return body


def assert_page_result(body, min_total=0):
    assert_api_ok(body, "分页查询")
    data = body.get("data")
    assert isinstance(data, dict), f"分页 data 应为对象: {data!r}"
    assert isinstance(data.get("list"), list), f"分页 list 应为数组: {data!r}"
    assert isinstance(data.get("total"), int), f"分页 total 应为整数: {data!r}"
    assert data["total"] >= min_total, f"分页 total 期望至少 {min_total}，实际 {data['total']}"
    return data


def assert_not_found(body):
    assert body.get("code") != 0 or not body.get("data"), f"期望数据不存在，实际 {body}"
    return body


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
