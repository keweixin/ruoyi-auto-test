"""MenuPage：菜单管理页 Page Object。

特点：树形表格，菜单类型（目录/菜单/按钮）。
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class MenuPage(BasePage):
    """菜单管理页。"""

    URL = "/system/menu"

    def open_page(self):
        self.open(cfg.web_url + self.URL)
        self.wait_visible(self.page.locator(".el-table"))

    def search_by_name(self, name):
        self.page.get_by_placeholder("请输入菜单名称").fill(name)
        self.page.get_by_role("button", name="搜索").click()

    def reset_search(self):
        self.page.get_by_role("button", name="重置").click()

    def add(self, name, menu_type="菜单"):
        """新增菜单。menu_type: 目录/菜单/按钮。"""
        self.page.get_by_role("button", name="新增").first.click()
        dialog = self.page.locator(".el-dialog").filter(visible=True).first
        dialog.get_by_placeholder("请输入菜单名称").fill(name)
        # 选择菜单类型（radio）
        dialog.get_by_text(menu_type, exact=True).click()
        dialog.get_by_text("确 定").click()
        self.page.wait_for_timeout(800)

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_text("删除").click()
        self.page.locator(".el-message-box").get_by_text("确定").click()
