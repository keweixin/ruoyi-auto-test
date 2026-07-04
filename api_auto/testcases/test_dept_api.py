"""部门管理接口测试用例。

覆盖 DEPT_API_001 ~ 010：
- CRUD + 异常 + 重复 + 状态切换 + 删除后查不到 + 数据库校验

学习重点：树形结构、上级部门 parentId、状态切换、数据清理。
"""
import allure
import pytest

from common.config import cfg
from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name
from common.schema_utils import assert_schema, LIST_DATA_SCHEMA


@allure.feature("部门管理接口")
@pytest.mark.api
class TestDeptApi:

    @allure.story("新增")
    @allure.title("DEPT_API_001 新增部门成功")
    def test_create_dept(self, dept_client):
        name = gen_name("auto_dept")
        data = {"name": name, "parentId": 0, "sort": 1, "status": 0,
                "phone": "13800000000", "email": "a@test.com"}
        body = dept_client.create(data).json()
        assert_api_ok(body, "新增部门")
        assert body["data"], "未返回 id"
        dept_client.delete(body["data"])

    @allure.story("异常")
    @allure.title("DEPT_API_002 新增部门名称为空失败")
    def test_create_empty_name(self, dept_client):
        body = dept_client.create(
            {"name": "", "parentId": 0, "sort": 1, "status": 0}
        ).json()
        assert_api_fail(body, "名称为空")

    @allure.story("异常")
    @allure.title("DEPT_API_003 新增重复部门失败")
    def test_create_duplicate(self, dept_client):
        name = gen_name("auto_dept")
        data = {"name": name, "parentId": 0, "sort": 1, "status": 0}
        first = dept_client.create(data).json()
        assert_api_ok(first, "第一次新增")
        try:
            dup = dept_client.create(data).json()
            assert_api_fail(dup, "重复新增")
        finally:
            dept_client.delete(first["data"])

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
        new_id = dept_client.create(
            {"name": gen_name("auto_dept"), "parentId": 0, "sort": 1, "status": 0}
        ).json()["data"]
        try:
            body = dept_client.update(
                {"id": new_id, "name": "x", "parentId": 0, "sort": 1, "status": 1}
            ).json()
            assert_api_ok(body, "禁用部门")
        finally:
            dept_client.delete(new_id)

    @allure.story("状态")
    @allure.title("DEPT_API_007 启用部门成功")
    def test_enable_dept(self, dept_client):
        new_id = dept_client.create(
            {"name": gen_name("auto_dept"), "parentId": 0, "sort": 1, "status": 1}
        ).json()["data"]
        try:
            body = dept_client.update(
                {"id": new_id, "name": "x", "parentId": 0, "sort": 1, "status": 0}
            ).json()
            assert_api_ok(body, "启用部门")
        finally:
            dept_client.delete(new_id)

    @allure.story("删除")
    @allure.title("DEPT_API_008 删除部门成功")
    def test_delete_dept(self, dept_client):
        new_id = dept_client.create(
            {"name": gen_name("auto_dept"), "parentId": 0, "sort": 1, "status": 0}
        ).json()["data"]
        body = dept_client.delete(new_id).json()
        assert_api_ok(body, "删除部门")

    @allure.story("删除")
    @allure.title("DEPT_API_009 删除后查询不到数据")
    def test_delete_then_not_found(self, dept_client):
        new_id = dept_client.create(
            {"name": gen_name("auto_dept"), "parentId": 0, "sort": 1, "status": 0}
        ).json()["data"]
        dept_client.delete(new_id)
        body = dept_client.get(new_id).json()
        assert body.get("code") != 0 or not body.get("data"), "删除后仍能查到"

    @allure.story("数据库校验")
    @allure.title("DEPT_API_010 数据库校验部门数据正确")
    @pytest.mark.db
    def test_db_check_dept(self, dept_client):
        name = gen_name("auto_dept")
        new_id = dept_client.create(
            {"name": name, "parentId": 0, "sort": 1, "status": 0}
        ).json()["data"]
        try:
            row = db_utils.query_one(
                "SELECT name, parent_id, status, deleted + 0 AS deleted FROM system_dept WHERE id=%s",
                (new_id,)
            )
            assert row and row["name"] == name and row["deleted"] == 0
            attach_text("部门数据库记录", str(row))
        finally:
            dept_client.delete(new_id)
