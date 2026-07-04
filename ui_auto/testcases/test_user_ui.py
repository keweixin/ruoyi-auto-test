"""用户管理 UI 测试用例（Vue3 / Element Plus）。

策略：用户数据优先由 API 创建，UI 层验证页面打开、查询、展示、删除确认、重置密码等关键用户可见行为。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok
from common.random_utils import gen_mobile, gen_username
from ui_auto.pages.user_page import UserPage


@allure.feature("用户管理 UI")
@pytest.mark.ui
class TestUserUi:

    def _create_user(self, user_client, status=0):
        username = gen_username()
        mobile = gen_mobile()
        body = user_client.create({
            "username": username,
            "password": "Test123456",
            "nickname": "自动用户",
            "mobile": mobile,
            "deptId": 100,
        }).json()
        assert_api_ok(body, "API 创建用户")
        uid = body["data"]
        if status != 0:
            assert_api_ok(user_client.update_status(uid, status).json())
        return uid, username, mobile

    @allure.title("USER_UI_001 进入用户管理页面成功")
    def test_open_user_page(self, page):
        up = UserPage(page)
        up.open_page()
        assert up.is_table_visible()

    @allure.title("USER_UI_002 按用户名搜索成功")
    def test_search_by_username(self, page, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            assert up.row_exists(username)
        finally:
            user_client.delete(uid)

    @allure.title("USER_UI_003 按手机号搜索成功")
    def test_search_by_mobile(self, page, user_client):
        uid, username, mobile = self._create_user(user_client)
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_mobile(mobile)
            assert up.row_exists(username), "按手机号未查到本次创建的用户"
        finally:
            user_client.delete(uid)

    @allure.title("USER_UI_004 新增后台用户后页面可查询")
    def test_add_user(self, page, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            assert up.row_exists(username), "新增后表格未查到"
        finally:
            user_client.delete(uid)

    @allure.title("USER_UI_005 新增用户必填项为空提示")
    def test_add_empty_required(self, page):
        up = UserPage(page)
        up.open_page()
        assert up.submit_empty_form() > 0, "空必填项提交后应显示校验错误"

    @allure.title("USER_UI_006 编辑用户成功")
    def test_edit_user(self, page, user_client):
        uid, username, mobile = self._create_user(user_client)
        try:
            assert_api_ok(user_client.update({
                "id": uid,
                "username": username,
                "nickname": "已编辑",
                "mobile": mobile,
                "deptId": 100,
            }).json())
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            assert "已编辑" in up.table_row_by_keyword(username).inner_text()
        finally:
            user_client.delete(uid)

    @allure.title("USER_UI_007 禁用用户成功")
    def test_disable_user(self, page, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            assert_api_ok(user_client.update_status(uid, 1).json())
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            assert up.row_exists(username)
            assert not up.is_enabled(username), "禁用后页面状态开关仍为开启"
        finally:
            user_client.delete(uid)

    @allure.title("USER_UI_008 启用用户成功")
    def test_enable_user(self, page, user_client):
        uid, username, _ = self._create_user(user_client, status=1)
        try:
            assert_api_ok(user_client.update_status(uid, 0).json())
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            assert up.row_exists(username)
            assert up.is_enabled(username), "启用后页面状态开关未开启"
        finally:
            user_client.delete(uid)

    @allure.title("USER_UI_009 重置密码成功")
    def test_reset_password(self, page, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            up.reset_password(username, "New123456")
            up.expect_toast("成功")
        finally:
            user_client.delete(uid)

    @allure.title("USER_UI_010 删除测试用户成功")
    def test_delete_user(self, page, user_client):
        uid, username, _ = self._create_user(user_client)
        up = UserPage(page)
        up.open_page()
        up.search_by_username(username)
        up.delete_row(username)
        up.expect_toast("成功")
        body = user_client.get(uid).json()
        assert body.get("code") != 0 or not body.get("data"), "UI 删除后接口仍能查到用户"
