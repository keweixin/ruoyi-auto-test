"""角色管理 UI 测试用例。

覆盖 ROLE_UI_001 ~ 008：
- 进入页面/新增/查询/编辑/禁用/启用/分配菜单权限/删除

学习重点：权限系统、菜单树勾选、数据库中间表校验。
"""
import allure
import pytest

from common.config import cfg
from common.random_utils import gen_name
from ui_auto.pages.role_page import RolePage


@allure.feature("角色管理 UI")
class TestRoleUi:

    @allure.title("ROLE_UI_001 进入角色管理页面成功")
    def test_open_role_page(self, page):
        rp = RolePage(page)
        rp.open_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("ROLE_UI_002 新增角色成功")
    def test_add_role(self, page):
        rp = RolePage(page)
        rp.open_page()
        name = gen_name("auto_role")
        code = gen_name("auto_code")
        rp.add(name, code)
        rp.expect_toast("成功")
        rp.search_by_name(name)
        assert rp.row_exists(name)

    @allure.title("ROLE_UI_003 按角色名称查询成功")
    def test_search_role(self, page):
        rp = RolePage(page)
        rp.open_page()
        rp.search_by_name("超级管理员")
        assert rp.table_row_count() >= 1

    @allure.title("ROLE_UI_004 编辑角色成功")
    def test_edit_role(self, page):
        rp = RolePage(page)
        rp.open_page()
        name = gen_name("auto_role")
        rp.add(name, gen_name("auto_code"))
        rp.search_by_name(name)
        row = rp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("button", name="修改").click()
        dialog = rp.page.locator(".el-dialog").first
        n = dialog.get_by_label("角色名称")
        n.fill("")
        n.fill(gen_name("auto_edited"))
        dialog.get_by_role("button", name="确 定").click()
        rp.expect_toast("成功")

    @allure.title("ROLE_UI_005 禁用角色成功")
    def test_disable_role(self, page):
        rp = RolePage(page)
        rp.open_page()
        name = gen_name("auto_role")
        rp.add(name, gen_name("auto_code"))
        rp.search_by_name(name)
        row = rp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("switch").click()
        rp.expect_toast("成功")

    @allure.title("ROLE_UI_006 启用角色成功")
    def test_enable_role(self, page):
        rp = RolePage(page)
        rp.open_page()
        name = gen_name("auto_role")
        rp.add(name, gen_name("auto_code"))
        rp.search_by_name(name)
        row = rp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("switch").click()
        row.get_by_role("switch").click()
        rp.expect_toast("成功")

    @allure.title("ROLE_UI_007 分配菜单权限成功")
    def test_assign_menu(self, page):
        rp = RolePage(page)
        rp.open_page()
        name = gen_name("auto_role")
        rp.add(name, gen_name("auto_code"))
        rp.search_by_name(name)
        rp.assign_menu(name, menu_names=["字典管理"])
        rp.expect_toast("成功")

    @allure.title("ROLE_UI_008 删除角色成功")
    def test_delete_role(self, page):
        rp = RolePage(page)
        rp.open_page()
        name = gen_name("auto_role")
        rp.add(name, gen_name("auto_code"))
        rp.search_by_name(name)
        rp.delete_row(name)
        rp.expect_toast("成功")
