"""用户管理 UI 测试用例。

覆盖 USER_UI_001 ~ 010：
- 进入页面/按用户名/手机号搜索/新增/必填校验/编辑/禁用/启用/重置密码/删除

学习重点：表单校验、状态开关、重置密码弹窗。
"""
import allure
import pytest

from common.config import cfg
from common.random_utils import gen_name, gen_mobile
from ui_auto.pages.user_page import UserPage


@allure.feature("用户管理 UI")
class TestUserUi:

    @allure.title("USER_UI_001 进入用户管理页面成功")
    def test_open_user_page(self, page):
        up = UserPage(page)
        up.open_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("USER_UI_002 按用户名搜索成功")
    def test_search_by_username(self, page):
        up = UserPage(page)
        up.open_page()
        up.search_by_username("admin")
        assert up.table_row_count() >= 1

    @allure.title("USER_UI_003 按手机号搜索成功")
    def test_search_by_mobile(self, page, user_client):
        up = UserPage(page)
        username = gen_name("auto_user")
        mobile = gen_mobile()
        uid = user_client.create({
            "username": username,
            "password": "Test123456",
            "nickname": "自动用户",
            "mobile": mobile,
            "deptId": 100,
        }).json()["data"]
        try:
            up.open_page()
            up.search_by_mobile(mobile)
            assert up.row_exists(username), "按手机号未查到本次创建的用户"
        finally:
            user_client.delete(uid)

    @allure.title("USER_UI_004 新增后台用户成功")
    def test_add_user(self, page):
        up = UserPage(page)
        up.open_page()
        username = gen_name("auto_user")
        up.add(username, "自动用户", gen_mobile())
        up.expect_toast("成功")
        up.search_by_username(username)
        assert up.row_exists(username), "新增后表格未查到"

    @allure.title("USER_UI_005 新增用户必填项为空提示")
    def test_add_empty_required(self, page):
        up = UserPage(page)
        up.open_page()
        up.page.get_by_role("button", name="新增").click()
        dialog = up.page.locator(".el-dialog").first
        # 不填任何必填项直接确定
        dialog.get_by_role("button", name="确 定").click()
        assert up.page.locator(".el-form-item__error").count() > 0, "未出现必填校验"

    @allure.title("USER_UI_006 编辑用户成功")
    def test_edit_user(self, page):
        up = UserPage(page)
        up.open_page()
        username = gen_name("auto_user")
        up.add(username, "自动用户", gen_mobile())
        up.search_by_username(username)
        row = up.page.locator(".el-table__row").filter(has_text=username)
        row.get_by_role("button", name="修改").click()
        dialog = up.page.locator(".el-dialog").first
        nick = dialog.get_by_label("用户昵称")
        nick.fill("")
        nick.fill("已编辑")
        dialog.get_by_role("button", name="确 定").click()
        up.expect_toast("成功")

    @allure.title("USER_UI_007 禁用用户成功")
    def test_disable_user(self, page):
        up = UserPage(page)
        up.open_page()
        username = gen_name("auto_user")
        up.add(username, "自动用户", gen_mobile())
        up.search_by_username(username)
        row = up.page.locator(".el-table__row").filter(has_text=username)
        row.get_by_role("switch").click()
        up.expect_toast("成功")

    @allure.title("USER_UI_008 启用用户成功")
    def test_enable_user(self, page):
        up = UserPage(page)
        up.open_page()
        username = gen_name("auto_user")
        up.add(username, "自动用户", gen_mobile())
        up.search_by_username(username)
        row = up.page.locator(".el-table__row").filter(has_text=username)
        row.get_by_role("switch").click()
        row.get_by_role("switch").click()
        up.expect_toast("成功")

    @allure.title("USER_UI_009 重置密码成功")
    def test_reset_password(self, page):
        up = UserPage(page)
        up.open_page()
        username = gen_name("auto_user")
        up.add(username, "自动用户", gen_mobile())
        up.search_by_username(username)
        up.reset_password(username, "New123456")
        up.expect_toast("成功")

    @allure.title("USER_UI_010 删除测试用户成功")
    def test_delete_user(self, page):
        up = UserPage(page)
        up.open_page()
        username = gen_name("auto_user")
        up.add(username, "自动用户", gen_mobile())
        up.search_by_username(username)
        up.delete_row(username)
        up.expect_toast("成功")
