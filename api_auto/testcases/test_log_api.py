"""日志查询接口测试用例。

覆盖 LOG_API_001 ~ 004：
- 操作日志分页查询（含总数、列表非空、字段结构）
- 登录日志分页查询（含总数、列表非空、字段结构）
- 操作日志按类型筛选
- 登录日志按用户名筛选

日志是审计与排障的核心，只读查询无副作用。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok, assert_response_ok, assert_response_fail
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA


@allure.feature("日志查询接口")
@pytest.mark.api
class TestLogApi:

    @allure.story("操作日志")
    @allure.title("LOG_API_001 操作日志分页查询成功")
    @pytest.mark.smoke
    def test_operate_log_page(self, operate_log_client):
        """操作日志分页查询：总数>0、列表非空、字段结构正确。"""
        body = operate_log_client.page({"pageNo": 1, "pageSize": 5}).json()
        assert_schema(body, PAGE_LIST_SCHEMA)
        assert_api_ok(body)
        data = body["data"]
        assert data["total"] > 0, "操作日志总数应大于 0（系统运行有操作记录）"
        assert len(data["list"]) > 0, "操作日志列表不应为空"
        # 校验关键字段存在
        first = data["list"][0]
        assert "id" in first and "type" in first, "操作日志缺少 id/type 字段"

    @allure.story("操作日志")
    @allure.title("LOG_API_002 操作日志按类型筛选成功")
    def test_operate_log_filter_by_type(self, operate_log_client):
        """操作日志按 type 筛选：返回的列表项 type 与筛选值一致。"""
        # 先查全部，取第一条的 type 作为筛选值
        all_body = assert_response_ok(operate_log_client.page({"pageNo": 1, "pageSize": 1}))
        first_type = all_body["data"]["list"][0]["type"]
        # 按 type 筛选
        body = assert_response_ok(operate_log_client.page({"pageNo": 1, "pageSize": 5, "type": first_type}))
        for item in body["data"]["list"]:
            assert item["type"] == first_type, f"筛选 type={first_type} 但返回 {item['type']}"

    @allure.story("登录日志")
    @allure.title("LOG_API_003 登录日志分页查询成功")
    @pytest.mark.smoke
    def test_login_log_page(self, login_log_client):
        """登录日志分页查询：总数>0（测试登录会产生记录）、列表非空。"""
        body = login_log_client.page({"pageNo": 1, "pageSize": 5}).json()
        assert_schema(body, PAGE_LIST_SCHEMA)
        assert_api_ok(body)
        data = body["data"]
        assert data["total"] > 0, "登录日志总数应大于 0（测试登录会产生记录）"
        assert len(data["list"]) > 0, "登录日志列表不应为空"
        first = data["list"][0]
        assert "id" in first and "username" in first, "登录日志缺少 id/username 字段"

    @allure.story("登录日志")
    @allure.title("LOG_API_004 登录日志按用户名筛选成功")
    def test_login_log_filter_by_username(self, login_log_client):
        """登录日志按 username 筛选：返回的列表项 username 含筛选值。"""
        body = assert_response_ok(login_log_client.page({"pageNo": 1, "pageSize": 5, "username": "admin"}))
        for item in body["data"]["list"]:
            assert "admin" in item.get("username", ""), \
                f"筛选 username=admin 但返回 {item.get('username')}"
