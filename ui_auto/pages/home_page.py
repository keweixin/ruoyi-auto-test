"""HomePage：首页 Page Object。

职责：判断是否在首页、菜单跳转、退出登录。
"""
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from ui_auto.base.base_page import BasePage


class HomePage(BasePage):
    """首页。"""

    def is_home_page(self, timeout=8000):
        """是否已进入首页（URL 含 index）。"""
        try:
            self.wait_url("index", timeout=timeout)
            return True
        except Exception:
            return "index" in self.page.url

    def goto_menu(self, *names):
        """逐级进入菜单，如 goto_menu("系统管理", "字典管理")。"""
        self.click_menu(*names)

    def logout(self):
        """退出登录：点头像 → 退出登录。"""
        self.page.locator(".avatar-wrapper:visible").hover()
        self.page.get_by_text("退出登录", exact=True).click()
        confirm = self.page.locator(".el-message-box:visible")
        confirm.get_by_role("button", name="确定", exact=True).click()

    def has_menu(self, menu_name, timeout=8000):
        """当前页面是否可见某菜单（用于权限差异验证）。"""
        menu_items = self.page.locator(
            ".sidebar-container .el-menu-item:visible, "
            ".sidebar-container .el-submenu__title:visible"
        )
        target = menu_items.filter(has_text=menu_name).first
        try:
            target.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False
