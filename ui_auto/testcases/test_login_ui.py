"""登录模块 UI 测试用例。

覆盖 AUTH_UI_001 ~ 008：
- 正确/错误/空用户名/空密码/登录后进首页/菜单展示/退出/未登录跳转

学习重点：UI 表单输入、Toast 断言、URL 断言、登录态。
注意：登录类用例用 fresh_page（无登录态），否则无法测登录流程。
"""
import json
from pathlib import Path

import allure
import pytest

from common.config import cfg
from ui_auto.pages.login_page import LoginPage
from ui_auto.pages.home_page import HomePage
from ui_auto.auth.auth_state_manager import AuthStateManager


@allure.feature("登录模块 UI")
@pytest.mark.ui
class TestLoginUi:

    @allure.title("AUTH_UI_001 正确账号密码登录成功")
    def test_login_success(self, fresh_page):
        lp = LoginPage(fresh_page)
        lp.open()
        lp.login_as_admin()
        # 断言进入首页
        assert HomePage(fresh_page).is_home_page(), "登录后未进入首页"

    @allure.title("AUTH_UI_002 错误密码登录失败")
    def test_login_wrong_pwd(self, fresh_page):
        lp = LoginPage(fresh_page)
        lp.open()
        lp.login(cfg.admin_user, "wrong_pwd")
        # 断言出现错误提示 Toast
        toast = lp.get_error_toast()
        assert toast, "未出现错误提示"
        # 仍停留在登录页
        assert lp.is_login_page()

    @allure.title("AUTH_UI_003 用户名为空提示")
    def test_login_empty_username(self, fresh_page):
        lp = LoginPage(fresh_page)
        lp.open()
        lp.login("", cfg.admin_pwd)
        assert lp.validation_error_count() > 0, "空用户名未显示表单校验状态"
        assert lp.is_login_page(), "空用户名仍登录成功"

    @allure.title("AUTH_UI_004 密码为空提示")
    def test_login_empty_password(self, fresh_page):
        lp = LoginPage(fresh_page)
        lp.open()
        lp.login(cfg.admin_user, "")
        assert lp.validation_error_count() > 0, "空密码未显示表单校验状态"
        assert lp.is_login_page(), "空密码仍登录成功"

    @allure.title("AUTH_UI_005 登录后进入首页")
    def test_login_then_home(self, fresh_page):
        lp = LoginPage(fresh_page)
        lp.open()
        lp.login_as_admin()
        hp = HomePage(fresh_page)
        assert hp.is_home_page(), "未进入首页"

    @allure.title("AUTH_UI_006 登录后菜单展示正常")
    def test_login_menu_display(self, fresh_page):
        lp = LoginPage(fresh_page)
        lp.open()
        lp.login_as_admin()
        hp = HomePage(fresh_page)
        assert hp.is_home_page()
        # admin 应能看到系统管理菜单
        assert hp.has_menu("系统管理") or hp.has_menu("字典管理"), "菜单未正常展示"

    @allure.title("AUTH_UI_007 退出登录成功")
    def test_logout(self, fresh_page):
        """使用独立 fresh_page 登录后退出，避免污染共享 storage_state。"""
        lp = LoginPage(fresh_page)
        lp.open()
        lp.login_as_admin()
        assert HomePage(fresh_page).is_home_page(timeout=10000)

        hp = HomePage(fresh_page)
        hp.logout()
        lp.wait_url("/login", timeout=8000)
        assert lp.is_login_page()

    @allure.title("AUTH_UI_008 未登录访问首页跳回登录页")
    def test_unauth_redirect(self, fresh_page):
        lp = LoginPage(fresh_page)
        lp.open_protected_page()
        assert lp.is_login_page()

    @allure.title("AUTH_UI_009 storage_state 失效后自动重新登录")
    def test_expired_storage_state_recovers(self, browser, tmp_path):
        state_path = tmp_path / "expired-state.json"
        state_path.write_text("{invalid-json", encoding="utf-8")
        manager = AuthStateManager(browser, state_path, cfg)
        context, authenticated_page = manager.new_authenticated_page()
        try:
            assert HomePage(authenticated_page).is_home_page(), "失效登录态未自动恢复"
        finally:
            context.close()

    @allure.title("AUTH_UI_010 storage_state 文件结构合法")
    def test_storage_state_fixture(self, storage_state):
        state_path = Path(storage_state)
        assert state_path.is_file()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert isinstance(state.get("cookies"), list)
        assert isinstance(state.get("origins"), list)
