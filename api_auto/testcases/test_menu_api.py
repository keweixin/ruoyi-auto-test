"""菜单管理接口测试用例（RuoYi v3.9.2 原版）。

原版字段：parentId/menuName/menuType(M目录 C菜单 F按钮)/path/orderNum/status。
表 sys_menu(主键menu_id, del_flag)。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok
from common.random_utils import gen_name


@allure.feature("菜单管理接口")
class TestMenuApi:

    @allure.title("MENU_API_001 查询菜单列表成功")
    def test_list_menu(self, menu_client):
        body = menu_client.list().json()
        assert_api_ok(body)
        assert isinstance(body["data"], list) and len(body["data"]) > 0

    @allure.title("MENU_API_002 新增菜单成功")
    def test_create_menu(self, menu_client):
        data = {"parentId": 0, "menuName": gen_name("auto_menu"), "menuType": "M", "orderNum": 1, "path": "auto", "status": "0"}
        body = menu_client.create(data).json()
        assert_api_ok(body, "新增菜单")
        rows = menu_client.list({"menuName": data["menuName"]}).json()["data"]
        try:
            assert any(r["menuName"] == data["menuName"] for r in rows), "未查到新增菜单"
        finally:
            if rows:
                menu_client.delete(rows[0]["menuId"])

    @allure.title("MENU_API_003 新增按钮权限成功")
    def test_create_button(self, menu_client):
        parent_name = gen_name("auto_menu")
        parent_id = menu_client.create({"parentId": 0, "menuName": parent_name, "menuType": "M", "orderNum": 1, "path": "auto", "status": "0"}).json()
        assert_api_ok(parent_id)
        parent_rows = menu_client.list({"menuName": parent_name}).json()["data"]
        pid = parent_rows[0]["menuId"]
        try:
            body = menu_client.create({"parentId": pid, "menuName": gen_name("auto_btn"), "menuType": "F", "orderNum": 1, "path": "", "perms": "auto:btn", "status": "0"}).json()
            assert_api_ok(body, "新增按钮权限")
            btn_rows = menu_client.list({"menuName": "auto_btn"}).json()["data"]
            if btn_rows:
                menu_client.delete(btn_rows[0]["menuId"])
        finally:
            menu_client.delete(pid)

    @allure.title("MENU_API_004 编辑菜单成功")
    def test_update_menu(self, menu_client):
        name = gen_name("auto_menu")
        menu_client.create({"parentId": 0, "menuName": name, "menuType": "M", "orderNum": 1, "path": "auto", "status": "0"})
        rows = menu_client.list({"menuName": name}).json()["data"]
        mid = rows[0]["menuId"]
        try:
            body = menu_client.update({"menuId": mid, "parentId": 0, "menuName": gen_name("auto_edited"), "menuType": "M", "orderNum": 2, "path": "auto2", "status": "0"}).json()
            assert_api_ok(body, "编辑菜单")
        finally:
            menu_client.delete(mid)

    @allure.title("MENU_API_005 删除测试菜单成功")
    def test_delete_menu(self, menu_client):
        name = gen_name("auto_menu")
        menu_client.create({"parentId": 0, "menuName": name, "menuType": "M", "orderNum": 1, "path": "auto", "status": "0"})
        rows = menu_client.list({"menuName": name}).json()["data"]
        mid = rows[0]["menuId"]
        body = menu_client.delete(mid).json()
        assert_api_ok(body, "删除菜单")

    @allure.title("MENU_API_006 给角色分配菜单后查询成功")
    def test_assign_then_query(self, menu_client, role_client, permission_client):
        rid, rname, rkey = (lambda n, k: (
            role_client.create({"roleName": n, "roleKey": k, "roleSort": 1, "status": "0", "menuIds": [1, 2]}).json(),
            n, k
        ))(gen_name("auto_role"), gen_name("auto_key"))
        # 查 id
        role_rows = role_client.page({"roleName": rname}).json()["rows"]
        role_id = role_rows[0]["roleId"]
        try:
            ids = permission_client.get_role_menu_ids(role_id)
            assert 1 in set(ids), "分配的菜单未查到"
        finally:
            role_client.delete(role_id)
