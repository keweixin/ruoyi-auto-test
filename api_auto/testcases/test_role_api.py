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

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail, assert_field, assert_page_result, assert_response_ok, assert_response_fail
from common.allure_utils import attach_json, attach_text
from common.environment_utils import get_assignable_menu_ids
from common.random_utils import gen_name
from common.data_provider import build_case_payload, load_create_cases, build_parametrize
from data.builders import valid_role_data


_ROLE_CASES, _ROLE_IDS = build_parametrize(load_create_cases("role"))


@allure.feature("角色管理接口")
@pytest.mark.api
class TestRoleApi:

    def _create_role(self, role_client):
        """创建测试角色并返回角色 ID。"""
        body = assert_response_ok(role_client.create(valid_role_data()), "创建角色")
        return body["data"]

    @allure.story("新增")
    @pytest.mark.parametrize("case", _ROLE_CASES, ids=_ROLE_IDS)
    def test_create_role_ddt(self, role_client, case):
        """ROLE_API_001~003 表驱动：合法创建 + 名称为空 + 重复角色。

        数据来源 data/role_data.yaml 的 create_cases。
        """
        allure.dynamic.title(f"{case['case_id']} {case['desc']}")
        payload = build_case_payload("role", case)
        if case["setup"] == "duplicate":
            first = assert_response_ok(role_client.create(payload), "前置：第一次创建")
            try:
                body = role_client.create(payload).json()
            finally:
                role_client.delete(first["data"])
        else:
            body = role_client.create(payload).json()

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
            rows = assert_page_result(body, min_total=1)["list"]
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
        role_id = self._create_role(role_client)
        try:
            role = role_client.get(role_id).json()["data"]
            role["status"] = 1
            assert_api_ok(role_client.update(role).json(), "禁用角色")
        finally:
            role_client.delete(role_id)

    @allure.story("状态")
    @allure.title("ROLE_API_007 启用角色成功")
    def test_enable_role(self, role_client):
        role_id = self._create_role(role_client)
        try:
            role = role_client.get(role_id).json()["data"]
            role["status"] = 1
            role_client.update(role).json()
            role["status"] = 0
            assert_api_ok(role_client.update(role).json(), "启用角色")
        finally:
            role_client.delete(role_id)

    @allure.story("权限分配")
    @allure.title("ROLE_API_008 给角色分配菜单权限成功")
    def test_assign_menu(self, role_client, permission_client):
        rid = self._create_role(role_client)
        try:
            body = assert_response_ok(permission_client.assign_role_menu(rid, get_assignable_menu_ids()), "分配菜单权限")
        finally:
            role_client.delete(rid)

    @allure.story("权限分配")
    @allure.title("ROLE_API_009 查询角色菜单权限成功")
    def test_list_role_menus(self, role_client, permission_client):
        rid = self._create_role(role_client)
        try:
            menu_ids = get_assignable_menu_ids(2)
            permission_client.assign_role_menu(rid, menu_ids)
            body = assert_response_ok(permission_client.list_role_menus(rid))
            result = set(body["data"])
            assert set(menu_ids).issubset(result), f"菜单未全部分配 实际={result}"
        finally:
            role_client.delete(rid)

    @allure.story("权限分配")
    @allure.title("ROLE_API_013 分配角色数据范围并校验数据库")
    @pytest.mark.db
    def test_assign_role_data_scope(self, role_client, permission_client):
        rid = self._create_role(role_client)
        try:
            body = assert_response_ok(permission_client.assign_role_data_scope(rid, 1), "分配全部数据权限")
            role = role_client.get(rid).json()
            attach_json("角色数据权限响应", role)
            assert_field(role["data"]["dataScope"], 1, "dataScope")
            db_utils.assert_db_field(
                "SELECT data_scope FROM system_role WHERE id=%s", (rid,), "data_scope", 1
            )
        finally:
            role_client.delete(rid)

    @allure.story("删除")
    @allure.title("ROLE_API_010 删除测试角色成功")
    def test_delete_role(self, role_client):
        rid = self._create_role(role_client)
        body = assert_response_ok(role_client.delete(rid), "删除角色")

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
            db_utils.assert_db_record("system_role", rid,
                                      {"name": name, "code": code}, "角色数据库记录")
        finally:
            role_client.delete(rid)

    @allure.story("数据库校验")
    @allure.title("ROLE_API_012 数据库校验角色菜单关系正确")
    @pytest.mark.db
    def test_db_check_role_menu(self, role_client, permission_client, menu_client):
        rid = self._create_role(role_client)
        menu_body = assert_response_ok(menu_client.list_all_simple(), "查询可分配菜单")
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
