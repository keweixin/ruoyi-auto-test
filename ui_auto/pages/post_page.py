"""PostPage：岗位管理页 Page Object。

特点：普通分页表格 CRUD。
"""
from ui_auto.base.base_page import BasePage


class PostPage(BasePage):
    """岗位管理页。open_page/reset_search/row_exists 继承自 BasePage。"""

    URL = "/system/post"

    def search_by_name(self, name):
        self.page.get_by_placeholder("请输入岗位名称").fill(name)
        self.table_btn("搜索").click()

    def add(self, name, code):
        """新增岗位。"""
        self.table_btn("新增").click()
        dialog = self.visible_dialog()
        self.form_item_input(dialog, "岗位标题").fill(name)
        self.form_item_input(dialog, "岗位编码").fill(code)
        self.form_item_input(dialog, "岗位顺序").fill("1")
        self.dialog_submit()

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="删除").click()
        self.messagebox_confirm()
