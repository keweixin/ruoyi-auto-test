"""纯接口联动测试：字典（RuoYi-Vue-Pro / yudao）。

覆盖 DICT_FLOW_001 ~ 004：
- 接口创建 → 接口查询 → DB 校验 → 接口清理
- 接口编辑 → 接口查询确认 → DB 校验
- 接口删除 → 接口查询确认 → DB 校验
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_not_found, assert_response_ok, assert_response_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name


@allure.feature("纯接口联动-字典")
@pytest.mark.flow
class TestDictFlow:

    @allure.title("DICT_FLOW_001 接口创建字典类型 → 接口查询 → DB 校验 → 清理")
    def test_api_create_api_db_verify(self, dict_client):
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        dict_id = dict_client.create_type({"name": name, "type": type_, "status": 0, "remark": "flow"}).json()["data"]
        try:
            body = assert_response_ok(dict_client.page_type({"pageNo": 1, "pageSize": 10, "type": type_}))
            rows = body["data"]["list"]
            assert any(r["name"] == name and r["id"] == dict_id for r in rows), "接口未查到造的字典"
            row = db_utils.query_one(
                "SELECT name, type, status, deleted + 0 AS deleted FROM system_dict_type WHERE id=%s",
                (dict_id,),
            )
            assert row and row["name"] == name and row["deleted"] == 0, "DB 未落库"
            attach_text("字典 DB 记录", str(row))
        finally:
            assert_api_ok(dict_client.delete_type(dict_id).json())

    @allure.title("DICT_FLOW_002 接口创建字典类型 → 接口分页查询 → DB 校验 → 清理")
    def test_api_create_page_db_verify(self, dict_client):
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        dict_id = dict_client.create_type({"name": name, "type": type_, "status": 0}).json()["data"]
        try:
            body = assert_response_ok(dict_client.page_type({"pageNo": 1, "pageSize": 10, "name": name}))
            assert body["data"]["total"] >= 1, "分页接口未查到造的字典"
            row = db_utils.query_one("SELECT name, type FROM system_dict_type WHERE id=%s", (dict_id,))
            assert row and row["name"] == name, "DB 未落库"
            attach_text("字典 DB 记录", str(row))
        finally:
            assert_api_ok(dict_client.delete_type(dict_id).json())

    @allure.title("DICT_FLOW_003 接口编辑字典类型 → 接口查询确认 → DB 校验 → 清理")
    def test_api_edit_api_db_verify(self, dict_client):
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        dict_id = dict_client.create_type({"name": name, "type": type_, "status": 0}).json()["data"]
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(dict_client.update_type({"id": dict_id, "name": new_name, "type": type_, "status": 0}).json())
            body = assert_response_ok(dict_client.get_type(dict_id))
            assert body["data"]["name"] == new_name, "接口查到的名称未更新"
            row = db_utils.query_one("SELECT name FROM system_dict_type WHERE id=%s", (dict_id,))
            assert row and row["name"] == new_name, "DB 名称未更新"
            attach_text("编辑后字典 DB 记录", str(row))
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_FLOW_004 接口删除字典类型 → 接口查询确认 → DB 校验")
    def test_api_delete_api_db_verify(self, dict_client):
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        dict_id = dict_client.create_type({"name": name, "type": type_, "status": 0}).json()["data"]
        assert_api_ok(dict_client.delete_type(dict_id).json())
        body = dict_client.get_type(dict_id).json()
        assert_not_found(body)
        row = db_utils.query_one("SELECT deleted + 0 AS deleted FROM system_dict_type WHERE id=%s", (dict_id,))
        assert row is None or row["deleted"] == 1, f"数据库未标记逻辑删除: {row}"
        attach_text("删除后字典 DB 记录", str(row))
