"""纯接口联动测试：部门 & 岗位。

覆盖 4 个场景：接口造数 → 接口验证 → 数据库校验 → 接口清理。

价值：不依赖前端，用接口+数据库验证完整联动逻辑。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_text
from common.random_utils import gen_name


@allure.feature("纯接口联动-部门岗位")
class TestDeptPostApiDbFlow:

    @allure.title("FLOW_001 接口新增部门 → 接口查询 → 数据库校验 → 接口清理")
    def test_api_add_dept_db_verify(self, dept_client):
        """接口造部门 → 接口确认存在 → 数据库校验字段 → 接口清理。"""
        name = gen_name("auto_flow")
        assert_api_ok(dept_client.create({
            "parentId": 100, "deptName": name, "orderNum": 1, "status": "0"
        }).json())
        rows = dept_client.list({"deptName": name}).json()["data"]
        dept_id = rows[0]["deptId"]
        try:
            assert any(r["deptName"] == name for r in rows), "接口未查到造的部门"
            row = db_utils.query_one(
                "SELECT dept_name, status, del_flag FROM sys_dept WHERE dept_id=%s", (dept_id,)
            )
            assert row and row["dept_name"] == name and row["del_flag"] == "0", "DB 未落库"
            attach_text("部门 DB 记录", str(row))
        finally:
            assert_api_ok(dept_client.delete(dept_id).json())

    @allure.title("FLOW_002 接口新增岗位 → 接口查询 → 数据库校验 → 接口清理")
    def test_api_add_post_db_verify(self, post_client):
        """接口造岗位 → 接口确认 → 数据库校验 → 接口清理。"""
        name = gen_name("auto_flow")
        code = gen_name("auto_code")
        assert_api_ok(post_client.create({
            "postCode": code, "postName": name, "postSort": 1, "status": "0"
        }).json())
        rows = post_client.page({"pageNum": 1, "pageSize": 10, "postName": name}).json()["rows"]
        pid = rows[0]["postId"]
        try:
            assert any(r["postName"] == name for r in rows), "接口未查到造的岗位"
            row = db_utils.query_one(
                "SELECT post_name, post_code, status FROM sys_post WHERE post_id=%s", (pid,)
            )
            assert row and row["post_name"] == name, "DB 未落库"
            attach_text("岗位 DB 记录", str(row))
        finally:
            assert_api_ok(post_client.delete(pid).json())

    @allure.title("FLOW_003 接口编辑部门 → 接口查询确认修改 → 数据库校验")
    def test_api_edit_dept_db_verify(self, dept_client):
        """接口造数 → 接口编辑 → 接口确认 → 数据库校验 → 接口清理。"""
        name = gen_name("auto_flow")
        assert_api_ok(dept_client.create({
            "parentId": 100, "deptName": name, "orderNum": 1, "status": "0"
        }).json())
        rows = dept_client.list({"deptName": name}).json()["data"]
        dept_id = rows[0]["deptId"]
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(dept_client.update({
                "deptId": dept_id, "deptName": new_name, "parentId": 100, "orderNum": 1, "status": "0"
            }).json())
            body = dept_client.get(dept_id).json()
            assert_api_ok(body)
            assert body["data"]["deptName"] == new_name, "接口查到的名称未更新"
            row = db_utils.query_one("SELECT dept_name FROM sys_dept WHERE dept_id=%s", (dept_id,))
            assert row and row["dept_name"] == new_name, "DB 名称未更新"
            attach_text("编辑后部门 DB 记录", str(row))
        finally:
            dept_client.delete(dept_id)

    @allure.title("FLOW_004 接口删除部门 → 数据库校验逻辑删除")
    def test_api_delete_dept_db_verify(self, dept_client):
        """接口造数 → 接口删除 → 数据库校验逻辑删除 del_flag='2'。原版 get 不过滤逻辑删除，用 DB 验证。"""
        name = gen_name("auto_flow")
        assert_api_ok(dept_client.create({
            "parentId": 100, "deptName": name, "orderNum": 1, "status": "0"
        }).json())
        rows = dept_client.list({"deptName": name}).json()["data"]
        dept_id = rows[0]["deptId"]
        assert_api_ok(dept_client.delete(dept_id).json())
        # 数据库校验：逻辑删除 del_flag='2'
        row = db_utils.query_one("SELECT del_flag FROM sys_dept WHERE dept_id=%s", (dept_id,))
        assert row is None or row["del_flag"] == "2", f"数据库未标记逻辑删除: {row}"
        attach_text("删除后部门 DB 记录", str(row))
