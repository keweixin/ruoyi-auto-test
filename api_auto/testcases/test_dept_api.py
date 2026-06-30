"""部门管理接口测试用例（RuoYi v3.9.2 原版）。

原版字段：parentId/deptName/orderNum/status；删除 sys_dept.del_flag。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name


def _create_dept(dept_client):
    name = gen_name("auto_dept")
    body = dept_client.create({"parentId": 100, "deptName": name, "orderNum": 1, "status": "0"}).json()
    assert_api_ok(body, "新增部门")
    rows = dept_client.list({"deptName": name}).json()["data"]
    return rows[0]["deptId"], name


@allure.feature("部门管理接口")
class TestDeptApi:

    @allure.title("DEPT_API_001 新增部门成功")
    def test_create_dept(self, dept_client):
        dept_id, name = _create_dept(dept_client)
        assert dept_id
        dept_client.delete(dept_id)

    @allure.title("DEPT_API_002 新增部门名称为空失败")
    def test_create_empty_name(self, dept_client):
        body = dept_client.create({"parentId": 100, "deptName": "", "orderNum": 1, "status": "0"}).json()
        assert_api_fail(body, "名称为空")

    @allure.title("DEPT_API_003 新增重复部门失败")
    def test_create_duplicate(self, dept_client):
        dept_id, name = _create_dept(dept_client)
        try:
            dup = dept_client.create({"parentId": 100, "deptName": name, "orderNum": 1, "status": "0"}).json()
            assert_api_fail(dup, "重复新增")
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_API_004 查询部门列表成功")
    def test_list_dept(self, dept_client):
        body = dept_client.list().json()
        assert_api_ok(body)
        assert isinstance(body["data"], list) and len(body["data"]) > 0

    @allure.title("DEPT_API_005 编辑部门名称成功")
    def test_update_dept(self, dept_client):
        dept_id, name = _create_dept(dept_client)
        try:
            new_name = gen_name("auto_edited")
            body = dept_client.update({"deptId": dept_id, "parentId": 100, "deptName": new_name, "orderNum": 1, "status": "0"}).json()
            assert_api_ok(body, "修改部门")
            assert dept_client.get(dept_id).json()["data"]["deptName"] == new_name
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_API_006 禁用部门成功")
    def test_disable_dept(self, dept_client):
        dept_id, name = _create_dept(dept_client)
        try:
            body = dept_client.update({"deptId": dept_id, "parentId": 100, "deptName": name, "orderNum": 1, "status": "1"}).json()
            assert_api_ok(body, "禁用部门")
            assert dept_client.get(dept_id).json()["data"]["status"] == "1"
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_API_007 启用部门成功")
    def test_enable_dept(self, dept_client):
        dept_id, name = _create_dept(dept_client)
        try:
            dept_client.update({"deptId": dept_id, "parentId": 100, "deptName": name, "orderNum": 1, "status": "1"})
            body = dept_client.update({"deptId": dept_id, "parentId": 100, "deptName": name, "orderNum": 1, "status": "0"}).json()
            assert_api_ok(body, "启用部门")
            assert dept_client.get(dept_id).json()["data"]["status"] == "0"
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_API_008 删除部门成功")
    def test_delete_dept(self, dept_client):
        dept_id, name = _create_dept(dept_client)
        body = dept_client.delete(dept_id).json()
        assert_api_ok(body, "删除部门")

    @allure.title("DEPT_API_009 删除后查询不到数据")
    def test_delete_then_not_found(self, dept_client):
        dept_id, name = _create_dept(dept_client)
        dept_client.delete(dept_id)
        rows = dept_client.list({"deptName": name}).json()["data"]
        assert not any(r["deptId"] == dept_id for r in rows), "删除后仍能查到"

    @allure.title("DEPT_API_010 数据库校验部门数据正确")
    @pytest.mark.db
    def test_db_check_dept(self, dept_client):
        dept_id, name = _create_dept(dept_client)
        try:
            row = db_utils.query_one("SELECT dept_name, del_flag FROM sys_dept WHERE dept_id=%s", (dept_id,))
            assert row and row["dept_name"] == name and row["del_flag"] == "0"
            attach_text("部门数据库记录", str(row))
        finally:
            dept_client.delete(dept_id)
