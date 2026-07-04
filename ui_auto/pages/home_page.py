"""HomePage：首页 Page Object。

职责：判断是否在首页、菜单跳转、退出登录。
"""
from urllib.parse import urlparse

from ui_auto.base.base_page import BasePage


class HomePage(BasePage):
    """首页。"""

    def is_home_page(self, timeout=8000):
        """是否已进入首页（URL 含 index）。"""
        try:
            self.wait_path("/index", timeout=timeout)
            return True
        except Exception:
            return urlparse(self.page.url).path == "/index"

    def goto_menu(self, *names):
        """逐级进入菜单，如 goto_menu("系统管理", "字典管理")。"""
        self.click_menu(*names)

    def logout(self):
        """退出登录：点用户下拉 → 退出系统/退出登录。"""
        trigger = self.page.locator(".user-info, [class*='user-info']").first
        if trigger.count() and trigger.is_visible():
            trigger.click()
        else:
            self.page.locator(".el-dropdown").last.click()
        item = self.page.get_by_text("退出系统", exact=True)
        if not item.count():
            item = self.page.get_by_text("退出登录", exact=True)
        item.click()
        self.messagebox_confirm()

    def has_menu(self, menu_name):
        """当前页面是否可见某菜单（用于权限差异验证）。"""
        return self.page.get_by_text(menu_name, exact=True).count() > 0
