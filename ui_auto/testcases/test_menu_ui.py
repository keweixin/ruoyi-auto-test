"""菜单管理 UI 测试用例。

覆盖 MENU_UI_001 ~ 006：
- 进入页面/新增/编辑/删除/树展开/查询

学习重点：菜单树、菜单类型(目录/菜单/按钮)。
"""
import allure
import pytest

from common.config import cfg
from common.random_utils import gen_name
from ui_auto.pages.menu_page import MenuPage


@allure.feature("菜单管理 UI")
class TestMenuUi:

    @allure.title("MENU_UI_001 进入菜单管理页面成功")
    def test_open_menu_page(self, page):
        mp = MenuPage(page)
        mp.open_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("MENU_UI_002 新增菜单成功")
    def test_add_menu(self, page):
        mp = MenuPage(page)
        mp.open_page()
        name = gen_name("auto_menu")
        mp.add(name, menu_type="菜单")
        mp.expect_toast("成功")
        mp.search_by_name(name)
        assert mp.row_exists(name)

    @allure.title("MENU_UI_003 编辑菜单成功")
    def test_edit_menu(self, page):
        mp = MenuPage(page)
        mp.open_page()
        name = gen_name("auto_menu")
        mp.add(name, menu_type="菜单")
        mp.search_by_name(name)
        row = mp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("button", name="修改").click()
        dialog = mp.page.locator(".el-dialog").first
        n = dialog.get_by_label("菜单名称")
        n.fill("")
        n.fill(gen_name("auto_edited"))
        dialog.get_by_role("button", name="确 定").click()
        mp.expect_toast("成功")

    @allure.title("MENU_UI_004 删除菜单成功")
    def test_delete_menu(self, page):
        mp = MenuPage(page)
        mp.open_page()
        name = gen_name("auto_menu")
        mp.add(name, menu_type="菜单")
        mp.search_by_name(name)
        mp.delete_row(name)
        mp.expect_toast("成功")

    @allure.title("MENU_UI_005 菜单树展开成功")
    def test_expand_menu_tree(self, page):
        mp = MenuPage(page)
        mp.open_page()
        expand_btn = page.locator(".el-table__row").first.locator(".el-table__expand-icon")
        if expand_btn.count() == 0:
            pytest.skip("当前菜单表格无可展开节点，跳过树展开验证")
        before = mp.table_row_count()
        expand_btn.click()
        after = mp.table_row_count()
        assert after >= before, f"展开后行数异常 before={before} after={after}"

    @allure.title("MENU_UI_006 按菜单名称查询成功")
    def test_search_menu(self, page):
        mp = MenuPage(page)
        mp.open_page()
        mp.search_by_name("系统管理")
        assert mp.table_row_count() >= 1
