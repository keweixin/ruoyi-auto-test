"""用户 接口+UI 联动测试。

覆盖 USER_FLOW_001 ~ 005：
- 接口创建用户 → UI 查询
- UI 创建用户 → 接口查询
- 接口禁用用户 → UI 登录失败
- 接口启用用户 → UI 登录成功
- UI 重置密码 → 接口验证新密码可登录

价值：体现接口依赖处理、用户登录验证、数据清理。
"""
import allure
import pytest

from common.config import cfg
from common.assert_utils import assert_api_ok, assert_api_fail
from common.random_utils import gen_name, gen_mobile
from api_auto.clients.user_client import UserClient
from api_auto.clients.auth_client import AuthClient
from ui_auto.pages.user_page import UserPage
from ui_auto.pages.login_page import LoginPage
from ui_auto.pages.home_page import HomePage


@allure.feature("用户 接口+UI 联动")
class TestUserFlow:

    @allure.title("USER_FLOW_001 接口创建用户，UI 查询用户")
    def test_api_create_ui_query(self, page, admin_token):
        """接口造用户 → UI 查询验证 → 接口清理。"""
        api = UserClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        username = gen_name("auto_flow")
        uid = api.create({
            "username": username, "password": "Test123456",
            "nickname": "联动用户", "mobile": gen_mobile(), "deptId": 100
        }).json()["data"]
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            assert up.row_exists(username), "UI 未查到接口创建的用户"
        finally:
            api.delete(uid)

    @allure.title("USER_FLOW_002 UI 创建用户，接口查询用户")
    def test_ui_create_api_query(self, page, admin_token):
        """UI 新增 → 接口查询确认 → 接口清理。"""
        up = UserPage(page)
        up.open_page()
        username = gen_name("auto_flow")
        up.add(username, "联动用户", gen_mobile())
        up.expect_toast("成功")

        api = UserClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        body = api.page({"pageNo": 1, "pageSize": 10, "username": username}).json()
        assert_api_ok(body)
        assert body["data"]["total"] >= 1, "接口未查到 UI 创建的用户"
        # 清理
        uid = body["data"]["list"][0]["id"]
        api.delete(uid)

    @allure.title("USER_FLOW_003 接口禁用用户，UI 登录失败")
    def test_api_disable_ui_login_fail(self, fresh_page, admin_token):
        """接口造用户 → 接口禁用 → UI 登录失败 → 接口清理。"""
        api = UserClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        username = gen_name("auto_flow")
        password = "Test123456"
        uid = api.create({
            "username": username, "password": password,
            "nickname": "禁用测试", "mobile": gen_mobile(), "deptId": 100
        }).json()["data"]
        try:
            api.update_status(uid, 1)  # 禁用
            # UI 用该用户登录应失败
            lp = LoginPage(fresh_page)
            lp.open()
            lp.login(username, password)
            assert "index" not in fresh_page.url, "禁用用户仍能 UI 登录"
        finally:
            api.delete(uid)

    @allure.title("USER_FLOW_004 接口启用用户，UI 登录成功")
    def test_api_enable_ui_login_success(self, fresh_page, admin_token):
        """接口造用户 → 禁用 → 启用 → UI 登录成功 → 接口清理。"""
        api = UserClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        username = gen_name("auto_flow")
        password = "Test123456"
        uid = api.create({
            "username": username, "password": password,
            "nickname": "启用测试", "mobile": gen_mobile(), "deptId": 100
        }).json()["data"]
        try:
            api.update_status(uid, 1)   # 禁用
            api.update_status(uid, 0)   # 启用
            # UI 登录
            lp = LoginPage(fresh_page)
            lp.open()
            lp.login(username, password)
            fresh_page.wait_for_url("**/index**", timeout=8000)
            assert "index" in fresh_page.url, "启用用户 UI 登录失败"
        finally:
            api.delete(uid)

    @allure.title("USER_FLOW_005 UI 重置密码，接口验证新密码可登录")
    def test_ui_reset_api_verify(self, page, admin_token):
        """接口造用户 → UI 重置密码 → 接口验证新密码可登录 → 接口清理。"""
        api = UserClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        username = gen_name("auto_flow")
        uid = api.create({
            "username": username, "password": "Test123456",
            "nickname": "重置测试", "mobile": gen_mobile(), "deptId": 100
        }).json()["data"]
        try:
            # UI 重置密码
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            new_pwd = "New123456"
            up.reset_password(username, new_pwd)
            up.expect_toast("成功")
            # 接口验证新密码可登录
            body = AuthClient(cfg.base_url, cfg.tenant_id).login(username, new_pwd).json()
            assert_api_ok(body, "新密码接口登录")
        finally:
            api.delete(uid)
