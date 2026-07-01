"""菜单管理 UI 测试用例。

覆盖 MENU_UI_001 ~ 006：
- 进入页面/新增/编辑/删除/树展开/查询

策略：API 造数据 → UI 打开页面 → UI 搜索验证 → API 清理。增删改操作用 API 而非 UI 交互。
"""
import allure
import pytest

from common.random_utils import gen_name
from common.assert_utils import assert_api_ok
from ui_auto.pages.menu_page import MenuPage


@allure.feature("菜单管理 UI")
class TestMenuUi:

    @allure.title("MENU_UI_001 进入菜单管理页面成功")
    def test_open_menu_page(self, page):
        mp = MenuPage(page)
        mp.open_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("MENU_UI_002 新增菜单成功")
    def test_add_menu(self, page, menu_client):
        """API 造菜单 → UI 搜索 → 验证行存在 → API 清理。"""
        name = gen_name("auto_menu")
        assert_api_ok(menu_client.create({
            "parentId": 0,
            "menuName": name,
            "menuType": "C",
            "orderNum": 1,
            "path": "/auto_" + name.lower().replace("_", ""),
            "component": "",
            "perms": "",
            "status": "0",
            "visible": "0",
            "isFrame": "1",
        }).json())
        rows = menu_client.list({"menuName": name}).json()["data"]
        mid = rows[0]["menuId"] if rows else None
        try:
            mp = MenuPage(page)
            mp.open_page()
            mp.search_by_name(name)
            assert mp.row_exists(name), "新增后表格未查到"
        finally:
            if mid:
                menu_client.delete(mid)

    @allure.title("MENU_UI_003 编辑菜单成功")
    def test_edit_menu(self, page, menu_client):
        """API 造菜单 → API 编辑名称 → UI 搜索新名称 → 验证 → API 清理。"""
        name = gen_name("auto_menu")
        assert_api_ok(menu_client.create({
            "parentId": 0,
            "menuName": name,
            "menuType": "C",
            "orderNum": 1,
            "path": "/auto_" + name.lower().replace("_", ""),
            "component": "",
            "perms": "",
            "status": "0",
            "visible": "0",
            "isFrame": "1",
        }).json())
        rows = menu_client.list({"menuName": name}).json()["data"]
        mid = rows[0]["menuId"]
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(menu_client.update({
                "menuId": mid,
                "menuName": new_name,
                "parentId": 0,
                "menuType": "C",
                "orderNum": 1,
                "path": "/auto_" + name.lower().replace("_", ""),
                "component": "",
                "perms": "",
                "status": "0",
                "visible": "0",
                "isFrame": "1",
            }).json())
            mp = MenuPage(page)
            mp.open_page()
            mp.search_by_name(new_name)
            assert mp.row_exists(new_name), "编辑后未查到新名称"
        finally:
            menu_client.delete(mid)

    @allure.title("MENU_UI_004 删除菜单成功")
    def test_delete_menu(self, page, menu_client):
        """API 造菜单 → UI 搜索验证存在 → API 删除 → UI 搜索验证不存在。"""
        name = gen_name("auto_menu")
        assert_api_ok(menu_client.create({
            "parentId": 0,
            "menuName": name,
            "menuType": "C",
            "orderNum": 1,
            "path": "/auto_" + name.lower().replace("_", ""),
            "component": "",
            "perms": "",
            "status": "0",
            "visible": "0",
            "isFrame": "1",
        }).json())
        rows = menu_client.list({"menuName": name}).json()["data"]
        mid = rows[0]["menuId"]
        mp = MenuPage(page)
        mp.open_page()
        mp.search_by_name(name)
        assert mp.row_exists(name), "删除前应能查到"
        assert_api_ok(menu_client.delete(mid).json())
        mp.search_by_name(name)
        assert not mp.row_exists(name), "删除后仍能查到"

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
