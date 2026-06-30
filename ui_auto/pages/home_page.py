"""HomePage：首页 Page Object。

职责：判断是否在首页、菜单跳转、退出登录。
"""
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
        # 若依前端退出入口通常是右上角用户下拉
        self.page.get_by_role("button", name="退出登录").click()

    def has_menu(self, menu_name):
        """当前页面是否可见某菜单（用于权限差异验证）。"""
        return self.page.get_by_role("link", name=menu_name).count() > 0
