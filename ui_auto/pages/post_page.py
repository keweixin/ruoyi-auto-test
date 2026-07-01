"""PostPage：岗位管理页 Page Object。

特点：普通分页表格 CRUD。
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class PostPage(BasePage):
    """岗位管理页。"""

    URL = "/system/post"

    def open_page(self):
        self.open(cfg.web_url + self.URL)
        self.wait_visible(self.page.locator(".el-table"))

    def search_by_name(self, name):
        self.page.get_by_placeholder("请输入岗位名称").fill(name)
        self.page.get_by_role("button", name="搜索").click()

    def reset_search(self):
        self.page.get_by_role("button", name="重置").click()

    def add(self, name, code):
        """新增岗位。"""
        self.page.get_by_role("button", name="新增").first.click()
        dialog = self.page.locator(".el-dialog").filter(visible=True).first
        dialog.get_by_placeholder("请输入岗位名称").fill(name)
        dialog.get_by_placeholder("请输入岗位编码").fill(code)
        dialog.get_by_text("确 定").click()
        self.page.wait_for_load_state("networkidle", timeout=5000)

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_text("删除").click()
        self.page.locator(".el-message-box").get_by_text("确定").click()
