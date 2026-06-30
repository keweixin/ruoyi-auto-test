"""登录认证接口测试用例。

覆盖 AUTH_API_001 ~ 009：
- 正确/错误/空用户名/空密码 登录（参数化）
- 获取登录用户信息
- 未带 token / 错误 token 访问（鉴权）
- 退出登录 + 退出后 token 失效

学习重点：token 获取、请求头封装、登录状态管理、鉴权验证。
"""
import allure
import pytest

from common.config import cfg
from common.assert_utils import assert_api_ok, assert_api_fail
from api_auto.clients.auth_client import AuthClient


@allure.feature("登录认证接口")
class TestAuthApi:

    @allure.story("登录")
    @pytest.mark.parametrize("username,password,expect_ok,desc", [
        (cfg.admin_user, cfg.admin_pwd, True,  "AUTH_API_001 正确账号密码登录成功"),
        (cfg.admin_user, "wrong_pwd",   False, "AUTH_API_002 错误密码登录失败"),
        ("",             cfg.admin_pwd, False, "AUTH_API_003 用户名为空登录失败"),
        (cfg.admin_user, "",            False, "AUTH_API_004 密码为空登录失败"),
    ], ids=["正确登录", "错误密码", "空用户名", "空密码"])
    def test_login(self, username, password, expect_ok, desc):
        """AUTH_API_001~004：登录正反向场景。"""
        allure.dynamic.title(desc)
        client = AuthClient(cfg.base_url, cfg.tenant_id)
        body = client.login(username, password).json()

        if expect_ok:
            assert_api_ok(body, "正确登录")
            assert body["data"]["accessToken"], "token 为空"
        else:
            assert_api_fail(body, "错误登录")

    @allure.story("获取用户信息")
    @allure.title("AUTH_API_005 获取当前登录用户信息成功")
    def test_get_permission_info_success(self, auth_client):
        """AUTH_API_005：已登录获取用户信息。"""
        body = auth_client.get_permission_info().json()
        assert_api_ok(body)
        assert body["data"]["user"], "用户信息为空"
        assert body["data"]["menus"], "菜单列表为空"

    @allure.story("鉴权")
    @allure.title("AUTH_API_006 未携带 token 访问用户信息失败")
    def test_get_info_without_token(self):
        """AUTH_API_006：不带 token 访问受保护接口，应被拒。"""
        client = AuthClient(cfg.base_url, cfg.tenant_id)  # 不 set_token
        resp = client.get_permission_info()
        # 401 表示未认证
        assert resp.status_code == 401 or resp.json().get("code") != 0, \
            "未携带 token 仍可访问，鉴权失败"

    @allure.story("鉴权")
    @allure.title("AUTH_API_007 携带错误 token 访问用户信息失败")
    def test_get_info_with_bad_token(self):
        """AUTH_API_007：带错误 token 访问，应被拒。"""
        client = AuthClient(cfg.base_url, cfg.tenant_id)
        client.set_token("invalid_token_xxx")
        resp = client.get_permission_info()
        assert resp.status_code == 401 or resp.json().get("code") != 0, \
            "错误 token 仍可访问，鉴权失败"

    @allure.story("退出登录")
    @allure.title("AUTH_API_008 退出登录成功 + AUTH_API_009 退出后 token 失效")
    def test_logout_and_token_invalid(self, logout_token):
        """AUTH_API_008/009：使用独立 token 退出，避免污染 session 级 admin_token。"""
        client = AuthClient(cfg.base_url, cfg.tenant_id)
        client.set_token(logout_token)

        body = client.logout().json()
        assert_api_ok(body, "退出登录")

        resp = client.get_permission_info()
        assert resp.status_code == 401 or resp.json().get("code") != 0, \
            "退出后 token 仍有效，逻辑错误"
