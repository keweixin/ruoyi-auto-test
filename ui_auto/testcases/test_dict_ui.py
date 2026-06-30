"""字典管理 UI 测试用例。

覆盖 DICT_UI_001 ~ 013：
- 进入页面/查询/重置/新增/必填校验/编辑/停用/启用/删除
- 字典数据 新增/编辑/删除

学习重点：表格查询、新增弹窗、编辑弹窗、删除确认框、Toast 断言。
推荐：用接口造数 → UI 验证（更稳，见 integration）。
"""
import time
import allure
import pytest

from common.config import cfg
from common.random_utils import gen_name
from ui_auto.pages.dict_page import DictPage


@allure.feature("字典管理 UI")
class TestDictUi:

    @allure.title("DICT_UI_001 进入字典管理页面成功")
    def test_open_dict_page(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        assert page.locator(".el-table").is_visible(), "字典页表格未展示"

    @allure.title("DICT_UI_002 按字典名称查询成功")
    def test_search_by_name(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        dp.search_by_name("性别")  # 若依自带"用户性别"字典
        # 表格应有数据
        assert dp.table_row_count() >= 1, "查询无结果"

    @allure.title("DICT_UI_003 按字典类型查询成功")
    def test_search_by_type(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        dp.search_by_type("sys_user_sex")
        assert dp.table_row_count() >= 1, "查询无结果"

    @allure.title("DICT_UI_004 点击重置后查询条件清空")
    def test_reset_search(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        dp.search_by_name("性别")
        dp.reset_search()
        # 重置后输入框应清空
        assert dp.page.get_by_placeholder("请输入字典名称").input_value() == ""

    @allure.title("DICT_UI_005 新增字典类型成功")
    def test_add_dict(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        name = gen_name("auto_dict")
        type_ = gen_name("auto_type")
        dp.add_type(name, type_)
        dp.expect_toast("成功")
        dp.search_by_name(name)
        assert dp.row_exists(name), "新增后表格未查到"

    @allure.title("DICT_UI_006 新增字典类型必填项为空提示")
    def test_add_empty_name(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        dp.page.get_by_role("button", name="新增").click()
        dialog = dp.page.locator(".el-dialog").first
        # 不填名称直接确定
        dialog.get_by_role("button", name="确 定").click()
        # 应出现表单校验错误
        assert dp.page.locator(".el-form-item__error").count() > 0, "未出现必填校验"

    @allure.title("DICT_UI_007 编辑字典类型成功")
    def test_edit_dict(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        name = gen_name("auto_dict")
        dp.add_type(name, gen_name("auto_type"))
        dp.search_by_name(name)
        new_name = gen_name("auto_edited")
        dp.edit_row(name, new_name=new_name)
        dp.expect_toast("成功")

    @allure.title("DICT_UI_008 停用字典类型成功")
    def test_disable_dict(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        name = gen_name("auto_dict")
        dp.add_type(name, gen_name("auto_type"))
        dp.search_by_name(name)
        # 状态切换（开关或操作列）
        row = dp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("switch").click()
        dp.expect_toast("成功")

    @allure.title("DICT_UI_009 启用字典类型成功")
    def test_enable_dict(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        name = gen_name("auto_dict")
        dp.add_type(name, gen_name("auto_type"))
        dp.search_by_name(name)
        row = dp.page.locator(".el-table__row").filter(has_text=name)
        # 连点两次模拟停用再启用
        row.get_by_role("switch").click()
        row.get_by_role("switch").click()
        dp.expect_toast("成功")

    @allure.title("DICT_UI_010 删除字典类型成功")
    def test_delete_dict(self, page):
        dp = DictPage(page)
        dp.open_type_page()
        name = gen_name("auto_dict")
        dp.add_type(name, gen_name("auto_type"))
        dp.search_by_name(name)
        dp.delete_row(name)
        dp.expect_toast("成功")

    @allure.title("DICT_UI_011 新增字典数据成功")
    def test_add_dict_data(self, page):
        dp = DictPage(page)
        dp.open_data_page()
        dp.page.get_by_role("button", name="新增").click()
        dialog = dp.page.locator(".el-dialog").first
        dialog.get_by_label("数据标签").fill(gen_name("自动选项"))
        dialog.get_by_label("数据键值").fill(gen_name("v"))
        dialog.get_by_role("button", name="确 定").click()
        dp.expect_toast("成功")

    @allure.title("DICT_UI_012 编辑字典数据成功")
    def test_edit_dict_data(self, page, dict_client):
        """接口先造 auto 字典数据，再 UI 精确定位本次数据编辑，禁止操作系统第一行。"""
        dp = DictPage(page)
        type_ = gen_name("auto_type")
        type_id = dict_client.create_type({"name": gen_name("auto_dict"), "type": type_, "status": 0}).json()["data"]
        label = gen_name("auto_label")
        data_id = dict_client.create_data({
            "sort": 1, "label": label, "value": gen_name("auto_value"), "dictType": type_, "status": 0
        }).json()["data"]
        try:
            dp.open_data_page()
            dp.page.get_by_placeholder("请输入字典标签").fill(label)
            dp.page.get_by_role("button", name="搜索").click()
            row = dp.table_row_by_keyword(label)
            row.get_by_role("button", name="修改").click()
            dialog = dp.page.locator(".el-dialog").first
            new_label = gen_name("auto_edited")
            label_input = dialog.get_by_label("数据标签")
            label_input.fill("")
            label_input.fill(new_label)
            dialog.get_by_role("button", name="确 定").click()
            dp.expect_toast("成功")
            assert dict_client.get_data(data_id).json()["data"]["label"] == new_label
        finally:
            dict_client.delete_data(data_id)
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_013 删除字典数据成功")
    def test_delete_dict_data(self, page, dict_client):
        """接口先造 auto 字典数据，再 UI 精确定位本次数据删除，禁止操作系统第一行。"""
        dp = DictPage(page)
        type_ = gen_name("auto_type")
        type_id = dict_client.create_type({"name": gen_name("auto_dict"), "type": type_, "status": 0}).json()["data"]
        label = gen_name("auto_label")
        data_id = dict_client.create_data({
            "sort": 1, "label": label, "value": gen_name("auto_value"), "dictType": type_, "status": 0
        }).json()["data"]
        try:
            dp.open_data_page()
            dp.page.get_by_placeholder("请输入字典标签").fill(label)
            dp.page.get_by_role("button", name="搜索").click()
            row = dp.table_row_by_keyword(label)
            row.get_by_role("button", name="删除").click()
            dp.page.locator(".el-message-box").get_by_role("button", name="确 定").click()
            dp.expect_toast("成功")
            body = dict_client.get_data(data_id).json()
            assert body.get("code") != 0 or not body.get("data"), "UI 删除后接口仍能查到字典数据"
        finally:
            dict_client.delete_data(data_id)
            dict_client.delete_type(type_id)
