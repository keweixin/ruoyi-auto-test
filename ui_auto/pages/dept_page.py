"""DeptPage：部门管理页 Page Object。

特点：树形表格，上级部门下拉选择（el-tree-select）。
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class DeptPage(BasePage):
    """部门管理页。"""

    URL = "/system/dept"

    def open_page(self):
        self.open(cfg.web_url + self.URL)
        self.wait_visible(self.page.locator(".el-table"))

    def search_by_name(self, name):
        self.page.get_by_placeholder("请输入部门名称").fill(name)
        self.page.get_by_role("button", name="搜索").click()

    def reset_search(self):
        self.page.get_by_role("button", name="重置").click()

    def add(self, name):
        """新增部门（顶级，parentId=0）。"""
        self.page.get_by_role("button", name="新增").click()
        dialog = self.page.locator(".el-dialog").first
        dialog.get_by_label("部门名称").fill(name)
        dialog.get_by_role("button", name="确 定").click()

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="删除").click()
        self.page.locator(".el-message-box").get_by_role("button", name="确 定").click()
