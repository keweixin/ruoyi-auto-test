"""字典管理 UI 测试用例（原版 element-ui，全语义化定位）。

原版特点：
- 表格无 switch，状态切换通过"修改"弹窗单选框
- 字典数据页路由 /system/dict-data/index/:dictId
- 按钮用 get_by_role("button", name="修改"/"删除")
- 表格加载用 .el-table__row 等待
"""
import allure
from common.random_utils import gen_name
from ui_auto.pages.dict_page import DictPage


@allure.feature("字典管理 UI")
class TestDictUi:

    # ==================== 字典类型 ====================

    @allure.title("DICT_UI_001 进入字典管理页面成功")
    def test_open_dict_page(self, page):
        dp = DictPage(page); dp.open_type_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("DICT_UI_002 按字典名称查询成功")
    def test_search_by_name(self, page):
        dp = DictPage(page); dp.open_type_page()
        dp.search_by_name("性别")
        assert dp.table_row_count() >= 1

    @allure.title("DICT_UI_003 按字典类型查询成功")
    def test_search_by_type(self, page):
        dp = DictPage(page); dp.open_type_page()
        dp.search_by_type("sys_user_sex")
        assert dp.table_row_count() >= 1

    @allure.title("DICT_UI_004 点击重置后查询条件清空")
    def test_reset_search(self, page):
        dp = DictPage(page); dp.open_type_page()
        dp.search_by_name("性别")
        dp.reset_search()
        assert page.get_by_placeholder("请输入字典名称").first.input_value() == ""

    @allure.title("DICT_UI_005 新增字典类型成功")
    def test_add_dict(self, page):
        dp = DictPage(page); dp.open_type_page()
        name = gen_name("auto_dict"); type_ = gen_name("auto_type")
        dp.add_type(name, type_)
        dp.search_by_name(name)
        assert dp.row_exists(name), "新增后表格未查到"

    @allure.title("DICT_UI_006 新增字典类型必填项为空提示")
    def test_add_empty_name(self, page):
        dp = DictPage(page); dp.open_type_page()
        page.get_by_text("新增").first.click()
        dialog = page.get_by_role("dialog")
        dialog.get_by_text("确 定").click()
        assert page.locator(".el-form-item__error").count() > 0, "未出现必填校验"

    @allure.title("DICT_UI_007 编辑字典类型成功")
    def test_edit_dict(self, page, dict_client):
        name = gen_name("auto_dict"); type_ = gen_name("auto_type")
        dict_client.create_type({"dictName": name, "dictType": type_, "status": "0"})
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        type_id = rows[0]["dictId"]
        try:
            dp = DictPage(page); dp.open_type_page()
            dp.search_by_name(name)
            new_name = gen_name("auto_edited")
            dp.page.locator(".el-table__row").filter(has_text=name).get_by_role("button", name="修改").click()
            dialog = page.get_by_role("dialog")
            inp = dialog.get_by_placeholder("请输入字典名称")
            inp.fill("")
            inp.fill(new_name)
            dialog.get_by_text("确 定").click()
            dialog.wait_for(state="hidden", timeout=5000)
            dp.search_by_name(new_name)
            assert dp.row_exists(new_name), "编辑后未查到新名称"
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_008 停用字典类型成功")
    def test_disable_dict(self, page, dict_client):
        name = gen_name("auto_dict"); type_ = gen_name("auto_type")
        dict_client.create_type({"dictName": name, "dictType": type_, "status": "0"})
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        type_id = rows[0]["dictId"]
        try:
            dp = DictPage(page); dp.open_type_page()
            dp.search_by_name(name)
            dp.page.locator(".el-table__row").filter(has_text=name).get_by_role("button", name="修改").click()
            dialog = page.get_by_role("dialog")
            dialog.get_by_text("停用").click()
            dialog.get_by_text("确 定").click()
            dialog.wait_for(state="hidden", timeout=5000)
            resp = dict_client.get_type(type_id).json()
            assert resp["data"]["status"] == "1", f"状态未变为停用: {resp}"
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_009 启用字典类型成功")
    def test_enable_dict(self, page, dict_client):
        name = gen_name("auto_dict"); type_ = gen_name("auto_type")
        dict_client.create_type({"dictName": name, "dictType": type_, "status": "1"})
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        type_id = rows[0]["dictId"]
        try:
            dp = DictPage(page); dp.open_type_page()
            dp.search_by_name(name)
            dp.page.locator(".el-table__row").filter(has_text=name).get_by_role("button", name="修改").click()
            dialog = page.get_by_role("dialog")
            dialog.get_by_text("正常").click()
            dialog.get_by_text("确 定").click()
            dialog.wait_for(state="hidden", timeout=5000)
            resp = dict_client.get_type(type_id).json()
            assert resp["data"]["status"] == "0", f"状态未变为启用: {resp}"
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_010 删除字典类型成功")
    def test_delete_dict(self, page, dict_client):
        name = gen_name("auto_dict"); type_ = gen_name("auto_type")
        dict_client.create_type({"dictName": name, "dictType": type_, "status": "0"})
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        type_id = rows[0]["dictId"]
        try:
            dp = DictPage(page); dp.open_type_page()
            dp.search_by_name(name)
            dp.delete_row(name)
            dp.page.wait_for_timeout(800)
            dp.search_by_name(name)
            assert not dp.row_exists(name), "删除后仍能查到"
        finally:
            try:
                dict_client.delete_type(type_id)
            except Exception:
                pass

    # ==================== 字典数据 ====================

    @allure.title("DICT_UI_011 新增字典数据成功")
    def test_add_dict_data(self, page, dict_client):
        type_ = gen_name("auto_type")
        dict_client.create_type({"dictName": gen_name("auto_dict"), "dictType": type_, "status": "0"})
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        type_id = rows[0]["dictId"]
        try:
            dp = DictPage(page); dp.open_data_page(type_id)
            # 新增字典数据
            label = gen_name("auto_label")
            page.get_by_text("新增").first.click()
            dialog = page.get_by_role("dialog")
            dialog.get_by_placeholder("请输入数据标签").fill(label)
            dialog.get_by_placeholder("请输入数据键值").fill("1")
            dialog.get_by_text("确 定").click()
            dialog.wait_for(state="hidden", timeout=5000)
            # 搜索验证
            page.get_by_placeholder("请输入字典标签").fill(label)
            page.get_by_text("搜索").first.click()
            assert dp.row_exists(label), "新增字典数据后表格未查到"
        finally:
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_012 编辑字典数据成功")
    def test_edit_dict_data(self, page, dict_client):
        type_ = gen_name("auto_type")
        dict_client.create_type({"dictName": gen_name("auto_dict"), "dictType": type_, "status": "0"})
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        type_id = rows[0]["dictId"]
        label = gen_name("auto_label")
        dict_client.create_data({"dictSort": 1, "dictLabel": label, "dictValue": "1", "dictType": type_, "status": "0"})
        rows_d = dict_client.list_data({"dictType": type_}).json()["rows"]
        data_code = rows_d[0]["dictCode"]
        try:
            dp = DictPage(page); dp.open_data_page(type_id)
            # 搜索
            page.get_by_placeholder("请输入字典标签").fill(label)
            page.get_by_text("搜索").first.click()
            # 修改
            new_label = gen_name("auto_edited")
            page.locator(".el-table__row").filter(has_text=label).get_by_role("button", name="修改").click()
            dialog = page.get_by_role("dialog")
            inp = dialog.get_by_placeholder("请输入数据标签")
            inp.fill("")
            inp.fill(new_label)
            dialog.get_by_text("确 定").click()
            dialog.wait_for(state="hidden", timeout=5000)
            # 搜索验证
            page.get_by_placeholder("请输入字典标签").fill("")
            page.get_by_placeholder("请输入字典标签").fill(new_label)
            page.get_by_text("搜索").first.click()
            assert dp.row_exists(new_label), "编辑字典数据后未查到新标签"
        finally:
            try:
                dict_client.delete_data(data_code)
            except Exception:
                pass
            dict_client.delete_type(type_id)

    @allure.title("DICT_UI_013 删除字典数据成功")
    def test_delete_dict_data(self, page, dict_client):
        type_ = gen_name("auto_type")
        dict_client.create_type({"dictName": gen_name("auto_dict"), "dictType": type_, "status": "0"})
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        type_id = rows[0]["dictId"]
        label = gen_name("auto_label")
        dict_client.create_data({"dictSort": 1, "dictLabel": label, "dictValue": "1", "dictType": type_, "status": "0"})
        rows_d = dict_client.list_data({"dictType": type_}).json()["rows"]
        data_code = rows_d[0]["dictCode"]
        try:
            dp = DictPage(page); dp.open_data_page(type_id)
            page.get_by_placeholder("请输入字典标签").fill(label)
            page.get_by_text("搜索").first.click()
            # 删除
            page.locator(".el-table__row").filter(has_text=label).get_by_role("button", name="删除").click()
            page.locator(".el-message-box").get_by_text("确定").click()
            page.wait_for_timeout(800)
            # 搜索验证消失
            page.get_by_placeholder("请输入字典标签").fill("")
            page.get_by_placeholder("请输入字典标签").fill(label)
            page.get_by_text("搜索").first.click()
            assert not dp.row_exists(label), "删除字典数据后仍能查到"
        finally:
            try:
                dict_client.delete_data(data_code)
            except Exception:
                pass
            dict_client.delete_type(type_id)
