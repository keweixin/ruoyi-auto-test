"""岗位管理接口测试用例。

覆盖 POST_API_001 ~ 009：
- CRUD + 异常 + 编码重复 + 状态切换 + 数据库校验

POST_API_001~003 采用 YAML 表驱动（data/post_data.yaml 的 create_cases）。

学习重点：普通表格 CRUD、编码唯一性校验、状态切换、表单必填校验。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA
from common.data_provider import build_case_payload, load_create_cases, build_parametrize
from common.test_data import with_created_entity


_POST_CASES, _POST_IDS = build_parametrize(load_create_cases("post"))


@allure.feature("岗位管理接口")
@pytest.mark.api
class TestPostApi:

    @allure.story("新增")
    @pytest.mark.parametrize("case", _POST_CASES, ids=_POST_IDS)
    def test_create_post_ddt(self, post_client, case):
        """POST_API_001~003 表驱动：合法创建 + 名称为空 + 编码重复。

        数据来源 data/post_data.yaml 的 create_cases。
        岗位的重复校验针对 code（非 name），故 duplicate_code 时第二次用同 code 但新 name。
        """
        allure.dynamic.title(f"{case['case_id']} {case['desc']}")
        payload = build_case_payload("post", case)
        if case["setup"] in ("duplicate", "duplicate_code"):
            first = post_client.create(payload).json()
            assert_api_ok(first, "前置：第一次创建")
            try:
                if case["setup"] == "duplicate_code":
                    # 同 code 但新 name，触发 code 唯一性校验
                    dup_payload = dict(payload)
                    dup_payload["name"] = gen_name("auto_post2")
                    body = post_client.create(dup_payload).json()
                else:
                    body = post_client.create(payload).json()
            finally:
                post_client.delete(first["data"])
        else:
            body = post_client.create(payload).json()

        if case["expect_ok"]:
            assert_api_ok(body, case["desc"])
            assert body["data"], "未返回 id"
            post_client.delete(body["data"])
        else:
            assert_api_fail(body, case["desc"])
            if case["expect_msg_contains"]:
                assert case["expect_msg_contains"] in body.get("msg", ""), \
                    f"msg 期望含 {case['expect_msg_contains']!r}，实际 {body.get('msg')!r}"

    @allure.story("查询")
    @allure.title("POST_API_004 查询岗位列表成功")
    @pytest.mark.smoke
    def test_page_post(self, post_client):
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        new_id = post_client.create({"name": name, "code": code, "sort": 1, "status": 0}).json()["data"]
        try:
            body = post_client.page({"pageNo": 1, "pageSize": 10, "name": name}).json()
            assert_schema(body, PAGE_LIST_SCHEMA)
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
        with with_created_entity(post_client, "post") as ent:
            post = post_client.get(ent.id).json()["data"]
            post["status"] = 1
            assert_api_ok(post_client.update(post).json(), "禁用岗位")

    @allure.story("状态")
    @allure.title("POST_API_007 启用岗位成功")
    def test_enable_post(self, post_client):
        with with_created_entity(post_client, "post") as ent:
            post = post_client.get(ent.id).json()["data"]
            post["status"] = 1
            post_client.update(post).json()
            post["status"] = 0
            assert_api_ok(post_client.update(post).json(), "启用岗位")

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
            db_utils.assert_db_record("system_post", new_id,
                                      {"name": name, "code": code}, "岗位数据库记录")
        finally:
            post_client.delete(new_id)
