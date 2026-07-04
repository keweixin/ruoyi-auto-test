"""RuoYi-Vue-Pro 登录认证接口测试用例。

覆盖 AUTH_API_001 ~ 009：
- 正确/错误/空用户名/空密码 登录（参数化）
- 获取登录用户信息
- 未带 token / 错误 token 访问（鉴权）
- 退出登录 + 退出后 token 失效

协议要点：code==0 成功；token 在 body['data']['accessToken']；携带 tenant-id。
"""
import allure
import pytest
import time
import os

from common.config import cfg
from common.assert_utils import assert_api_ok, assert_api_fail, assert_response_ok, assert_response_fail
from api_auto.clients.auth_client import AuthClient
from common.schema_utils import assert_schema, LOGIN_SCHEMA, GET_INFO_SCHEMA
from common.yaml_utils import load_case_list


_LOGIN_CASES = load_case_list(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "login_data.yaml"),
    "login", "cases"
)


@allure.feature("登录认证接口")
@pytest.mark.api
class TestAuthApi:

    @allure.story("登录")
    @pytest.mark.parametrize("case", _LOGIN_CASES, ids=[case["case_id"] for case in _LOGIN_CASES])
    def test_login(self, case):
        username = cfg.admin_user if case["username"] == "$ADMIN_USER" else case["username"]
        password = cfg.admin_pwd if case["password"] == "$ADMIN_PASSWORD" else case["password"]
        expect_ok = case["expect_ok"]
        desc = f'{case["case_id"]} {case["desc"]}'
        allure.dynamic.title(desc)
        client = AuthClient(cfg.base_url, cfg.tenant_id)
        body = client.login(username, password).json()
        if expect_ok:
            assert_schema(body, LOGIN_SCHEMA)
            assert_api_ok(body, "正确登录")
            token = body.get("data", {}).get("accessToken")
            assert token, "token 为空"
        else:
            assert_api_fail(body, "错误登录")

    @allure.story("获取用户信息")
    @allure.title("AUTH_API_005 获取当前登录用户信息成功")
    @pytest.mark.smoke
    def test_get_info_success(self, auth_client):
        body = auth_client.get_info().json()
        assert_schema(body, GET_INFO_SCHEMA)
        assert_api_ok(body)
        assert body["data"]["user"], "用户信息为空"

    @allure.story("鉴权")
    @allure.title("AUTH_API_006 未携带 token 访问用户信息失败")
    def test_get_info_without_token(self):
        client = AuthClient(cfg.base_url, cfg.tenant_id)
        resp = client.get_info()
        assert resp.status_code == 401 or resp.json().get("code") != 0, \
            "未携带 token 仍可访问，鉴权失败"

    @allure.story("鉴权")
    @allure.title("AUTH_API_007 携带错误 token 访问用户信息失败")
    def test_get_info_with_bad_token(self):
        client = AuthClient(cfg.base_url, cfg.tenant_id)
        client.set_token("invalid_token_xxx")
        resp = client.get_info()
        assert resp.status_code == 401 or resp.json().get("code") != 0, \
            "错误 token 仍可访问，鉴权失败"

    @allure.story("退出登录")
    @allure.title("AUTH_API_008 退出登录成功 + AUTH_API_009 退出后 token 失效")
    def test_logout_and_token_invalid(self, logout_token):
        client = AuthClient(cfg.base_url, cfg.tenant_id)
        client.set_token(logout_token)
        body = assert_response_ok(client.logout(), "退出登录")
        resp = client.get_info()
        assert resp.status_code == 401 or resp.json().get("code") != 0, \
            "退出后 token 仍有效，逻辑错误"

    @allure.story("Token 生命周期")
    @allure.title("AUTH_API_010 refreshToken 可换取新 accessToken")
    def test_refresh_token(self, token_manager):
        old_token = token_manager.get_access_token()
        new_token = token_manager.refresh_access_token()
        assert new_token
        assert new_token != old_token, "刷新后 accessToken 未变化"

    @allure.story("Token 生命周期")
    @allure.title("AUTH_API_011 accessToken 失效后自动刷新并重试一次")
    def test_retry_after_unauthorized(self, auth_client, token_manager):
        token_manager.access_token = "invalid_token_for_retry"
        token_manager.expires_time_ms = int(time.time() * 1000) + 600_000
        body = assert_response_ok(auth_client.get_permission_info(), "401 后刷新重试")
        assert token_manager.access_token != "invalid_token_for_retry"

    @allure.story("fixture")
    @allure.title("AUTH_API_012 裸 admin_token 可创建独立鉴权 Client")
    def test_admin_token_fixture(self, admin_token):
        client = AuthClient(cfg.base_url, cfg.tenant_id)
        client.set_token(admin_token)
        assert_api_ok(client.get_permission_info().json(), "裸 Token 鉴权")
