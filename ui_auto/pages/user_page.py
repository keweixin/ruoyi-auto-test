"""UserPage：用户管理页 Page Object。

特点：含部门树、角色多选、状态开关、重置密码弹窗。
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class UserPage(BasePage):
    """用户管理页。"""

    URL = "/system/user"

    def open_page(self):
        self.open(cfg.web_url + self.URL)
        self.page.locator(".el-table__row").first.wait_for(state="visible", timeout=10000)

    def search_by_username(self, username):
        self.fill_vue(self.page.get_by_placeholder("请输入用户名称").first, username)
        self.page.get_by_text("搜索").first.click()
        self.page.wait_for_load_state("networkidle", timeout=5000)

    def search_by_mobile(self, mobile):
        self.fill_vue(self.page.get_by_placeholder("请输入手机号码").first, mobile)
        self.page.get_by_text("搜索").first.click()
        self.page.wait_for_load_state("networkidle", timeout=5000)

    def reset_search(self):
        self.page.get_by_text("重置").first.click()

    def add(self, username, nickname, mobile):
        """新增用户（简化版：用户名/昵称/手机号 + 默认部门）。"""
        self.page.get_by_text("新增").first.click()
        dialog = self.page.get_by_role("dialog")
        self.fill_vue(dialog.get_by_placeholder("请输入用户名称").first, username)
        self.fill_vue(dialog.get_by_placeholder("请输入用户昵称").first, nickname)
        self.fill_vue(dialog.get_by_placeholder("请输入手机号码").first, mobile)
        self.fill_vue(dialog.get_by_placeholder("请输入用户密码").first, "Test123456")
        dialog.get_by_text("确 定").click()
        self.page.wait_for_load_state("networkidle", timeout=5000)

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def reset_password(self, keyword, new_pwd):
        """重置某用户密码。原版用 el-message-box 弹窗输入。"""
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_text("重置密码").click()
        # 重置密码弹窗是 el-message-box
        msgbox = self.page.locator(".el-message-box")
        msgbox.wait_for(state="visible", timeout=5000)
        self.fill_vue(msgbox.get_by_role("textbox"), new_pwd)
        msgbox.get_by_text("确定").click()
        self.page.wait_for_load_state("networkidle", timeout=5000)

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_text("删除").click()
        self.page.locator(".el-message-box").get_by_text("确定").click()
