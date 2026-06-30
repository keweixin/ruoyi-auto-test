"""菜单管理接口测试用例。

覆盖 MENU_API_001 ~ 006：
- 查询列表 + 新增菜单 + 新增按钮权限 + 编辑 + 删除 + 给角色分配后查询

学习重点：菜单树、菜单类型(目录/菜单/按钮)、权限验证基础。
"""
import allure
import pytest

from common.config import cfg
from common.assert_utils import assert_api_ok, assert_api_fail
from common.random_utils import gen_name


@allure.feature("菜单管理接口")
class TestMenuApi:

    @allure.story("查询")
    @allure.title("MENU_API_001 查询菜单列表成功")
    def test_list_menu(self, menu_client):
        body = menu_client.list().json()
        assert_api_ok(body)
        assert isinstance(body["data"], list) and len(body["data"]) > 0

    @allure.story("新增")
    @allure.title("MENU_API_002 新增菜单成功")
    def test_create_menu(self, menu_client):
        data = {
            "parentId": 0, "name": gen_name("auto_menu"),
            "type": 2, "path": gen_name("auto"), "sort": 1, "status": 0
        }
        body = menu_client.create(data).json()
        assert_api_ok(body, "新增菜单")
        assert body["data"]
        menu_client.delete(body["data"])

    @allure.story("新增")
    @allure.title("MENU_API_003 新增按钮权限成功")
    def test_create_button(self, menu_client):
        """type=3 是按钮。挂在某个已有菜单下。"""
        # 先建一个菜单当父
        parent_id = menu_client.create({
            "parentId": 0, "name": gen_name("auto_menu"),
            "type": 2, "path": gen_name("auto"), "sort": 1, "status": 0
        }).json()["data"]
        try:
            body = menu_client.create({
                "parentId": parent_id, "name": gen_name("auto_btn"),
                "type": 3, "path": "", "sort": 1, "status": 0
            }).json()
            assert_api_ok(body, "新增按钮权限")
            menu_client.delete(body["data"])
        finally:
            menu_client.delete(parent_id)

    @allure.story("修改")
    @allure.title("MENU_API_004 编辑菜单成功")
    def test_update_menu(self, menu_client):
        new_id = menu_client.create({
            "parentId": 0, "name": gen_name("auto_menu"),
            "type": 2, "path": gen_name("auto"), "sort": 1, "status": 0
        }).json()["data"]
        try:
            body = menu_client.update({
                "id": new_id, "parentId": 0, "name": gen_name("auto_menu_edited"),
                "type": 2, "path": gen_name("auto_edited"), "sort": 2, "status": 0
            }).json()
            assert_api_ok(body, "编辑菜单")
        finally:
            menu_client.delete(new_id)

    @allure.story("删除")
    @allure.title("MENU_API_005 删除测试菜单成功")
    def test_delete_menu(self, menu_client):
        new_id = menu_client.create({
            "parentId": 0, "name": gen_name("auto_menu"),
            "type": 2, "path": gen_name("auto"), "sort": 1, "status": 0
        }).json()["data"]
        body = menu_client.delete(new_id).json()
        assert_api_ok(body, "删除菜单")

    @allure.story("权限分配")
    @allure.title("MENU_API_006 给角色分配菜单后查询成功")
    def test_assign_then_query(self, menu_client, role_client, permission_client):
        """新建菜单 → 分配给角色 → 查询角色菜单确认存在。"""
        rid = role_client.create({
            "name": gen_name("auto_role"), "code": gen_name("auto_role_code"),
            "sort": 1, "status": 0, "remark": "auto"
        }).json()["data"]
        menu_id = menu_client.create({
            "parentId": 0, "name": gen_name("auto_menu"),
            "type": 2, "path": gen_name("auto"), "sort": 1, "status": 0
        }).json()["data"]
        try:
            permission_client.assign_role_menu(rid, [menu_id])
            body = permission_client.list_role_menus(rid).json()
            assert_api_ok(body)
            assert menu_id in set(body["data"]), "分配的菜单未查到"
        finally:
            permission_client.assign_role_menu(rid, [])  # 解绑
            menu_client.delete(menu_id)
            role_client.delete(rid)
