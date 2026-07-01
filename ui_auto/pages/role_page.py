"""RolePage：角色管理页 Page Object。

特点：分配菜单权限用菜单树勾选（el-tree 的 checkbox）。
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class RolePage(BasePage):
    """角色管理页。"""

    URL = "/system/role"

    def open_page(self):
        self.open(cfg.web_url + self.URL)
        self.wait_visible(self.page.locator(".el-table"))

    def search_by_name(self, name):
        self.fill_vue(self.page.get_by_placeholder("请输入角色名称").first, name)
        self.page.get_by_text("搜索").first.click()
        self.page.wait_for_timeout(800)

    def reset_search(self):
        self.page.get_by_text("重置").first.click()

    def add(self, name, code):
        """新增角色。"""
        self.page.get_by_text("新增").first.click()
        dialog = self.page.get_by_role("dialog")
        self.fill_vue(dialog.get_by_placeholder("请输入角色名称").first, name)
        self.fill_vue(dialog.get_by_placeholder("请输入角色权限字符").first, code)
        dialog.get_by_text("确 定").click()
        self.page.wait_for_timeout(800)

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def assign_menu(self, keyword, menu_names=None):
        """给角色分配菜单权限。仅允许操作本次 auto 测试角色且要求匹配唯一。"""
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_text("菜单权限").click()
        dialog = self.page.get_by_role("dialog")
        if menu_names:
            for name in menu_names:
                dialog.get_by_text(name).first.click()
        dialog.get_by_text("确 定").click()
        self.page.wait_for_timeout(800)

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_text("删除").click()
        self.page.locator(".el-message-box").get_by_text("确定").click()
