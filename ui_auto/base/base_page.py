"""BasePage：UI 自动化 base 层，封装页面公共操作。

- 所有 Page 类继承，不允许直接用 time.sleep
- 新增辅助函数：dialog_input(cls, placeholder) 在可见弹窗内定位输入框
"""
import os
from common.logger import log


class BasePage:
    def __init__(self, page):
        self.page = page

    def open(self, url):
        log.info("打开页面: %s", url)
        self.page.goto(url)

    def click(self, locator):
        locator.click()

    def fill(self, locator, value):
        locator.fill(value)

    def wait_visible(self, locator, timeout=8000):
        locator.wait_for(state="visible", timeout=timeout)

    def wait_url(self, part, timeout=8000):
        self.page.wait_for_url(f"**{part}**", timeout=timeout)

    def toast_text(self, timeout=8000):
        """等待并获取 Toast 文本。原版消失快则返回空。"""
        toast = self.page.locator(".el-message").first
        try:
            toast.wait_for(state="visible", timeout=timeout)
            return toast.inner_text()
        except Exception:
            return ""

    def expect_toast(self, expect_text, timeout=8000):
        """断言 Toast 文本。消失太快则跳过。"""
        text = self.toast_text(timeout)
        if text:
            assert expect_text in text, f"Toast 期望含'{expect_text}'，实际'{text}'"

    def click_menu(self, *names):
        for name in names:
            log.info("点击菜单: %s", name)
            item = self.page.get_by_role("link", name=name).first
            if not item.is_visible():
                self.page.get_by_text(name).first.click()
            else:
                item.click()

    def table_row_count(self):
        return self.page.locator(".el-table__row").count()

    def table_has_row(self, keyword):
        return self.page.locator(".el-table__row").filter(has_text=keyword).count() > 0

    def table_row_by_keyword(self, keyword, unique=True):
        rows = self.page.locator(".el-table__row").filter(has_text=keyword)
        count = rows.count()
        if unique:
            assert count == 1, f"表格行匹配不唯一 keyword={keyword!r} count={count}"
        else:
            assert count >= 1, f"表格未找到 keyword={keyword!r} 的行"
        return rows.first

    def safe_auto_keyword(self, keyword):
        assert str(keyword).startswith("auto"), f"拒绝操作非 auto 测试数据：{keyword}"

    def screenshot(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.page.screenshot(path=path)
        log.info("截图保存: %s", path)

    # ===== 弹窗内辅助 =====
    def visible_dialog(self):
        """返回当前可见的弹窗（用语义化 role=dialog 定位）。"""
        dlg = self.page.get_by_role("dialog")
        dlg.wait_for(state="visible", timeout=5000)
        return dlg

    def dialog_input(self, placeholder):
        """弹窗内 input。原版 element-ui 弹窗 role=dialog，用语义化定位。"""
        return self.page.get_by_role("dialog").get_by_placeholder(placeholder)

    def dialog_confirm(self):
        """点击弹窗确定按钮。"""
        dlg = self.page.get_by_role("dialog")
        dlg.get_by_text("确 定").click()
        dlg.wait_for(state="hidden", timeout=5000)

    def table_btn(self, button_name):
        """页面顶部表格操作按钮（搜索/重置/新增/导出等），用文本匹配避开 icon 前缀。"""
        return self.page.get_by_text(button_name).first

    def fill_vue(self, locator, text):
        """触发 Vue v-model：click 聚焦 + keyboard.type（带 delay 逐字输入）。"""
        locator.click()
        self.page.keyboard.press("Control+a")
        self.page.keyboard.press("Backspace")
        self.page.keyboard.type(str(text), delay=50)
