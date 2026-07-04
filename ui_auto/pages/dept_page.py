"""DeptPage：部门管理页 Page Object。

特点：树形表格，上级部门下拉选择（el-tree-select）"""
from ui_auto.base.base_page import BasePage


class DeptPage(BasePage):
    """部门管理页。open_page/reset_search/row_exists 继承自 BasePage。"""

    URL = "/system/dept"

    def search_by_name(self, name):
        query_form = self.page.locator(".el-form").first
        query_form.get_by_placeholder("请输入部门名称").fill(name)
        self.table_btn("搜索").click()

    def add(self, name, sort=1):
        """新增顶级部门，并填写当前表单要求的全部必填项。"""
        self.table_btn("新增").click()
        dialog = self.visible_dialog()
        self.form_item_select(dialog, "上级部门").click()
        self.click_tree_option("顶级部门")
        self.dialog_input("请输入部门名称").fill(name)
        self.fill_vue(self.form_item_input(dialog, "显示排序"), sort)
        self.dialog_confirm()

    def edit_name(self, keyword, new_name):
        """修改唯一匹配部门的名称。"""
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="修改").click()
        dialog = self.visible_dialog()
        self.form_item_input(dialog, "部门名称").fill(new_name)
        self.dialog_submit()

    def set_status(self, keyword, label):
        """通过编辑表单设置部门状态；当前页面表格本身没有状态开关。"""
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="修改").click()
        dialog = self.visible_dialog()
        self.form_item_select(dialog, "状态").click()
        self.page.locator(".el-select-dropdown:visible .el-select-dropdown__item").filter(
            has_text=label
        ).first.click()
        self.dialog_submit()

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="删除").click()
        self.messagebox_confirm()
