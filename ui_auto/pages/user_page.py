"""UserPage：用户管理页 Page Object。

特点：含部门树、角色多选、状态开关、重置密码弹窗。
"""
from ui_auto.base.base_page import BasePage


class UserPage(BasePage):
    """用户管理页。open_page/reset_search/row_exists 继承自 BasePage。"""

    URL = "/system/user"

    def search_by_username(self, username):
        self.page.get_by_placeholder("请输入用户名称").fill(username)
        self.table_btn("搜索").click()

    def search_by_mobile(self, mobile):
        self.page.get_by_placeholder("请输入手机号码").fill(mobile)
        self.table_btn("搜索").click()

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

    def is_enabled(self, keyword):
        """读取用户行状态开关，返回当前是否启用。"""
        switch = self.table_row_by_keyword(keyword).get_by_role("switch")
        return switch.get_attribute("aria-checked") == "true"

    def toggle_status(self, keyword):
        """点击状态开关切换用户启用/禁用状态。

        Element Plus 的 el-switch 把 role=switch 放在内部隐藏的 input 上，
        Playwright 无法点击它；真正可点击的是外层 .el-switch 容器（onClick 绑定在此）。
        状态切换会弹出二次确认框，由调用方负责确认。
        """
        self.safe_auto_keyword(keyword)
        switch = self.table_row_by_keyword(keyword).locator(".el-switch").first
        switch.scroll_into_view_if_needed()
        switch.click()

    def toggle_status_and_wait(self, keyword, enabled):
        self.toggle_status(keyword)
        box = self.page.locator(".el-message-box")
        box.wait_for(state="visible", timeout=5000)
        confirm = box.get_by_role("button", name="确定", exact=True).first
        if not confirm.count():
            confirm = box.get_by_role("button", name="确 定").first
        self.click_and_wait_response(confirm, "/system/user/update-status")
        box.wait_for(state="hidden", timeout=5000)
        self.wait_switch_state(keyword, enabled)

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
