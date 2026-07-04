"""DictPage：字典管理页 Page Object。

定位策略：
- 路由：/system/dict（字典类型）/ /system/dict/data（字典数据）
- 查询输入框：placeholder 含"字典名称"
- 搜索/重置按钮：role=button
- 新增按钮：role=button name="新增"
- 弹窗：.el-dialog，表单项用 get_by_label
- 表格行：.el-table__row（仅此处用 CSS，无语义角色）
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class DictPage(BasePage):
    """字典管理页（字典类型）。"""

    TYPE_URL = "/system/dict"       # 字典类型页路由
    DATA_URL = "/dict/type/data"    # 字典数据页路由前缀

    def open_type_page(self):
        """打开字典类型页。"""
        self.open(cfg.web_url + self.TYPE_URL)
        self.wait_visible(self.page.locator(".el-table"))

    def open_data_page(self, dict_type=None):
        """打开字典数据页。Vue3 路由为 /dict/type/data/:dictType。"""
        url = f"/dict/type/data/{dict_type}" if dict_type else self.DATA_URL
        self.open(cfg.web_url + url)
        self.wait_visible(self.page.locator(".el-table"))

    # ===== 查询 =====
    def search_by_name(self, name):
        """按字典名称查询。"""
        self.page.get_by_placeholder("请输入字典名称").fill(name)
        self.page.get_by_role("button", name="搜索").click()

    def search_by_type(self, type_):
        """按字典类型查询。"""
        self.page.get_by_placeholder("请输入字典类型").fill(type_)
        self.page.get_by_role("button", name="搜索").click()

    def reset_search(self):
        """点击重置。"""
        self.page.get_by_role("button", name="重置").click()

    def type_name_query_value(self):
        return self.page.get_by_placeholder("请输入字典名称").input_value()

    def search_data_by_label(self, label):
        self.page.get_by_placeholder("请输入字典标签").fill(label)
        self.page.get_by_role("button", name="搜索").click()

    def delete_data_row(self, label):
        self.safe_auto_keyword(label)
        row = self.table_row_by_keyword(label)
        row.get_by_role("button", name="删除").click()
        self.messagebox_confirm()

    # ===== 新增 =====
    def add_type(self, name, type_):
        """新增字典类型。"""
        self.page.get_by_role("button", name="新增").click()
        dialog = self.visible_dialog()
        self.form_item_input(dialog, "字典名称").fill(name)
        self.form_item_input(dialog, "字典类型").fill(type_)
        # 状态默认开启，备注可选
        self.dialog_submit()

    # ===== 操作表格行 =====
    def row_exists(self, keyword):
        """表格是否存在含 keyword 的行。"""
        return self.table_has_row(keyword)

    def edit_row(self, keyword, new_name=None):
        """编辑某行。仅允许编辑本次 auto 测试数据且要求匹配唯一。"""
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="修改").click()
        dialog = self.visible_dialog()
        if new_name:
            name_input = self.form_item_input(dialog, "字典名称")
            name_input.fill("")
            name_input.fill(new_name)
        self.dialog_submit()

    def delete_row(self, keyword):
        """删除某行（含确认框）。仅允许删除本次 auto 测试数据且要求匹配唯一。"""
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="删除").click()
        self.messagebox_confirm()
