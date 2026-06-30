"""岗位管理接口测试用例。

覆盖 POST_API_001 ~ 009：
- CRUD + 异常 + 编码重复 + 状态切换 + 数据库校验

学习重点：普通表格 CRUD、编码唯一性校验、状态切换、表单必填校验。
"""
import allure
import pytest

from common.config import cfg
from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name


@allure.feature("岗位管理接口")
class TestPostApi:

    @allure.story("新增")
    @allure.title("POST_API_001 新增岗位成功")
    def test_create_post(self, post_client):
        data = {"name": gen_name("auto_post"), "code": gen_name("auto_code"),
                "sort": 1, "status": 0, "remark": "auto"}
        body = post_client.create(data).json()
        assert_api_ok(body, "新增岗位")
        assert body["data"]
        post_client.delete(body["data"])

    @allure.story("异常")
    @allure.title("POST_API_002 新增岗位名称为空失败")
    def test_create_empty_name(self, post_client):
        body = post_client.create(
            {"name": "", "code": gen_name("c"), "sort": 1, "status": 0}
        ).json()
        assert_api_fail(body, "名称为空")

    @allure.story("异常")
    @allure.title("POST_API_003 新增岗位编码重复失败")
    def test_create_duplicate_code(self, post_client):
        code = gen_name("auto_code")
        data = {"name": gen_name("auto_post"), "code": code, "sort": 1, "status": 0}
        first = post_client.create(data).json()
        assert_api_ok(first, "第一次新增")
        try:
            dup = post_client.create(
                {"name": gen_name("auto_post2"), "code": code, "sort": 1, "status": 0}
            ).json()
            assert_api_fail(dup, "编码重复")
        finally:
            post_client.delete(first["data"])

    @allure.story("查询")
    @allure.title("POST_API_004 查询岗位列表成功")
    def test_page_post(self, post_client):
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        new_id = post_client.create({"name": name, "code": code, "sort": 1, "status": 0}).json()["data"]
        try:
            body = post_client.page({"pageNo": 1, "pageSize": 10, "name": name}).json()
            assert_api_ok(body)
            rows = body["data"]["list"]
            assert any(r["id"] == new_id and r["name"] == name for r in rows), "未查到本次创建的岗位"
        finally:
            post_client.delete(new_id)

    @allure.story("修改")
    @allure.title("POST_API_005 编辑岗位成功")
    def test_update_post(self, post_client):
        new_id = post_client.create(
            {"name": gen_name("auto_post"), "code": gen_name("auto_code"),
             "sort": 1, "status": 0, "remark": "auto"}
        ).json()["data"]
        try:
            body = post_client.update(
                {"id": new_id, "name": gen_name("auto_post_edited"),
                 "code": gen_name("auto_code_edited"), "sort": 2, "status": 0, "remark": "edited"}
            ).json()
            assert_api_ok(body, "编辑岗位")
        finally:
            post_client.delete(new_id)

    @allure.story("状态")
    @allure.title("POST_API_006 禁用岗位成功")
    def test_disable_post(self, post_client):
        new_id = post_client.create(
            {"name": gen_name("auto_post"), "code": gen_name("auto_code"),
             "sort": 1, "status": 0}
        ).json()["data"]
        try:
            body = post_client.update(
                {"id": new_id, "name": "x", "code": gen_name("c"), "sort": 1, "status": 1}
            ).json()
            assert_api_ok(body, "禁用岗位")
        finally:
            post_client.delete(new_id)

    @allure.story("状态")
    @allure.title("POST_API_007 启用岗位成功")
    def test_enable_post(self, post_client):
        new_id = post_client.create(
            {"name": gen_name("auto_post"), "code": gen_name("auto_code"),
             "sort": 1, "status": 1}
        ).json()["data"]
        try:
            body = post_client.update(
                {"id": new_id, "name": "x", "code": gen_name("c"), "sort": 1, "status": 0}
            ).json()
            assert_api_ok(body, "启用岗位")
        finally:
            post_client.delete(new_id)

    @allure.story("删除")
    @allure.title("POST_API_008 删除岗位成功")
    def test_delete_post(self, post_client):
        new_id = post_client.create(
            {"name": gen_name("auto_post"), "code": gen_name("auto_code"),
             "sort": 1, "status": 0}
        ).json()["data"]
        body = post_client.delete(new_id).json()
        assert_api_ok(body, "删除岗位")

    @allure.story("数据库校验")
    @allure.title("POST_API_009 数据库校验岗位数据正确")
    @pytest.mark.db
    def test_db_check_post(self, post_client):
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        new_id = post_client.create(
            {"name": name, "code": code, "sort": 1, "status": 0, "remark": "dbcheck"}
        ).json()["data"]
        try:
            row = db_utils.query_one(
                "SELECT name, code, status, deleted FROM system_post WHERE id=%s",
                (new_id,)
            )
            assert row and row["name"] == name and row["code"] == code and row["deleted"] == 0
            attach_text("岗位数据库记录", str(row))
        finally:
            post_client.delete(new_id)
