"""纯接口联动测试：字典。

覆盖 DICT_FLOW_001 ~ 004：
- 接口创建 → 接口查询 → DB 校验 → 接口清理
- 接口编辑 → 接口查询确认 → DB 校验
- 接口删除 → 接口查询确认 → DB 校验

价值：不依赖前端，用接口+数据库验证字典联动逻辑。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_text
from common.random_utils import gen_name


@allure.feature("纯接口联动-字典")
class TestDictFlow:

    @allure.title("DICT_FLOW_001 接口创建字典类型 → 接口查询 → DB 校验 → 清理")
    def test_api_create_api_db_verify(self, dict_client):
        """接口造数 → 接口验证 → 数据库校验 → 接口清理。"""
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        assert_api_ok(dict_client.create_type({
            "dictName": name, "dictType": type_, "status": "0", "remark": "flow"
        }).json())
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        dict_id = rows[0]["dictId"]
        try:
            assert any(r["dictName"] == name for r in rows), "接口未查到造的字典"
            row = db_utils.query_one(
                "SELECT dict_name, status FROM sys_dict_type WHERE dict_id=%s", (dict_id,)
            )
            assert row and row["dict_name"] == name, "DB 未落库"
            attach_text("字典 DB 记录", str(row))
        finally:
            assert_api_ok(dict_client.delete_type(dict_id).json())

    @allure.title("DICT_FLOW_002 接口创建字典类型 → 接口分页查询 → DB 校验 → 清理")
    def test_api_create_page_db_verify(self, dict_client):
        """接口造数 → 分页查询验证 → 数据库校验 → 接口清理。"""
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        assert_api_ok(dict_client.create_type({
            "dictName": name, "dictType": type_, "status": "0"
        }).json())
        body = dict_client.list_type({"pageNum": 1, "pageSize": 10, "dictName": name}).json()
        assert_api_ok(body)
        assert body["total"] >= 1, "分页接口未查到造的字典"
        dict_id = body["rows"][0]["dictId"]
        try:
            row = db_utils.query_one(
                "SELECT dict_name, dict_type FROM sys_dict_type WHERE dict_id=%s", (dict_id,)
            )
            assert row and row["dict_name"] == name, "DB 未落库"
            attach_text("字典 DB 记录", str(row))
        finally:
            assert_api_ok(dict_client.delete_type(dict_id).json())

    @allure.title("DICT_FLOW_003 接口编辑字典类型 → 接口查询确认 → DB 校验 → 清理")
    def test_api_edit_api_db_verify(self, dict_client):
        """接口造数 → 接口编辑 → 接口确认 → 数据库校验 → 接口清理。"""
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        assert_api_ok(dict_client.create_type({
            "dictName": name, "dictType": type_, "status": "0"
        }).json())
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        dict_id = rows[0]["dictId"]
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(dict_client.update_type({
                "dictId": dict_id, "dictName": new_name, "dictType": type_, "status": "0"
            }).json())
            body = dict_client.get_type(dict_id).json()
            assert_api_ok(body)
            assert body["data"]["dictName"] == new_name, "接口查到的名称未更新"
            row = db_utils.query_one("SELECT dict_name FROM sys_dict_type WHERE dict_id=%s", (dict_id,))
            assert row and row["dict_name"] == new_name, "DB 名称未更新"
            attach_text("编辑后字典 DB 记录", str(row))
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_FLOW_004 接口删除字典类型 → 接口查询确认 → DB 校验")
    def test_api_delete_api_db_verify(self, dict_client):
        """接口造数 → 接口删除 → 接口确认已删 → 数据库校验。"""
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        assert_api_ok(dict_client.create_type({
            "dictName": name, "dictType": type_, "status": "0"
        }).json())
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        dict_id = rows[0]["dictId"]
        assert_api_ok(dict_client.delete_type(dict_id).json())
        # 接口确认：再查应查不到或返回空
        body = dict_client.get_type(dict_id).json()
        assert body.get("code") != 200 or not body.get("data"), "接口仍能查到已删字典"
        # 数据库校验：字典类型是物理删除
        row = db_utils.query_one("SELECT dict_id FROM sys_dict_type WHERE dict_id=%s", (dict_id,))
        assert row is None, "数据库未物理删除字典"
        attach_text("删除后字典 DB 记录", str(row))
