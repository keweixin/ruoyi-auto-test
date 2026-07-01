"""岗位管理接口测试用例（RuoYi v3.9.2 原版）。

原版字段：postCode/postName/postSort/status；表 sys_post(主键post_id, del_flag)。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA, DETAIL_SCHEMA


def _create_post(post_client):
    name = gen_name("auto_post")
    code = gen_name("auto_code")
    body = post_client.create({"postCode": code, "postName": name, "postSort": 1, "status": "0", "remark": "auto"}).json()
    assert_api_ok(body, "新增岗位")
    rows = post_client.page({"postName": name}).json()["rows"]
    return rows[0]["postId"], name, code


@allure.feature("岗位管理接口")
@pytest.mark.api
class TestPostApi:

    @allure.title("POST_API_001 新增岗位成功")
    def test_create_post(self, post_client):
        post_id, name, code = _create_post(post_client)
        assert post_id
        post_client.delete(post_id)

    @allure.title("POST_API_002 新增岗位名称为空失败")
    def test_create_empty_name(self, post_client):
        body = post_client.create({"postCode": gen_name("c"), "postName": "", "postSort": 1, "status": "0"}).json()
        assert_api_fail(body, "名称为空")

    @allure.title("POST_API_003 新增岗位编码重复失败")
    def test_create_duplicate_code(self, post_client):
        post_id, name, code = _create_post(post_client)
        try:
            dup = post_client.create({"postCode": code, "postName": gen_name("p2"), "postSort": 1, "status": "0"}).json()
            assert_api_fail(dup, "编码重复")
        finally:
            post_client.delete(post_id)

    @allure.title("POST_API_004 查询岗位列表成功")
    @pytest.mark.smoke
    def test_page_post(self, post_client):
        post_id, name, code = _create_post(post_client)
        try:
            body = post_client.page({"postName": name}).json()
            assert_schema(body, PAGE_LIST_SCHEMA)
            assert_api_ok(body)
            rows = body["rows"]
            assert any(r["postId"] == post_id and r["postName"] == name for r in rows), "未查到本次岗位"
        finally:
            post_client.delete(post_id)

    @allure.title("POST_API_005 编辑岗位成功")
    def test_update_post(self, post_client):
        post_id, name, code = _create_post(post_client)
        try:
            body = post_client.update({"postId": post_id, "postCode": code, "postName": gen_name("edited"), "postSort": 2, "status": "0"}).json()
            assert_api_ok(body, "编辑岗位")
        finally:
            post_client.delete(post_id)

    @allure.title("POST_API_006 禁用岗位成功")
    def test_disable_post(self, post_client):
        post_id, name, code = _create_post(post_client)
        try:
            body = post_client.update({"postId": post_id, "postCode": code, "postName": name, "postSort": 1, "status": "1"}).json()
            assert_api_ok(body, "禁用岗位")
            post_body = post_client.get(post_id).json()
            assert_schema(post_body, DETAIL_SCHEMA)
            assert post_body["data"]["status"] == "1"
        finally:
            post_client.delete(post_id)

    @allure.title("POST_API_007 启用岗位成功")
    def test_enable_post(self, post_client):
        post_id, name, code = _create_post(post_client)
        try:
            post_client.update({"postId": post_id, "postCode": code, "postName": name, "postSort": 1, "status": "1"})
            body = post_client.update({"postId": post_id, "postCode": code, "postName": name, "postSort": 1, "status": "0"}).json()
            assert_api_ok(body, "启用岗位")
            assert post_client.get(post_id).json()["data"]["status"] == "0"
        finally:
            post_client.delete(post_id)

    @allure.title("POST_API_008 删除岗位成功")
    def test_delete_post(self, post_client):
        post_id, name, code = _create_post(post_client)
        body = post_client.delete(post_id).json()
        assert_api_ok(body, "删除岗位")

    @allure.title("POST_API_009 数据库校验岗位数据正确")
    @pytest.mark.db
    def test_db_check_post(self, post_client):
        post_id, name, code = _create_post(post_client)
        try:
            row = db_utils.query_one("SELECT post_name, post_code FROM sys_post WHERE post_id=%s", (post_id,))
            assert row and row["post_name"] == name and row["post_code"] == code
            attach_text("岗位数据库记录", str(row))
        finally:
            post_client.delete(post_id)
