"""LoginPage：登录页 Page Object。

定位策略（Element Plus 登录页）：
- 账号输入框：placeholder="请输入账号"
- 密码输入框：placeholder="请输入密码"
- 登录按钮：role=button name="登 录"
- 错误提示：.el-message（Toast）

注意：按钮文字"登 录"中间可能有空格，以本地为准，必要时改成 name="登"。
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class LoginPage(BasePage):
    """登录页。"""

    def __init__(self, page, web_url=None):
        super().__init__(page)
        self.web_url = web_url or cfg.web_url
        # 元素定位集中管理（语义化）
        self.username_input = page.get_by_placeholder("请输入账号")
        self.password_input = page.get_by_placeholder("请输入密码")
        self.login_btn = page.get_by_role("button", name="登 录")

    def open(self):
        """打开登录页。"""
        super().open(self.web_url)

    def login(self, username, password):
        """执行登录。"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()

    def login_as_admin(self):
        """用默认管理员登录。"""
        self.login(cfg.admin_user, cfg.admin_pwd)

    def get_error_toast(self):
        """获取错误提示文本。"""
        return self.toast_text()
