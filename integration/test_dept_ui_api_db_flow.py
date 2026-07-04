"""纯接口联动测试：部门 & 岗位（RuoYi-Vue-Pro / yudao）。

覆盖 4 个场景：接口造数 → 接口验证 → 数据库校验 → 接口清理。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_text
from common.random_utils import gen_name


@allure.feature("纯接口联动-部门岗位")
@pytest.mark.flow
class TestDeptPostApiDbFlow:

    @allure.title("FLOW_001 接口新增部门 → 接口查询 → 数据库校验 → 接口清理")
    def test_api_add_dept_db_verify(self, dept_client):
        name = gen_name("auto_flow")
        dept_id = dept_client.create({"parentId": 0, "name": name, "sort": 1, "status": 0}).json()["data"]
        try:
            rows = dept_client.list({"name": name}).json()["data"]
            assert any(r["id"] == dept_id and r["name"] == name for r in rows), "接口未查到造的部门"
            row = db_utils.query_one(
                "SELECT name, status, deleted + 0 AS deleted FROM system_dept WHERE id=%s",
                (dept_id,),
            )
            assert row and row["name"] == name and row["deleted"] == 0, "DB 未落库"
            attach_text("部门 DB 记录", str(row))
        finally:
            assert_api_ok(dept_client.delete(dept_id).json())

    @allure.title("FLOW_002 接口新增岗位 → 接口查询 → 数据库校验 → 接口清理")
    def test_api_add_post_db_verify(self, post_client):
        name = gen_name("auto_flow")
        code = gen_name("auto_code")
        post_id = post_client.create({"code": code, "name": name, "sort": 1, "status": 0}).json()["data"]
        try:
            body = post_client.page({"pageNo": 1, "pageSize": 10, "name": name}).json()
            assert_api_ok(body)
            rows = body["data"]["list"]
            assert any(r["id"] == post_id and r["name"] == name for r in rows), "接口未查到造的岗位"
            row = db_utils.query_one(
                "SELECT name, code, status, deleted + 0 AS deleted FROM system_post WHERE id=%s",
                (post_id,),
            )
            assert row and row["name"] == name and row["deleted"] == 0, "DB 未落库"
            attach_text("岗位 DB 记录", str(row))
        finally:
            assert_api_ok(post_client.delete(post_id).json())

    @allure.title("FLOW_003 接口编辑部门 → 接口查询确认修改 → 数据库校验")
    def test_api_edit_dept_db_verify(self, dept_client):
        name = gen_name("auto_flow")
        dept_id = dept_client.create({"parentId": 0, "name": name, "sort": 1, "status": 0}).json()["data"]
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(dept_client.update({"id": dept_id, "name": new_name, "parentId": 0, "sort": 1, "status": 0}).json())
            body = dept_client.get(dept_id).json()
            assert_api_ok(body)
            assert body["data"]["name"] == new_name, "接口查到的名称未更新"
            row = db_utils.query_one("SELECT name FROM system_dept WHERE id=%s", (dept_id,))
            assert row and row["name"] == new_name, "DB 名称未更新"
            attach_text("编辑后部门 DB 记录", str(row))
        finally:
            dept_client.delete(dept_id)

    @allure.title("FLOW_004 接口删除部门 → 数据库校验逻辑删除")
    def test_api_delete_dept_db_verify(self, dept_client):
        name = gen_name("auto_flow")
        dept_id = dept_client.create({"parentId": 0, "name": name, "sort": 1, "status": 0}).json()["data"]
        assert_api_ok(dept_client.delete(dept_id).json())
        row = db_utils.query_one("SELECT deleted + 0 AS deleted FROM system_dept WHERE id=%s", (dept_id,))
        assert row is None or row["deleted"] == 1, f"数据库未标记逻辑删除: {row}"
        attach_text("删除后部门 DB 记录", str(row))
