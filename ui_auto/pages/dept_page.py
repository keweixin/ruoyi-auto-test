"""DeptPage: 部门管理页（原版 RuoYi element-ui，全语义化定位）。"""
from ui_auto.base.base_page import BasePage
from common.config import cfg

class DeptPage(BasePage):
    URL = "/system/dept"

    def open_page(self):
        self.open(cfg.web_url + self.URL)
        self.page.locator(".el-table__row").first.wait_for(state="visible", timeout=10000)

    def search_by_name(self, name):
        self.page.get_by_placeholder("请输入部门名称").first.fill(name)
        self.page.get_by_text("搜索").first.click()

    def reset_search(self):
        self.page.get_by_text("重置").first.click()

    def add(self, name):
        self.page.get_by_text("新增").first.click()
        dialog = self.page.get_by_role("dialog")
        dialog.get_by_placeholder("请输入部门名称").fill(name)
        dialog.get_by_text("确 定").click()
        dialog.wait_for(state="hidden", timeout=5000)

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="删除").click()
        self.page.locator(".el-message-box").get_by_text("确定").click()
