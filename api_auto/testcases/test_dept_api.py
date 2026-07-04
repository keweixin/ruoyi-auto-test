"""部门管理接口测试用例。

覆盖 DEPT_API_001 ~ 010：
- CRUD + 异常 + 重复 + 状态切换 + 删除后查不到 + 数据库校验

DEPT_API_001~003 采用 YAML 表驱动（data/dept_data.yaml 的 create_cases）。

学习重点：树形结构、上级部门 parentId、状态切换、数据清理。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail, assert_not_found, assert_response_ok, assert_response_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name
from common.schema_utils import assert_schema, LIST_DATA_SCHEMA
from common.data_provider import build_case_payload, load_create_cases, build_parametrize
from common.test_data import with_created_entity


_DEPT_CASES, _DEPT_IDS = build_parametrize(load_create_cases("dept"))


@allure.feature("部门管理接口")
@pytest.mark.api
class TestDeptApi:

    @allure.story("新增")
    @pytest.mark.parametrize("case", _DEPT_CASES, ids=_DEPT_IDS)
    def test_create_dept_ddt(self, dept_client, case):
        """DEPT_API_001~003 表驱动：合法创建 + 名称为空 + 重复部门。

        数据来源 data/dept_data.yaml 的 create_cases。
        """
        allure.dynamic.title(f"{case['case_id']} {case['desc']}")
        payload = build_case_payload("dept", case)
        if case["setup"] == "duplicate":
            first = assert_response_ok(dept_client.create(payload), "前置：第一次创建")
            try:
                body = dept_client.create(payload).json()
            finally:
                dept_client.delete(first["data"])
        else:
            body = dept_client.create(payload).json()

        if case["expect_ok"]:
            assert_api_ok(body, case["desc"])
            assert body["data"], "未返回 id"
            dept_client.delete(body["data"])
        else:
            assert_api_fail(body, case["desc"])
            if case["expect_msg_contains"]:
                assert case["expect_msg_contains"] in body.get("msg", ""), \
                    f"msg 期望含 {case['expect_msg_contains']!r}，实际 {body.get('msg')!r}"

    @allure.story("查询")
    @allure.title("DEPT_API_004 查询部门列表成功")
    @pytest.mark.smoke
    def test_list_dept(self, dept_client):
        body = dept_client.list().json()
        assert_schema(body, LIST_DATA_SCHEMA)
        assert_api_ok(body)
        assert isinstance(body["data"], list)

    @allure.story("修改")
    @allure.title("DEPT_API_005 编辑部门名称成功")
    def test_update_dept(self, dept_client):
        name = gen_name("auto_dept")
        new_id = dept_client.create(
            {"name": name, "parentId": 0, "sort": 1, "status": 0}
        ).json()["data"]
        try:
            new_name = gen_name("auto_dept_edited")
            body = dept_client.update(
                {"id": new_id, "name": new_name, "parentId": 0, "sort": 1, "status": 0}
            ).json()
            assert_api_ok(body, "修改部门")
        finally:
            dept_client.delete(new_id)

    @allure.story("状态")
    @allure.title("DEPT_API_006 禁用部门成功")
    def test_disable_dept(self, dept_client):
        with with_created_entity(dept_client, "dept") as ent:
            dept = dept_client.get(ent.id).json()["data"]
            dept["status"] = 1
            assert_api_ok(dept_client.update(dept).json(), "禁用部门")

    @allure.story("状态")
    @allure.title("DEPT_API_007 启用部门成功")
    def test_enable_dept(self, dept_client):
        with with_created_entity(dept_client, "dept") as ent:
            # 先禁用，再启用
            dept = dept_client.get(ent.id).json()["data"]
            dept["status"] = 1
            dept_client.update(dept).json()
            dept["status"] = 0
            assert_api_ok(dept_client.update(dept).json(), "启用部门")

    @allure.story("删除")
    @allure.title("DEPT_API_008 删除部门成功")
    def test_delete_dept(self, dept_client):
        new_id = dept_client.create(
            {"name": gen_name("auto_dept"), "parentId": 0, "sort": 1, "status": 0}
        ).json()["data"]
        body = assert_response_ok(dept_client.delete(new_id), "删除部门")

    @allure.story("删除")
    @allure.title("DEPT_API_009 删除后查询不到数据")
    def test_delete_then_not_found(self, dept_client):
        new_id = dept_client.create(
            {"name": gen_name("auto_dept"), "parentId": 0, "sort": 1, "status": 0}
        ).json()["data"]
        dept_client.delete(new_id)
        body = dept_client.get(new_id).json()
        assert_not_found(body)

    @allure.story("数据库校验")
    @allure.title("DEPT_API_010 数据库校验部门数据正确")
    @pytest.mark.db
    def test_db_check_dept(self, dept_client):
        name = gen_name("auto_dept")
        new_id = dept_client.create(
            {"name": name, "parentId": 0, "sort": 1, "status": 0}
        ).json()["data"]
        try:
            db_utils.assert_db_record("system_dept", new_id, {"name": name}, "部门数据库记录")
        finally:
            dept_client.delete(new_id)
