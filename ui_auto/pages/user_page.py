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
        self.wait_visible(self.page.locator(".el-table"))

    def search_by_username(self, username):
        self.page.get_by_placeholder("请输入用户名称").fill(username)
        self.page.get_by_role("button", name="搜索").click()

    def search_by_mobile(self, mobile):
        self.page.get_by_placeholder("请输入手机号码").fill(mobile)
        self.page.get_by_role("button", name="搜索").click()

    def reset_search(self):
        self.page.get_by_role("button", name="重置").click()

    def add(self, username, nickname, mobile):
        """新增用户（简化版：用户名/昵称/手机号 + 默认部门）。"""
        self.page.get_by_role("button", name="新增").click()
        dialog = self.page.locator(".el-dialog").first
        dialog.get_by_label("用户名称").fill(username)
        dialog.get_by_label("用户昵称").fill(nickname)
        dialog.get_by_label("手机号码").fill(mobile)
        dialog.get_by_label("密码").fill("Test123456")
        dialog.get_by_role("button", name="确 定").click()

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def reset_password(self, keyword, new_pwd):
        """重置某用户密码。仅允许操作本次 auto 测试用户且要求匹配唯一。"""
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="重置密码").click()
        dialog = self.page.locator(".el-message-box")
        dialog.get_by_role("textbox").fill(new_pwd)
        dialog.get_by_role("button", name="确 定").click()

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="删除").click()
        self.page.locator(".el-message-box").get_by_role("button", name="确 定").click()
