"""字典 接口+UI 联动测试。

覆盖 DICT_FLOW_001 ~ 004：
- 接口创建 → UI 查询验证
- UI 创建 → 接口查询验证
- UI 编辑 → 接口查询验证
- 接口删除 → UI 查询验证不存在

价值：体现接口造数、UI 验证、接口清理。
"""
import allure
import pytest

from common.config import cfg
from common.assert_utils import assert_api_ok
from common.random_utils import gen_name
from api_auto.clients.dict_client import DictClient
from ui_auto.pages.dict_page import DictPage


@allure.feature("字典 接口+UI 联动")
class TestDictFlow:

    @allure.title("DICT_FLOW_001 接口创建字典类型，UI 查询验证展示正确")
    def test_api_create_ui_verify(self, page, admin_token):
        """接口造数 → UI 验证展示 → 接口清理。"""
        # 1. 接口造数
        api = DictClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        new_id = api.create_type({"name": name, "type": type_, "status": 0, "remark": "flow"}).json()["data"]

        try:
            # 2. UI 验证
            dp = DictPage(page)
            dp.open_type_page()
            dp.search_by_name(name)
            assert dp.row_exists(name), "UI 未查到接口创建的字典"
        finally:
            # 3. 接口清理
            api.delete_type(new_id)

    @allure.title("DICT_FLOW_002 UI 创建字典类型，接口查询验证数据正确")
    def test_ui_create_api_verify(self, page, admin_token):
        """UI 新增 → 接口查询确认 → 接口清理。"""
        # 1. UI 新增
        dp = DictPage(page)
        dp.open_type_page()
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        dp.add_type(name, type_)
        dp.expect_toast("成功")

        # 2. 接口查询确认
        api = DictClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        body = api.page_type({"pageNo": 1, "pageSize": 10, "name": name}).json()
        assert_api_ok(body)
        assert body["data"]["total"] >= 1, "接口未查到 UI 创建的字典"

        # 3. 接口清理
        new_id = body["data"]["list"][0]["id"]
        api.delete_type(new_id)

    @allure.title("DICT_FLOW_003 UI 编辑字典类型，接口查询验证修改成功")
    def test_ui_edit_api_verify(self, page, admin_token):
        """接口造数 → UI 编辑 → 接口查询确认修改 → 接口清理。"""
        # 1. 接口造数
        api = DictClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        new_id = api.create_type({"name": name, "type": type_, "status": 0}).json()["data"]
        try:
            # 2. UI 编辑
            dp = DictPage(page)
            dp.open_type_page()
            dp.search_by_name(name)
            new_name = gen_name("auto_edited")
            dp.edit_row(name, new_name=new_name)
            dp.expect_toast("成功")
            # 3. 接口查询确认
            body = api.get_type(new_id).json()
            assert_api_ok(body)
            assert body["data"]["name"] == new_name, "接口查到的名称未更新"
        finally:
            api.delete_type(new_id)

    @allure.title("DICT_FLOW_004 接口删除字典类型，UI 查询验证数据不存在")
    def test_api_delete_ui_verify(self, page, admin_token):
        """接口造数 → 接口删除 → UI 查询验证不存在。"""
        # 1. 接口造数
        api = DictClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        new_id = api.create_type({"name": name, "type": type_, "status": 0}).json()["data"]

        # 2. 接口删除
        api.delete_type(new_id)

        # 3. UI 查询验证不存在
        dp = DictPage(page)
        dp.open_type_page()
        dp.search_by_name(name)
        assert not dp.row_exists(name), "接口已删除，UI 仍能查到"
