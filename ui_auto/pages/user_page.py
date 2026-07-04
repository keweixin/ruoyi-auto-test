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
        """新增用户（填写用户名/昵称/手机号/密码 + 默认部门）。"""
        self.page.get_by_role("button", name="新增").click()
        dialog = self.visible_dialog()
        self.form_item_select(dialog, "归属部门").click()
        self.click_tree_option("芋道源码")
        self.form_item_input(dialog, "用户名称").fill(username)
        self.form_item_input(dialog, "用户昵称").fill(nickname)
        self.form_item_input(dialog, "手机号码").fill(mobile)
        self.form_item_input(dialog, "用户密码").fill("Test123456")
        self.dialog_submit()

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def is_enabled(self, keyword):
        """读取用户行状态开关，返回当前是否启用。"""
        switch = self.table_row_by_keyword(keyword).get_by_role("switch")
        return switch.get_attribute("aria-checked") == "true"

    def reset_password(self, keyword, new_pwd):
        """重置某用户密码。仅允许操作本次 auto 测试用户且要求匹配唯一。"""
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="更多").click()
        self.page.get_by_text("重置密码", exact=True).click()
        dialog = self.page.locator(".el-message-box")
        dialog.get_by_role("textbox").fill(new_pwd)
        self.messagebox_confirm()

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="更多").click()
        self.page.get_by_text("删除", exact=True).click()
        self.messagebox_confirm()
