"""LoginPage：登录页 Page Object。

定位策略（Element Plus / Vue3 登录页）：
- 租户输入框：placeholder="请输入租户名称"（开启多租户时出现）
- 账号输入框：placeholder="请输入用户名"
- 密码输入框：placeholder="请输入密码"
- 登录按钮：role=button name="登录"
- 错误提示：.el-message（Toast）

注意：若验证码组件出现，测试环境应关闭 VITE_APP_CAPTCHA_ENABLE，或单独配置验证码自动化策略。
"""
from urllib.parse import urlparse

from ui_auto.base.base_page import BasePage
from common.config import cfg


class LoginPage(BasePage):
    """登录页。"""

    def __init__(self, page, web_url=None):
        super().__init__(page)
        self.web_url = web_url or cfg.web_url
        # 元素定位集中管理（语义化）
        self.tenant_input = page.get_by_placeholder("请输入租户名称")
        self.username_input = page.get_by_placeholder("请输入用户名")
        self.password_input = page.get_by_placeholder("请输入密码").first
        self.login_btn = page.get_by_role("button", name="登录", exact=True)

    def open(self):
        """打开登录页。"""
        super().open(self.web_url)

    def open_protected_page(self, path="/index"):
        """无登录态访问受保护页面并等待跳转到登录页。"""
        super().open(self.web_url + path)
        self.page.wait_for_url(
            lambda url: urlparse(str(url)).path == "/login",
            timeout=8000,
        )

    def is_login_page(self):
        return urlparse(self.page.url).path == "/login"

    def validation_error_count(self, timeout=3000):
        invalid_items = self.page.locator(".el-form-item.is-error")
        invalid_items.first.wait_for(state="visible", timeout=timeout)
        return invalid_items.count()

    def login(self, username, password, tenant_name=None):
        """执行登录。"""
        if self.tenant_input.count() > 0 and self.tenant_input.first.is_visible():
            self.tenant_input.first.fill(tenant_name if tenant_name is not None else getattr(cfg, "tenant_name", "芋道源码"))
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()
        verify = self.page.locator(".verifybox, .verify-img-out, .verify-bar-area")
        if verify.count() > 0 and verify.first.is_visible():
            raise AssertionError("当前前端开启了验证码，请关闭 VITE_APP_CAPTCHA_ENABLE 或配置自动化验证码策略")

    def login_as_admin(self):
        """用默认管理员登录并等待进入首页。"""
        self.login(cfg.admin_user, cfg.admin_pwd)
        self.wait_logged_in()

    def wait_logged_in(self, timeout=None):
        """严格等待登录路由完成，避免 redirect=/index 造成假通过。

        CI 环境（Vite dev server 首次编译首页 chunk 较慢）默认给 40s，
        本地默认 15s。
        """
        import os
        if timeout is None:
            timeout = 40000 if os.getenv("CI") else 15000
        self.page.wait_for_url(
            lambda url: urlparse(str(url)).path in ("/", "/index"),
            timeout=timeout,
        )

    def get_error_toast(self):
        """获取错误提示文本。"""
        alert = self.page.get_by_role("alert").first
        alert.wait_for(state="visible", timeout=5000)
        return alert.inner_text()
