"""菜单管理 UI 测试用例（Vue3 / Element Plus）。

说明：菜单会影响前端动态路由，UI 层不直接新增/删除真实菜单，避免破坏当前登录态。
这里验证页面、查询、弹窗、树形展示、操作按钮等用户可见行为；菜单 CRUD 由 API 层覆盖。
"""
import allure
import pytest

from ui_auto.pages.menu_page import MenuPage


@allure.feature("菜单管理 UI")
@pytest.mark.ui
class TestMenuUi:

    @allure.title("MENU_UI_001 进入菜单管理页面成功")
    def test_open_menu_page(self, page):
        mp = MenuPage(page)
        mp.open_page()
        assert mp.text_exists("菜单名称")

    @allure.title("MENU_UI_002 新增菜单弹窗可打开")
    def test_add_menu(self, page):
        mp = MenuPage(page)
        mp.open_page()
        assert mp.add_dialog_has_required_fields()

    @allure.title("MENU_UI_003 新增菜单必填项为空不提交")
    def test_add_menu_empty_required(self, page):
        mp = MenuPage(page)
        mp.open_page()
        assert mp.submit_empty_form() > 0, "空必填项提交后应显示校验错误"

    @allure.title("MENU_UI_004 操作列按钮可见")
    def test_delete_menu(self, page):
        mp = MenuPage(page)
        mp.open_page()
        assert mp.has_operation("修改")
        assert mp.has_operation("删除")

    @allure.title("MENU_UI_005 菜单树结构展示成功")
    def test_expand_menu_tree(self, page):
        mp = MenuPage(page)
        mp.open_page()
        assert mp.text_exists("系统管理")

    @allure.title("MENU_UI_006 按菜单名称查询成功")
    def test_search_menu(self, page):
        mp = MenuPage(page)
        mp.open_page()
        mp.search_by_name("系统管理")
        assert mp.text_exists("系统管理")
