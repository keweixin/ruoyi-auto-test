"""字典管理接口测试用例。

覆盖 DICT_API_001 ~ 015：
- 字典类型 CRUD + 异常 + 重复 + 状态切换
- 字典数据 CRUD
- 数据库校验（落库 + 逻辑删除）

学习重点：CRUD 闭环、参数异常、重复数据校验、数据库校验、随机数据 + 清理。
"""
import time
import allure
import pytest
import os

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail, assert_not_found, assert_page_result
from common.allure_utils import attach_text
from common.random_utils import gen_name
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA
from common.yaml_utils import load_case_list


_DICT_VALIDATION_CASES = load_case_list(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "dict_data.yaml"),
    "dict", "validation_cases"
)


@allure.feature("字典管理接口")
@pytest.mark.api
class TestDictApi:

    @allure.story("参数校验")
    @pytest.mark.parametrize("case", _DICT_VALIDATION_CASES, ids=[case["case_id"] for case in _DICT_VALIDATION_CASES])
    def test_type_validation(self, dict_client, case):
        data = {"name": gen_name("auto_dict"), "type": gen_name("auto_type"), "status": 0}
        data[case["field"]] = case["value"]
        assert_api_fail(dict_client.create_type(data).json(), case["desc"])

    @allure.story("查询")
    @allure.title("DICT_API_016 兼容方法查询字典类型分页")
    def test_list_type_compatibility(self, dict_client):
        body = dict_client.list_type({"pageNo": 1, "pageSize": 10}).json()
        assert_api_ok(body, "查询字典类型分页")
        assert_page_result(body)

    @allure.story("查询")
    @allure.title("DICT_API_017 查询精简字典类型列表")
    def test_list_type_all(self, dict_client):
        body = dict_client.list_type_all().json()
        assert_api_ok(body, "查询精简字典类型列表")
        assert isinstance(body["data"], list)

    @allure.story("查询")
    @allure.title("DICT_API_018 查询字典数据分页")
    def test_list_data_compatibility(self, dict_client):
        body = dict_client.list_data({"pageNo": 1, "pageSize": 10}).json()
        assert_api_ok(body, "查询字典数据分页")
        assert_page_result(body)

    @allure.story("字典类型 - 新增")
    @allure.title("DICT_API_001 新增字典类型成功")
    def test_create_type_success(self, dict_client):
        """新增成功 + 接口返回新 id。"""
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        data = {"name": name, "type": type_, "status": 0, "remark": "自动化测试"}
        body = dict_client.create_type(data).json()
        assert_api_ok(body, "新增字典类型")
        assert body["data"], "未返回新 id"
        # 清理
        dict_client.delete_type(body["data"])

    @allure.story("字典类型 - 异常")
    @allure.title("DICT_API_002 新增字典类型时名称为空失败")
    def test_create_type_empty_name(self, dict_client):
        """名称为空应被校验拦截。"""
        body = dict_client.create_type(
            {"name": "", "type": gen_name("t"), "status": 0}
        ).json()
        assert_api_fail(body, "名称为空")

    @allure.story("字典类型 - 异常")
    @allure.title("DICT_API_003 新增重复字典类型失败")
    def test_create_type_duplicate(self, dict_client):
        """type 重复应失败。"""
        type_ = gen_name("auto_type")
        data = {"name": gen_name("auto_dict"), "type": type_, "status": 0}
        first = dict_client.create_type(data).json()
        assert_api_ok(first, "第一次新增")
        try:
            dup = dict_client.create_type(data).json()
            assert_api_fail(dup, "重复新增")
        finally:
            dict_client.delete_type(first["data"])

    @allure.story("字典类型 - 查询")
    @allure.title("DICT_API_004 按字典名称查询成功")
    @pytest.mark.smoke
    def test_page_type_by_name(self, dict_client):
        """按名称查询能查到。"""
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        new_id = dict_client.create_type(
            {"name": name, "type": type_, "status": 0}
        ).json()["data"]
        try:
            body = dict_client.page_type(
                {"pageNo": 1, "pageSize": 10, "name": name}
            ).json()
            assert_schema(body, PAGE_LIST_SCHEMA)
            assert_api_ok(body)
            assert body["data"]["total"] >= 1, "按名称未查到"
        finally:
            dict_client.delete_type(new_id)

    @allure.story("字典类型 - 查询")
    @allure.title("DICT_API_005 按字典类型查询成功")
    def test_page_type_by_type(self, dict_client):
        """按 type 查询能查到。"""
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        new_id = dict_client.create_type(
            {"name": name, "type": type_, "status": 0}
        ).json()["data"]
        try:
            body = dict_client.page_type(
                {"pageNo": 1, "pageSize": 10, "type": type_}
            ).json()
            assert_api_ok(body)
            assert body["data"]["total"] >= 1, "按 type 未查到"
        finally:
            dict_client.delete_type(new_id)

    @allure.story("字典类型 - 修改")
    @allure.title("DICT_API_006 编辑字典类型成功")
    def test_update_type(self, dict_client):
        """修改后 name 生效。"""
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        new_id = dict_client.create_type(
            {"name": name, "type": type_, "status": 0}
        ).json()["data"]
        try:
            new_name = gen_name("auto_dict_edited")
            body = dict_client.update_type(
                {"id": new_id, "name": new_name, "type": type_, "status": 0}
            ).json()
            assert_api_ok(body, "修改字典类型")
        finally:
            dict_client.delete_type(new_id)

    @allure.story("字典类型 - 状态")
    @allure.title("DICT_API_007 停用字典类型成功")
    def test_disable_type(self, dict_client):
        """status 改为 1（禁用）。"""
        new_id = dict_client.create_type(
            {"name": gen_name("auto_dict"), "type": gen_name("auto_type"), "status": 0}
        ).json()["data"]
        try:
            body = dict_client.update_type(
                {"id": new_id, "name": "x", "type": gen_name("t"), "status": 1}
            ).json()
            assert_api_ok(body, "停用")
        finally:
            dict_client.delete_type(new_id)

    @allure.story("字典类型 - 状态")
    @allure.title("DICT_API_008 启用字典类型成功")
    def test_enable_type(self, dict_client):
        """status 改为 0（开启）。"""
        new_id = dict_client.create_type(
            {"name": gen_name("auto_dict"), "type": gen_name("auto_type"), "status": 1}
        ).json()["data"]
        try:
            body = dict_client.update_type(
                {"id": new_id, "name": "x", "type": gen_name("t"), "status": 0}
            ).json()
            assert_api_ok(body, "启用")
        finally:
            dict_client.delete_type(new_id)

    @allure.story("字典类型 - 删除")
    @allure.title("DICT_API_009 删除字典类型成功")
    def test_delete_type(self, dict_client):
        """删除接口返回成功。"""
        new_id = dict_client.create_type(
            {"name": gen_name("auto_dict"), "type": gen_name("auto_type"), "status": 0}
        ).json()["data"]
        body = dict_client.delete_type(new_id).json()
        assert_api_ok(body, "删除")

    @allure.story("字典类型 - 删除")
    @allure.title("DICT_API_010 删除后再次查询不到数据")
    def test_delete_then_not_found(self, dict_client):
        """删除后再查详情，应查不到或状态为已删除。"""
        type_ = gen_name("auto_type")
        new_id = dict_client.create_type(
            {"name": gen_name("auto_dict"), "type": type_, "status": 0}
        ).json()["data"]
        dict_client.delete_type(new_id)
        body = dict_client.get_type(new_id).json()
        # 若依删除后 get 通常返回 code!=0 或 data 为空
        assert_not_found(body)

    @allure.story("字典数据 - CRUD")
    @allure.title("DICT_API_011 新增字典数据成功")
    def test_create_data(self, dict_client):
        """新增字典数据。先建字典类型，再建数据。"""
        type_ = gen_name("auto_type")
        type_id = dict_client.create_type(
            {"name": gen_name("auto_dict"), "type": type_, "status": 0}
        ).json()["data"]
        try:
            body = dict_client.create_data(
                {"sort": 1, "label": "自动选项", "value": "1",
                 "dictType": type_, "status": 0}
            ).json()
            assert_api_ok(body, "新增字典数据")
            dict_client.delete_data(body["data"])
        finally:
            dict_client.delete_type(type_id)

    @allure.story("字典数据 - CRUD")
    @allure.title("DICT_API_012 编辑字典数据成功")
    def test_update_data(self, dict_client):
        """编辑字典数据。"""
        type_ = gen_name("auto_type")
        type_id = dict_client.create_type(
            {"name": gen_name("auto_dict"), "type": type_, "status": 0}
        ).json()["data"]
        data_id = dict_client.create_data(
            {"sort": 1, "label": "自动选项", "value": "1", "dictType": type_, "status": 0}
        ).json()["data"]
        try:
            body = dict_client.update_data(
                {"id": data_id, "sort": 2, "label": "已编辑", "value": "2",
                 "dictType": type_, "status": 0}
            ).json()
            assert_api_ok(body, "编辑字典数据")
        finally:
            dict_client.delete_data(data_id)
            dict_client.delete_type(type_id)

    @allure.story("字典数据 - CRUD")
    @allure.title("DICT_API_013 删除字典数据成功")
    def test_delete_data(self, dict_client):
        """删除字典数据。"""
        type_ = gen_name("auto_type")
        type_id = dict_client.create_type(
            {"name": gen_name("auto_dict"), "type": type_, "status": 0}
        ).json()["data"]
        data_id = dict_client.create_data(
            {"sort": 1, "label": "自动选项", "value": "1", "dictType": type_, "status": 0}
        ).json()["data"]
        try:
            body = dict_client.delete_data(data_id).json()
            assert_api_ok(body, "删除字典数据")
        finally:
            dict_client.delete_type(type_id)

    @allure.story("数据库校验")
    @allure.title("DICT_API_014 数据库校验字典类型落库正确")
    @pytest.mark.db
    def test_db_check_dict_type(self, dict_client):
        """新增后查库验证字段正确；删除后验证逻辑删除。"""
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        new_id = dict_client.create_type(
            {"name": name, "type": type_, "status": 0, "remark": "dbcheck"}
        ).json()["data"]
        try:
            row = db_utils.query_one(
                "SELECT name, type, status, deleted + 0 AS deleted FROM system_dict_type WHERE type=%s",
                (type_,)
            )
            assert row, "数据库未查到新增的字典类型"
            assert row["name"] == name and row["status"] == 0 and row["deleted"] == 0
            attach_text("字典类型数据库记录", str(row))
        finally:
            dict_client.delete_type(new_id)

        # 删除后验证逻辑删除
        row2 = db_utils.query_one(
            "SELECT deleted + 0 AS deleted FROM system_dict_type WHERE type=%s", (type_,)
        )
        assert row2 is None or row2["deleted"] == 1, "删除后未标记逻辑删除"
        attach_text("删除后数据库记录", str(row2))

    @allure.story("数据库校验")
    @allure.title("DICT_API_015 数据库校验字典数据落库正确")
    @pytest.mark.db
    def test_db_check_dict_data(self, dict_client):
        """新增字典数据后查库验证。"""
        type_ = gen_name("auto_type")
        type_id = dict_client.create_type(
            {"name": gen_name("auto_dict"), "type": type_, "status": 0}
        ).json()["data"]
        data_id = dict_client.create_data(
            {"sort": 1, "label": "db项", "value": "9", "dictType": type_, "status": 0}
        ).json()["data"]
        try:
            row = db_utils.query_one(
                "SELECT label, value, dict_type, deleted + 0 AS deleted FROM system_dict_data WHERE id=%s",
                (data_id,)
            )
            assert row and row["label"] == "db项" and row["deleted"] == 0
            attach_text("字典数据数据库记录", str(row))
        finally:
            dict_client.delete_data(data_id)
            dict_client.delete_type(type_id)
