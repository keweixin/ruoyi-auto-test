"""字典管理 UI 测试用例（Vue3 / Element Plus）。

策略：复杂表单造数优先由 API 完成，UI 层验证页面打开、查询、展示、必填校验和删除确认。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok, assert_not_found, assert_response_ok, assert_response_fail
from common.random_utils import gen_name
from ui_auto.pages.dict_page import DictPage


@allure.feature("字典管理 UI")
@pytest.mark.ui
class TestDictUi:

    def _create_type(self, dict_client, status=0):
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        body = assert_response_ok(dict_client.create_type({"name": name, "type": type_, "status": status}), "API 创建字典类型")
        return body["data"], name, type_

    def _create_data(self, dict_client, type_, status=0):
        label = gen_name("auto_label")
        value = gen_name("auto_value")
        body = dict_client.create_data({
            "sort": 1,
            "label": label,
            "value": value,
            "dictType": type_,
            "status": status,
        }).json()
        assert_api_ok(body, "API 创建字典数据")
        return body["data"], label, value

    @allure.title("DICT_UI_001 进入字典管理页面成功")
    def test_open_dict_page(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        assert dp.is_table_visible(), "字典页表格未展示"

    @allure.title("DICT_UI_002 按字典名称查询成功")
    def test_search_by_name(self, page, dict_client):
        type_id, name, _ = self._create_type(dict_client)
        try:
            dp = DictPage(page)
            dp.open_type_page()
            dp.search_by_name(name)
            assert dp.row_exists(name), "按名称查询无结果"
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_003 按字典类型查询成功")
    def test_search_by_type(self, page, dict_client):
        type_id, _, type_ = self._create_type(dict_client)
        try:
            dp = DictPage(page)
            dp.open_type_page()
            dp.search_by_type(type_)
            assert dp.row_exists(type_), "按类型查询无结果"
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_004 点击重置后查询条件清空")
    def test_reset_search(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        dp.search_by_name("性别")
        dp.reset_search()
        assert dp.type_name_query_value() == ""

    @allure.title("DICT_UI_005 新增字典类型后页面可查询")
    def test_add_dict(self, page, dict_client):
        type_id, name, _ = self._create_type(dict_client)
        try:
            dp = DictPage(page)
            dp.open_type_page()
            dp.search_by_name(name)
            assert dp.row_exists(name), "新增后表格未查到"
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_006 新增字典类型必填项为空提示")
    def test_add_empty_name(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        assert dp.submit_empty_form() > 0, "空必填项提交后应显示校验错误"

    @allure.title("DICT_UI_007 编辑字典类型成功")
    def test_edit_dict(self, page, dict_client):
        type_id, name, type_ = self._create_type(dict_client)
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(dict_client.update_type({"id": type_id, "name": new_name, "type": type_, "status": 0}).json())
            dp = DictPage(page)
            dp.open_type_page()
            dp.search_by_name(new_name)
            assert dp.row_exists(new_name)
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_008 停用字典类型成功")
    def test_disable_dict(self, page, dict_client):
        type_id, name, type_ = self._create_type(dict_client)
        try:
            assert_api_ok(dict_client.update_type({"id": type_id, "name": name, "type": type_, "status": 1}).json())
            dp = DictPage(page)
            dp.open_type_page()
            dp.search_by_name(name)
            assert "关闭" in dp.table_row_by_keyword(name).inner_text()
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_009 启用字典类型成功")
    def test_enable_dict(self, page, dict_client):
        type_id, name, type_ = self._create_type(dict_client, status=1)
        try:
            assert_api_ok(dict_client.update_type({"id": type_id, "name": name, "type": type_, "status": 0}).json())
            dp = DictPage(page)
            dp.open_type_page()
            dp.search_by_name(name)
            assert "开启" in dp.table_row_by_keyword(name).inner_text()
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_010 删除字典类型成功")
    def test_delete_dict(self, page, dict_client):
        type_id, name, _ = self._create_type(dict_client)
        dp = DictPage(page)
        dp.open_type_page()
        dp.search_by_name(name)
        dp.delete_row(name)
        dp.expect_toast("成功")
        body = dict_client.get_type(type_id).json()
        assert_not_found(body)

    @allure.title("DICT_UI_011 新增字典数据后页面可查询")
    def test_add_dict_data(self, page, dict_client):
        type_id, _, type_ = self._create_type(dict_client)
        data_id, label, _ = self._create_data(dict_client, type_)
        try:
            dp = DictPage(page)
            dp.open_data_page(type_)
            dp.search_data_by_label(label)
            assert dp.row_exists(label)
        finally:
            dict_client.delete_data(data_id)
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_012 编辑字典数据成功")
    def test_edit_dict_data(self, page, dict_client):
        type_id, _, type_ = self._create_type(dict_client)
        data_id, label, value = self._create_data(dict_client, type_)
        new_label = gen_name("auto_edited")
        try:
            assert_api_ok(dict_client.update_data({
                "id": data_id, "sort": 1, "label": new_label, "value": value,
                "dictType": type_, "status": 0,
            }).json())
            dp = DictPage(page)
            dp.open_data_page(type_)
            dp.search_data_by_label(new_label)
            assert dp.row_exists(new_label)
        finally:
            dict_client.delete_data(data_id)
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_013 删除字典数据成功")
    def test_delete_dict_data(self, page, dict_client):
        type_id, _, type_ = self._create_type(dict_client)
        data_id, label, _ = self._create_data(dict_client, type_)
        try:
            dp = DictPage(page)
            dp.open_data_page(type_)
            dp.search_data_by_label(label)
            dp.delete_data_row(label)
            dp.expect_toast("成功")
            body = dict_client.get_data(data_id).json()
            assert_not_found(body)
        finally:
            dict_client.delete_data(data_id)
            dict_client.delete_type(type_id)
