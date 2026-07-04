"""角色管理接口测试用例。

覆盖 ROLE_API_001 ~ 012：
- CRUD + 异常 + 重复 + 状态切换 + 分配菜单权限 + 查询角色菜单 + 数据库校验(角色/角色菜单关系)

ROLE_API_001~003 采用 YAML 表驱动（data/role_data.yaml 的 create_cases）。

学习重点：权限系统理解、角色和菜单关系、数据库中间表校验。

⚠ 已核对源码：RoleSaveReqVO 无 menuIds / dataScope
   - 分配菜单走 PermissionClient.assign_role_menu
   - 查角色菜单走 PermissionClient.list_role_menus
   - 中间表：system_role_menu
"""
import allure
import pytest

from common.config import cfg
from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA
from common.data_provider import load_create_cases, build_parametrize


_ROLE_CASES, _ROLE_IDS = build_parametrize(load_create_cases("role"))


@allure.feature("角色管理接口")
@pytest.mark.api
class TestRoleApi:

    def _create_role(self, role_client):
        """辅助：创建测试角色，返回 role_id。"""
        body = role_client.create({
            "name": gen_name("auto_role"),
            "code": gen_name("auto_role_code"),
            "sort": 1,
            "status": 0,
            "remark": "auto",
        }).json()
        assert_api_ok(body, "创建角色")
        return body["data"]

    @allure.story("新增")
    @pytest.mark.parametrize("case", _ROLE_CASES, ids=_ROLE_IDS)
    def test_create_role_ddt(self, role_client, case):
        """ROLE_API_001~003 表驱动：合法创建 + 名称为空 + 重复角色。

        数据来源 data/role_data.yaml 的 create_cases。
        """
        allure.dynamic.title(f"{case['case_id']} {case['desc']}")
        if case["setup"] == "duplicate":
            first = role_client.create(case["payload"]).json()
            assert_api_ok(first, "前置：第一次创建")
            try:
                body = role_client.create(case["payload"]).json()
            finally:
                role_client.delete(first["data"])
        else:
            body = role_client.create(case["payload"]).json()

        if case["expect_ok"]:
            assert_api_ok(body, case["desc"])
            rid = body["data"]
            assert rid, "创建成功但未返回 id"
            role_client.delete(rid)
        else:
            assert_api_fail(body, case["desc"])
            if case["expect_msg_contains"]:
                assert case["expect_msg_contains"] in body.get("msg", ""), \
                    f"msg 期望含 {case['expect_msg_contains']!r}，实际 {body.get('msg')!r}"

    @allure.story("查询")
    @allure.title("ROLE_API_004 查询角色列表成功")
    @pytest.mark.smoke
    def test_page_role(self, role_client):
        name = gen_name("auto_role")
        code = gen_name("auto_role_code")
        rid = role_client.create({"name": name, "code": code, "sort": 1, "status": 0}).json()["data"]
        try:
            body = role_client.page({"pageNo": 1, "pageSize": 10, "name": name}).json()
            assert_schema(body, PAGE_LIST_SCHEMA)
            assert_api_ok(body)
            rows = body["data"]["list"]
            assert any(r["id"] == rid and r["name"] == name for r in rows), "未查到本次创建的角色"
        finally:
            role_client.delete(rid)

    @allure.story("修改")
    @allure.title("ROLE_API_005 编辑角色成功")
    def test_update_role(self, role_client):
        rid = self._create_role(role_client)
        try:
            body = role_client.update({
                "id": rid, "name": gen_name("auto_role_edited"),
                "code": gen_name("auto_role_code_edited"),
                "sort": 2, "status": 0, "remark": "edited"
            }).json()
            assert_api_ok(body, "编辑角色")
        finally:
            role_client.delete(rid)

    @allure.story("状态")
    @allure.title("ROLE_API_006 禁用角色成功")
    def test_disable_role(self, role_client):
        rid = self._create_role(role_client)
        try:
            role = role_client.get(rid).json()["data"]
            role["status"] = 1
            body = role_client.update(role).json()
            assert_api_ok(body, "禁用角色")
        finally:
            role_client.delete(rid)

    @allure.story("状态")
    @allure.title("ROLE_API_007 启用角色成功")
    def test_enable_role(self, role_client):
        rid = self._create_role(role_client)
        try:
            role = role_client.get(rid).json()["data"]
            role["status"] = 0
            body = role_client.update(role).json()
            assert_api_ok(body, "启用角色")
        finally:
            role_client.delete(rid)

    @allure.story("权限分配")
    @allure.title("ROLE_API_008 给角色分配菜单权限成功")
    def test_assign_menu(self, role_client, permission_client):
        rid = self._create_role(role_client)
        try:
            body = permission_client.assign_role_menu(rid, [1, 2, 3]).json()
            assert_api_ok(body, "分配菜单权限")
        finally:
            role_client.delete(rid)

    @allure.story("权限分配")
    @allure.title("ROLE_API_009 查询角色菜单权限成功")
    def test_list_role_menus(self, role_client, permission_client):
        rid = self._create_role(role_client)
        try:
            menu_ids = [1, 2]
            permission_client.assign_role_menu(rid, menu_ids)
            body = permission_client.list_role_menus(rid).json()
            assert_api_ok(body)
            result = set(body["data"])
            assert set(menu_ids).issubset(result), f"菜单未全部分配 实际={result}"
        finally:
            role_client.delete(rid)

    @allure.story("删除")
    @allure.title("ROLE_API_010 删除测试角色成功")
    def test_delete_role(self, role_client):
        rid = self._create_role(role_client)
        body = role_client.delete(rid).json()
        assert_api_ok(body, "删除角色")

    @allure.story("数据库校验")
    @allure.title("ROLE_API_011 数据库校验角色信息正确")
    @pytest.mark.db
    def test_db_check_role(self, role_client):
        name = gen_name("auto_role")
        code = gen_name("auto_role_code")
        rid = role_client.create(
            {"name": name, "code": code, "sort": 1, "status": 0, "remark": "dbcheck"}
        ).json()["data"]
        try:
            row = db_utils.query_one(
                "SELECT name, code, status, deleted + 0 AS deleted FROM system_role WHERE id=%s",
                (rid,)
            )
            assert row and row["name"] == name and row["code"] == code and row["deleted"] == 0
            attach_text("角色数据库记录", str(row))
        finally:
            role_client.delete(rid)

    @allure.story("数据库校验")
    @allure.title("ROLE_API_012 数据库校验角色菜单关系正确")
    @pytest.mark.db
    def test_db_check_role_menu(self, role_client, permission_client, menu_client):
        rid = self._create_role(role_client)
        menu_body = menu_client.list_all_simple().json()
        assert_api_ok(menu_body, "查询可分配菜单")
        assigned = [item["id"] for item in menu_body["data"][:3]]
        assert assigned, "没有可分配菜单"
        try:
            permission_client.assign_role_menu(rid, assigned)
            rows = db_utils.query_all(
                "SELECT menu_id FROM system_role_menu WHERE role_id=%s AND deleted=0",
                (rid,)
            )
            db_menu_ids = {r["menu_id"] for r in rows}
            assert set(assigned).issubset(db_menu_ids), \
                f"中间表菜单关系不完整 db={db_menu_ids}"
            attach_text("角色菜单关系数据库记录", str(rows))
        finally:
            role_client.delete(rid)
