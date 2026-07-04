"""纯接口联动测试：角色权限（RuoYi-Vue-Pro / yudao）。

覆盖 ROLE_FLOW_001 ~ 004：
- 接口创建角色 → 接口查询 → DB 校验 → 清理
- 接口创建角色并分配菜单 → 验证菜单关系 → DB 校验
- 接口修改角色菜单 → 验证菜单关系变更 → DB 校验
- 接口建角色+建用户+绑角色 → DB 验证关系
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_text
from common.random_utils import gen_name, gen_mobile, gen_username


@allure.feature("纯接口联动-角色权限")
@pytest.mark.flow
class TestRolePermissionFlow:

    def _create_role(self, role_client):
        name = gen_name("auto_flow")
        rid = role_client.create({
            "name": name,
            "code": gen_name("auto_key"),
            "sort": 1,
            "status": 0,
            "remark": "flow",
        }).json()["data"]
        return rid, name

    def _menu_ids(self, menu_client, size=3):
        body = menu_client.list_all_simple().json()
        assert_api_ok(body, "查询可分配菜单")
        ids = [item["id"] for item in body["data"][:size]]
        assert ids, "没有可分配菜单"
        return ids

    @allure.title("ROLE_FLOW_001 接口创建角色 → 接口查询 → DB 校验 → 清理")
    def test_api_create_role_db_verify(self, role_client):
        rid, name = self._create_role(role_client)
        try:
            body = role_client.page({"pageNo": 1, "pageSize": 10, "name": name}).json()
            assert_api_ok(body)
            rows = body["data"]["list"]
            assert any(r["id"] == rid and r["name"] == name for r in rows), "接口未查到造的角色"
            row = db_utils.query_one(
                "SELECT name, deleted + 0 AS deleted FROM system_role WHERE id=%s",
                (rid,),
            )
            assert row and row["name"] == name and row["deleted"] == 0
            attach_text("角色 DB 记录", str(row))
        finally:
            assert_api_ok(role_client.delete(rid).json())

    @allure.title("ROLE_FLOW_002 接口创建角色分配菜单 → 查关系 → DB 校验 → 清理")
    def test_api_create_role_with_menus(self, role_client, permission_client, menu_client):
        rid, _ = self._create_role(role_client)
        menu_ids = self._menu_ids(menu_client, 3)
        try:
            assert_api_ok(permission_client.assign_role_menu(rid, menu_ids).json())
            ids = permission_client.get_role_menu_ids(rid)
            assert set(menu_ids).issubset(set(ids)), f"菜单未分配 实际={ids}"
            db_rows = db_utils.query_all(
                "SELECT menu_id FROM system_role_menu WHERE role_id=%s AND deleted=0",
                (rid,),
            )
            assert set(menu_ids).issubset({r["menu_id"] for r in db_rows}), "中间表关系缺失"
            attach_text("角色菜单 DB 记录", str(db_rows))
        finally:
            permission_client.assign_role_menu(rid, [])
            assert_api_ok(role_client.delete(rid).json())

    @allure.title("ROLE_FLOW_003 接口修改角色菜单 → 查关系变更 → DB 校验 → 清理")
    def test_api_update_role_menus(self, role_client, permission_client, menu_client):
        rid, _ = self._create_role(role_client)
        first_ids = self._menu_ids(menu_client, 2)
        next_ids = self._menu_ids(menu_client, 4)
        try:
            assert_api_ok(permission_client.assign_role_menu(rid, first_ids).json())
            assert set(first_ids).issubset(set(permission_client.get_role_menu_ids(rid)))
            assert_api_ok(permission_client.assign_role_menu(rid, next_ids).json())
            ids_after = permission_client.get_role_menu_ids(rid)
            assert set(next_ids).issubset(set(ids_after)), f"修改后菜单未分配 实际={ids_after}"
            db_rows = db_utils.query_all(
                "SELECT menu_id FROM system_role_menu WHERE role_id=%s AND deleted=0",
                (rid,),
            )
            assert set(next_ids).issubset({r["menu_id"] for r in db_rows}), "修改后中间表关系缺失"
            attach_text("修改后角色菜单 DB 记录", str(db_rows))
        finally:
            permission_client.assign_role_menu(rid, [])
            assert_api_ok(role_client.delete(rid).json())

    @allure.title("ROLE_FLOW_004 接口建角色+用户+绑角色 → DB 验证关系")
    def test_api_role_user_menu_access(self, role_client, user_client, permission_client, menu_client):
        rid, _ = self._create_role(role_client)
        menu_ids = self._menu_ids(menu_client, 3)
        username = gen_username()
        uid = None
        try:
            assert_api_ok(permission_client.assign_role_menu(rid, menu_ids).json())
            assert set(menu_ids).issubset(set(permission_client.get_role_menu_ids(rid)))
            uid = user_client.create({
                "username": username,
                "nickname": "权限测试",
                "password": "Test123456",
                "mobile": gen_mobile(),
                "deptId": 100,
            }).json()["data"]
            assert_api_ok(permission_client.assign_user_role(uid, [rid]).json())
            ur_rows = db_utils.query_all(
                "SELECT role_id FROM system_user_role WHERE user_id=%s AND deleted=0",
                (uid,),
            )
            assert any(r["role_id"] == rid for r in ur_rows), "用户角色关系未建立"
            attach_text("用户角色关系 DB 记录", str(ur_rows))
        finally:
            if uid:
                user_client.delete(uid)
            role_client.delete(rid)
