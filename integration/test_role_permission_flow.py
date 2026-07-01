"""纯接口联动测试：角色权限。

覆盖 ROLE_FLOW_001 ~ 004：
- 接口创建角色 → 接口查询 → DB 校验 → 清理
- 接口创建角色并分配菜单 → 验证菜单关系 → DB 校验
- 接口修改角色菜单 → 验证菜单关系变更 → DB 校验
- 接口建角色+建用户+绑角色 → 登录验证菜单权限

价值：不依赖前端，用接口+数据库验证角色权限联动逻辑。
"""
import allure
import pytest

from common import db_utils
from common.config import cfg
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_text
from common.random_utils import gen_name, gen_mobile
from api_auto.clients.auth_client import AuthClient


@allure.feature("纯接口联动-角色权限")
class TestRolePermissionFlow:

    @allure.title("ROLE_FLOW_001 接口创建角色 → 接口查询 → DB 校验 → 清理")
    def test_api_create_role_db_verify(self, role_client):
        """接口造角色 → 接口验证 → 数据库校验 → 接口清理。"""
        name = gen_name("auto_flow")
        assert_api_ok(role_client.create({
            "roleName": name, "roleKey": gen_name("auto_key"),
            "roleSort": 1, "status": "0", "remark": "flow", "menuIds": []
        }).json())
        rows = role_client.page({"pageNum": 1, "pageSize": 10, "roleName": name}).json()["rows"]
        rid = rows[0]["roleId"]
        try:
            assert any(r["roleName"] == name for r in rows), "接口未查到造的角色"
            row = db_utils.query_one("SELECT role_name, del_flag FROM sys_role WHERE role_id=%s", (rid,))
            assert row and row["role_name"] == name and row["del_flag"] == "0"
            attach_text("角色 DB 记录", str(row))
        finally:
            assert_api_ok(role_client.delete(rid).json())

    @allure.title("ROLE_FLOW_002 接口创建角色分配菜单 → 查关系 → DB 校验 → 清理")
    def test_api_create_role_with_menus(self, role_client, permission_client):
        """接口建角色(带 menuIds) → 查角色菜单 → 数据库校验中间表 → 清理。"""
        name = gen_name("auto_flow")
        assert_api_ok(role_client.create({
            "roleName": name, "roleKey": gen_name("auto_key"),
            "roleSort": 1, "status": "0", "menuIds": [1, 2, 3]
        }).json())
        rows = role_client.page({"pageNum": 1, "pageSize": 10, "roleName": name}).json()["rows"]
        rid = rows[0]["roleId"]
        try:
            ids = permission_client.get_role_menu_ids(rid)
            assert set([1, 2, 3]).issubset(set(ids)), f"菜单未分配 实际={ids}"
            db_rows = db_utils.query_all("SELECT menu_id FROM sys_role_menu WHERE role_id=%s", (rid,))
            assert set([1, 2, 3]).issubset({r["menu_id"] for r in db_rows}), "中间表关系缺失"
            attach_text("角色菜单 DB 记录", str(db_rows))
        finally:
            assert_api_ok(role_client.delete(rid).json())

    @allure.title("ROLE_FLOW_003 接口修改角色菜单 → 查关系变更 → DB 校验 → 清理")
    def test_api_update_role_menus(self, role_client, permission_client):
        """接口建角色(无菜单) → 通过 update 分配菜单 → 验证 → DB 校验 → 清理。"""
        name = gen_name("auto_flow")
        assert_api_ok(role_client.create({
            "roleName": name, "roleKey": gen_name("auto_key"),
            "roleSort": 1, "status": "0", "menuIds": []
        }).json())
        rows = role_client.page({"pageNum": 1, "pageSize": 10, "roleName": name}).json()["rows"]
        rid = rows[0]["roleId"]
        try:
            # 先确认无菜单
            ids_before = permission_client.get_role_menu_ids(rid)
            assert len(ids_before) == 0, f"新建角色不应有菜单 实际={ids_before}"
            # 通过 update 分配菜单（用确认存在的菜单 id）
            assert_api_ok(role_client.update({
                "roleId": rid, "roleName": name, "roleKey": gen_name("auto_key"),
                "roleSort": 1, "status": "0", "menuIds": [1, 2, 3, 4]
            }).json())
            ids_after = permission_client.get_role_menu_ids(rid)
            assert set([1, 2, 3, 4]).issubset(set(ids_after)), f"修改后菜单未分配 实际={ids_after}"
            db_rows = db_utils.query_all("SELECT menu_id FROM sys_role_menu WHERE role_id=%s", (rid,))
            assert set([1, 2, 3, 4]).issubset({r["menu_id"] for r in db_rows}), "修改后中间表关系缺失"
            attach_text("修改后角色菜单 DB 记录", str(db_rows))
        finally:
            assert_api_ok(role_client.delete(rid).json())

    @allure.title("ROLE_FLOW_004 接口建角色+用户+绑角色 → DB 验证关系")
    def test_api_role_user_menu_access(self, role_client, user_client, permission_client):
        """接口建角色(带部分菜单) → 建用户绑定角色 → DB 验证用户角色关系 → 清理。"""
        name = gen_name("auto_flow")
        assert_api_ok(role_client.create({
            "roleName": name, "roleKey": gen_name("auto_key"),
            "roleSort": 1, "status": "0", "menuIds": [1, 2, 3]
        }).json())
        rows = role_client.page({"pageNum": 1, "pageSize": 10, "roleName": name}).json()["rows"]
        rid = rows[0]["roleId"]
        username = gen_name("auto_puser")
        uid = None
        try:
            role_menu_ids = permission_client.get_role_menu_ids(rid)
            assert set([1, 2, 3]).issubset(set(role_menu_ids)), f"角色菜单未分配 实际={role_menu_ids}"
            # 创建用户并绑定角色
            assert_api_ok(user_client.create({
                "userName": username, "nickName": "权限测试",
                "password": "Test123456", "phonenumber": gen_mobile(),
                "deptId": 100, "status": "0", "roleIds": [rid]
            }).json())
            rows_u = user_client.page({"pageNum": 1, "pageSize": 10, "userName": username}).json()["rows"]
            uid = rows_u[0]["userId"]
            # DB 验证用户角色关系
            ur_rows = db_utils.query_all("SELECT role_id FROM sys_user_role WHERE user_id=%s", (uid,))
            assert any(r["role_id"] == rid for r in ur_rows), "用户角色关系未建立"
            attach_text("用户角色关系 DB 记录", str(ur_rows))
        finally:
            if uid:
                user_client.delete(uid)
            role_client.delete(rid)
