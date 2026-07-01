"""字典管理接口测试用例（RuoYi v3.9.2 原版）。

原版字段：dictName/dictType/status；新增返回 {code:200} 无 data，需 list 查 id。
数据库表：sys_dict_type(主键dict_id) / sys_dict_data(主键dict_code)。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA, DETAIL_SCHEMA


def _create_type(dict_client):
    name = gen_name("auto_dict")
    type_ = gen_name("auto_type")
    body = dict_client.create_type({"dictName": name, "dictType": type_, "status": "0", "remark": "auto"}).json()
    assert_api_ok(body, "新增字典类型")
    # 查 id
    rows = dict_client.list_type({"dictType": type_, "pageNum": 1, "pageSize": 10}).json()["rows"]
    return rows[0]["dictId"], name, type_


@allure.feature("字典管理接口")
@pytest.mark.api
class TestDictApi:

    @allure.title("DICT_API_001 新增字典类型成功")
    def test_create_type_success(self, dict_client):
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        body = dict_client.create_type({"dictName": name, "dictType": type_, "status": "0", "remark": "auto"}).json()
        assert_api_ok(body, "新增字典类型")
        try:
            rows = dict_client.list_type({"dictType": type_}).json()["rows"]
            assert any(r["dictName"] == name for r in rows), "未查到新增字典"
        finally:
            dict_client.delete_type(rows[0]["dictId"]) if rows else None

    @allure.title("DICT_API_002 新增字典类型时名称为空失败")
    def test_create_type_empty_name(self, dict_client):
        body = dict_client.create_type({"dictName": "", "dictType": gen_name("t"), "status": "0"}).json()
        assert_api_fail(body, "名称为空")

    @allure.title("DICT_API_003 新增重复字典类型失败")
    def test_create_type_duplicate(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            dup = dict_client.create_type({"dictName": name, "dictType": type_, "status": "0"}).json()
            assert_api_fail(dup, "重复新增")
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_004 按字典名称查询成功")
    @pytest.mark.smoke
    def test_list_type_by_name(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            body = dict_client.list_type({"dictName": name}).json()
            assert_schema(body, PAGE_LIST_SCHEMA)
            rows = body["rows"]
            assert any(r["dictName"] == name for r in rows), "按名称未查到"
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_005 按字典类型查询成功")
    def test_list_type_by_type(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            rows = dict_client.list_type({"dictType": type_}).json()["rows"]
            assert any(r["dictType"] == type_ for r in rows), "按类型未查到"
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_006 编辑字典类型成功")
    def test_update_type(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            new_name = gen_name("auto_edited")
            body = dict_client.update_type({"dictId": dict_id, "dictName": new_name, "dictType": type_, "status": "0"}).json()
            assert_api_ok(body, "修改字典类型")
            after_body = dict_client.get_type(dict_id).json()
            assert_schema(after_body, DETAIL_SCHEMA)
            after = after_body["data"]
            assert after["dictName"] == new_name, "名称未更新"
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_007 停用字典类型成功")
    def test_disable_type(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            body = dict_client.update_type({"dictId": dict_id, "dictName": name, "dictType": type_, "status": "1"}).json()
            assert_api_ok(body, "停用")
            assert dict_client.get_type(dict_id).json()["data"]["status"] == "1"
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_008 启用字典类型成功")
    def test_enable_type(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            body = dict_client.update_type({"dictId": dict_id, "dictName": name, "dictType": type_, "status": "0"}).json()
            assert_api_ok(body, "启用")
            assert dict_client.get_type(dict_id).json()["data"]["status"] == "0"
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_009 删除字典类型成功")
    def test_delete_type(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        body = dict_client.delete_type(dict_id).json()
        assert_api_ok(body, "删除字典类型")

    @allure.title("DICT_API_010 删除后再次查询不到数据")
    def test_delete_then_not_found(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        dict_client.delete_type(dict_id)
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        assert not any(r["dictId"] == dict_id for r in rows), "删除后仍能查到"

    @allure.title("DICT_API_011 新增字典数据成功")
    def test_create_data(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            body = dict_client.create_data({"dictSort": 1, "dictLabel": "自动选项", "dictValue": "1", "dictType": type_, "status": "0"}).json()
            assert_api_ok(body, "新增字典数据")
            rows = dict_client.list_data({"dictType": type_}).json()["rows"]
            assert any(r["dictLabel"] == "自动选项" for r in rows)
            dict_client.delete_data(rows[0]["dictCode"])
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_012 编辑字典数据成功")
    def test_update_data(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            dict_client.create_data({"dictSort": 1, "dictLabel": "自动选项", "dictValue": "1", "dictType": type_, "status": "0"})
            rows = dict_client.list_data({"dictType": type_}).json()["rows"]
            code = rows[0]["dictCode"]
            body = dict_client.update_data({"dictCode": code, "dictSort": 2, "dictLabel": "已编辑", "dictValue": "2", "dictType": type_, "status": "0"}).json()
            assert_api_ok(body, "编辑字典数据")
            assert dict_client.get_data(code).json()["data"]["dictLabel"] == "已编辑"
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_013 删除字典数据成功")
    def test_delete_data(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        try:
            dict_client.create_data({"dictSort": 1, "dictLabel": "自动选项", "dictValue": "1", "dictType": type_, "status": "0"})
            rows = dict_client.list_data({"dictType": type_}).json()["rows"]
            code = rows[0]["dictCode"]
            body = dict_client.delete_data(code).json()
            assert_api_ok(body, "删除字典数据")
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_014 数据库校验字典类型落库正确")
    @pytest.mark.db
    def test_db_check_dict_type(self, dict_client):
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        dict_client.create_type({"dictName": name, "dictType": type_, "status": "0", "remark": "dbcheck"})
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        dict_id = rows[0]["dictId"]
        try:
            row = db_utils.query_one("SELECT dict_name, status FROM sys_dict_type WHERE dict_id=%s", (dict_id,))
            assert row and row["dict_name"] == name
            attach_text("字典类型数据库记录", str(row))
        finally:
            dict_client.delete_type(dict_id)

    @allure.title("DICT_API_015 数据库校验字典数据落库正确")
    @pytest.mark.db
    def test_db_check_dict_data(self, dict_client):
        dict_id, name, type_ = _create_type(dict_client)
        dict_client.create_data({"dictSort": 1, "dictLabel": "db项", "dictValue": "9", "dictType": type_, "status": "0"})
        rows = dict_client.list_data({"dictType": type_}).json()["rows"]
        code = rows[0]["dictCode"]
        try:
            row = db_utils.query_one("SELECT dict_label, dict_value FROM sys_dict_data WHERE dict_code=%s", (code,))
            assert row and row["dict_label"] == "db项"
            attach_text("字典数据数据库记录", str(row))
        finally:
            dict_client.delete_data(code)
            dict_client.delete_type(dict_id)
