"""角色管理接口测试用例（RuoYi v3.9.2 原版）。

原版字段：roleName/roleKey/roleSort/status；菜单分配在创建时通过 menuIds。
表 sys_role(主键role_id, role_key, del_flag) / sys_role_menu。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA, DETAIL_SCHEMA


def _create_role(role_client, menu_ids=None):
    name = gen_name("auto_role")
    key = gen_name("auto_key")
    body = role_client.create({
        "roleName": name, "roleKey": key, "roleSort": 1, "status": "0", "remark": "auto",
        "menuIds": menu_ids or []
    }).json()
    assert_api_ok(body, "创建角色")
    rows = role_client.page({"roleName": name}).json()["rows"]
    return rows[0]["roleId"], name, key


@allure.feature("角色管理接口")
@pytest.mark.api
class TestRoleApi:

    @allure.title("ROLE_API_001 新增角色成功")
    @pytest.mark.smoke
    def test_create_role(self, role_client):
        rid, name, key = _create_role(role_client)
        assert rid
        role_client.delete(rid)

    @allure.title("ROLE_API_002 新增角色名称为空失败")
    def test_create_empty_name(self, role_client):
        body = role_client.create({"roleName": "", "roleKey": gen_name("k"), "roleSort": 1, "status": "0", "menuIds": []}).json()
        assert_api_fail(body, "名称为空")

    @allure.title("ROLE_API_003 新增重复角色失败")
    def test_create_duplicate(self, role_client):
        rid, name, key = _create_role(role_client)
        try:
            body = role_client.create({"roleName": name, "roleKey": key, "roleSort": 1, "status": "0", "menuIds": []}).json()
            assert_api_fail(body, "重复新增")
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_API_004 查询角色列表成功")
    @pytest.mark.smoke
    def test_page_role(self, role_client):
        rid, name, key = _create_role(role_client)
        try:
            body = role_client.page({"roleName": name}).json()
            assert_schema(body, PAGE_LIST_SCHEMA)
            assert_api_ok(body)
            assert any(r["roleId"] == rid and r["roleName"] == name for r in body["rows"]), "未查到本次角色"
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_API_005 编辑角色成功")
    def test_update_role(self, role_client):
        rid, name, key = _create_role(role_client)
        try:
            body = role_client.update({"roleId": rid, "roleName": gen_name("edited"), "roleKey": key, "roleSort": 2, "status": "0", "menuIds": []}).json()
            assert_api_ok(body, "编辑角色")
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_API_006 禁用角色成功")
    def test_disable_role(self, role_client):
        rid, name, key = _create_role(role_client)
        try:
            body = role_client.update({"roleId": rid, "roleName": name, "roleKey": key, "roleSort": 1, "status": "1", "menuIds": []}).json()
            assert_api_ok(body, "禁用角色")
            role_body = role_client.get(rid).json()
            assert_schema(role_body, DETAIL_SCHEMA)
            assert role_body["data"]["status"] == "1"
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_API_007 启用角色成功")
    def test_enable_role(self, role_client):
        rid, name, key = _create_role(role_client)
        try:
            role_client.update({"roleId": rid, "roleName": name, "roleKey": key, "roleSort": 1, "status": "1", "menuIds": []})
            body = role_client.update({"roleId": rid, "roleName": name, "roleKey": key, "roleSort": 1, "status": "0", "menuIds": []}).json()
            assert_api_ok(body, "启用角色")
            assert role_client.get(rid).json()["data"]["status"] == "0"
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_API_008 给角色分配菜单权限成功")
    def test_assign_menu(self, role_client, permission_client):
        rid, name, key = _create_role(role_client, menu_ids=[1, 2, 3])
        try:
            ids = permission_client.get_role_menu_ids(rid)
            assert set([1, 2, 3]).issubset(set(ids)), f"菜单未全部分配 实际={ids}"
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_API_009 查询角色菜单权限成功")
    def test_list_role_menus(self, role_client, permission_client):
        rid, name, key = _create_role(role_client, menu_ids=[1, 2])
        try:
            ids = permission_client.get_role_menu_ids(rid)
            assert set([1, 2]).issubset(set(ids)), f"菜单未查到 实际={ids}"
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_API_010 删除测试角色成功")
    def test_delete_role(self, role_client):
        rid, name, key = _create_role(role_client)
        body = role_client.delete(rid).json()
        assert_api_ok(body, "删除角色")

    @allure.title("ROLE_API_011 数据库校验角色信息正确")
    @pytest.mark.db
    def test_db_check_role(self, role_client):
        name = gen_name("auto_role")
        key = gen_name("auto_key")
        role_client.create({"roleName": name, "roleKey": key, "roleSort": 1, "status": "0", "menuIds": []})
        rows = role_client.page({"roleName": name}).json()["rows"]
        rid = rows[0]["roleId"]
        try:
            row = db_utils.query_one("SELECT role_name, role_key, del_flag FROM sys_role WHERE role_id=%s", (rid,))
            assert row and row["role_name"] == name and row["role_key"] == key and row["del_flag"] == "0"
            attach_text("角色数据库记录", str(row))
        finally:
            role_client.delete(rid)

    @allure.title("ROLE_API_012 数据库校验角色菜单关系正确")
    @pytest.mark.db
    def test_db_check_role_menu(self, role_client, permission_client):
        rid, name, key = _create_role(role_client, menu_ids=[1, 2, 3])
        try:
            rows = db_utils.query_all("SELECT menu_id FROM sys_role_menu WHERE role_id=%s", (rid,))
            db_ids = {r["menu_id"] for r in rows}
            assert set([1, 2, 3]).issubset(db_ids), f"中间表菜单关系不完整 db={db_ids}"
            attach_text("角色菜单关系数据库记录", str(rows))
        finally:
            role_client.delete(rid)
