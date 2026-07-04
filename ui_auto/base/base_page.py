"""BasePage：UI 自动化 base 层，封装页面公共操作。

- 所有 Page 类继承，不允许直接用 time.sleep
- 新增辅助函数：dialog_input(cls, placeholder) 在可见弹窗内定位输入框
"""
import os
from urllib.parse import urlparse
from common.logger import log


class BasePage:
    def __init__(self, page):
        self.page = page

    def open(self, url):
        log.info("打开页面: %s", url)
        import os
        if os.getenv("CI"):
            # CI 下 Vite dev server 首次编译路由 chunk 较慢，用 domcontentloaded 避免等 load
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        else:
            self.page.goto(url)

    def click(self, locator):
        locator.click()

    def fill(self, locator, value):
        locator.fill(value)

    def wait_visible(self, locator, timeout=8000):
        locator.wait_for(state="visible", timeout=timeout)

    def wait_url(self, part, timeout=8000):
        self.page.wait_for_url(f"**{part}**", timeout=timeout)

    def wait_path(self, expected_path, timeout=15000):
        """严格等待 URL path，避免 redirect=/index 造成假通过。"""
        self.page.wait_for_url(
            lambda url: urlparse(str(url)).path == expected_path,
            timeout=timeout,
        )

    def toast_text(self, timeout=8000):
        """等待并获取 Element Plus 消息文本；找不到时直接失败，避免假通过。"""
        toast = self.page.locator(".el-message:visible, .el-notification:visible").first
        toast.wait_for(state="visible", timeout=timeout)
        return toast.inner_text()

    def expect_toast(self, expect_text, timeout=8000):
        """断言 Toast 文本必须出现并包含期望关键字。"""
        text = self.toast_text(timeout)
        assert expect_text in text, f"Toast 期望含'{expect_text}'，实际'{text}'"

    def click_menu(self, *names):
        for name in names:
            log.info("点击菜单: %s", name)
            item = self.page.locator(".el-menu-item, .el-sub-menu__title").filter(has_text=name).first
            if item.count() and item.is_visible():
                item.click()
            else:
                self.page.get_by_text(name, exact=True).first.click()

    def table_row_count(self):
        return self.page.locator(".el-table__row").count()

    def is_table_visible(self):
        """页面主表格是否可见。"""
        return self.page.locator(".el-table").is_visible()

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
        """弹窗内 input。Element Plus 弹窗 role=dialog，用语义化定位。"""
        return self.page.get_by_role("dialog").get_by_placeholder(placeholder)

    def form_item_input(self, scope, label, index=0):
        """按 Element Plus 表单项 label 查找 input，避免 label 未绑定 for 导致 get_by_label 失效。"""
        item = scope.locator(".el-form-item").filter(has_text=label).first
        return item.locator("input").nth(index)

    def form_item_select(self, scope, label):
        """按 Element Plus 表单项 label 查找下拉选择框 wrapper。"""
        item = scope.locator(".el-form-item").filter(has_text=label).first
        return item.locator(".el-select__wrapper, .el-tree-select__wrapper").first

    def click_tree_option(self, label, timeout=8000):
        """点击当前可见树形下拉中的选项。"""
        option = self.page.locator(".el-popper:visible .el-tree-node__label").filter(has_text=label).first
        option.wait_for(state="visible", timeout=timeout)
        option.click()

    def dialog_submit(self):
        """点击普通业务表单弹窗提交按钮（Element Plus Dialog，一般显示“确 定”）。"""
        dlg = self.page.get_by_role("dialog")
        btn = dlg.get_by_role("button", name="确 定").first
        if not btn.count():
            btn = dlg.get_by_role("button", name="确定").first
        btn.click()
        dlg.wait_for(state="hidden", timeout=5000)

    def dialog_confirm(self):
        """兼容旧调用名：普通表单弹窗提交。"""
        self.dialog_submit()

    def messagebox_confirm(self):
        """点击消息确认框确定按钮（Element Plus MessageBox，一般显示“确定”）。"""
        box = self.page.locator(".el-message-box")
        box.wait_for(state="visible", timeout=5000)
        btn = box.get_by_role("button", name="确定", exact=True).first
        if not btn.count():
            btn = box.get_by_role("button", name="确 定").first
        btn.click()
        box.wait_for(state="hidden", timeout=5000)

    def table_btn(self, button_name):
        """页面顶部表格操作按钮（搜索/重置/新增/导出等），用文本匹配避开 icon 前缀。"""
        return self.page.get_by_text(button_name).first

    def open_create_dialog(self):
        """点击页面工具栏新增按钮并返回可见业务弹窗。"""
        self.page.get_by_role("button", name="新增").first.click()
        return self.visible_dialog()

    def submit_empty_form(self):
        """提交空表单并返回当前可见校验错误数量。"""
        dialog = self.open_create_dialog()
        dialog.get_by_role("button", name="确 定").first.click()
        dialog.wait_for(state="visible", timeout=3000)
        invalid_items = dialog.locator(".el-form-item.is-error")
        invalid_items.first.wait_for(state="visible", timeout=3000)
        return invalid_items.count()

    def fill_vue(self, locator, text):
        """触发 Vue v-model：click 聚焦 + keyboard.type（带 delay 逐字输入）。"""
        locator.click()
        self.page.keyboard.press("Control+a")
        self.page.keyboard.press("Backspace")
        self.page.keyboard.type(str(text), delay=50)
