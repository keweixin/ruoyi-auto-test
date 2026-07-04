"""角色管理 UI 测试用例（Vue3 / Element Plus）。

策略：角色数据优先由 API 创建，UI 层验证页面打开、查询、展示、删除确认和菜单权限弹窗。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok
from common.random_utils import gen_name
from ui_auto.pages.role_page import RolePage


@allure.feature("角色管理 UI")
@pytest.mark.ui
class TestRoleUi:

    def _create_role(self, role_client, status=0):
        name = gen_name("auto_role")
        code = gen_name("auto_code")
        body = role_client.create({"name": name, "code": code, "sort": 1, "status": status}).json()
        assert_api_ok(body, "API 创建角色")
        return body["data"], name, code

    @allure.title("ROLE_UI_001 进入角色管理页面成功")
    def test_open_role_page(self, page):
        rp = RolePage(page)
        rp.open_page()
        assert rp.is_table_visible()

    @allure.title("ROLE_UI_002 新增角色后页面可查询")
    def test_add_role(self, page, role_client):
        rid, name, _ = self._create_role(role_client)
        try:
            rp = RolePage(page)
            rp.open_page()
            rp.search_by_name(name)
            assert rp.row_exists(name)
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_UI_003 按角色名称查询成功")
    def test_search_role(self, page, role_client):
        rid, name, _ = self._create_role(role_client)
        try:
            rp = RolePage(page)
            rp.open_page()
            rp.search_by_name(name)
            assert rp.table_row_count() >= 1
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_UI_004 编辑角色成功")
    def test_edit_role(self, page, role_client):
        rid, name, code = self._create_role(role_client)
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(role_client.update({"id": rid, "name": new_name, "code": code, "sort": 1, "status": 0}).json())
            rp = RolePage(page)
            rp.open_page()
            rp.search_by_name(new_name)
            assert rp.row_exists(new_name)
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_UI_005 禁用角色成功")
    def test_disable_role(self, page, role_client):
        rid, name, code = self._create_role(role_client)
        try:
            assert_api_ok(role_client.update({"id": rid, "name": name, "code": code, "sort": 1, "status": 1}).json())
            rp = RolePage(page)
            rp.open_page()
            rp.search_by_name(name)
            assert "关闭" in rp.table_row_by_keyword(name).inner_text()
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_UI_006 启用角色成功")
    def test_enable_role(self, page, role_client):
        rid, name, code = self._create_role(role_client, status=1)
        try:
            assert_api_ok(role_client.update({"id": rid, "name": name, "code": code, "sort": 1, "status": 0}).json())
            rp = RolePage(page)
            rp.open_page()
            rp.search_by_name(name)
            assert "开启" in rp.table_row_by_keyword(name).inner_text()
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_UI_007 分配菜单权限弹窗可打开并提交")
    def test_assign_menu(self, page, role_client):
        rid, name, _ = self._create_role(role_client)
        try:
            rp = RolePage(page)
            rp.open_page()
            rp.search_by_name(name)
            rp.assign_menu(name, menu_names=["系统管理"])
            rp.expect_toast("成功")
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_UI_008 删除角色成功")
    def test_delete_role(self, page, role_client):
        rid, name, _ = self._create_role(role_client)
        rp = RolePage(page)
        rp.open_page()
        rp.search_by_name(name)
        rp.delete_row(name)
        rp.expect_toast("成功")
        body = role_client.get(rid).json()
        assert body.get("code") != 0 or not body.get("data"), "UI 删除后接口仍能查到角色"
