"""BasePage：UI 自动化 base 层，封装页面公共操作。

设计说明：
- 所有 Page 类继承它，复用 open/click/fill/wait/screenshot 等。
- 严格遵守：禁用 time.sleep，使用 Playwright 自带的自动等待和 expect 断言。
- 定位策略：优先 get_by_role / get_by_label / get_by_placeholder / get_by_text 等语义化定位，
  仅对表格行等无语义元素使用最小 CSS（如 .el-table__row）。
"""
import os

from common.logger import log


class BasePage:
    """所有 Page 类的基类。"""

    def __init__(self, page):
        self.page = page

    # ===== 基础导航 =====
    def open(self, url):
        """打开指定 URL。"""
        log.info("打开页面: %s", url)
        self.page.goto(url)

    # ===== 元素操作（均带自动等待）=====
    def click(self, locator):
        """点击元素（自动等待可点击）。"""
        locator.click()

    def fill(self, locator, value):
        """清空并输入文本。"""
        locator.fill(value)

    def get_text(self, locator):
        """获取元素文本。"""
        return locator.inner_text()

    # ===== 等待（替代 sleep）=====
    def is_visible(self, locator, timeout=8000):
        """元素是否可见。"""
        return locator.is_visible(timeout=timeout)

    def wait_visible(self, locator, timeout=8000):
        """等待元素可见。"""
        locator.wait_for(state="visible", timeout=timeout)

    def wait_url(self, part, timeout=8000):
        """等待 URL 包含某片段。"""
        self.page.wait_for_url(f"**{part}**", timeout=timeout)

    # ===== Toast 提示（若依用 el-message）=====
    def toast_text(self, timeout=5000):
        """等待并获取 Toast(el-message) 文本。"""
        toast = self.page.locator(".el-message").first
        toast.wait_for(state="visible", timeout=timeout)
        return toast.inner_text()

    def expect_toast(self, expect_text, timeout=5000):
        """断言 Toast 文本包含某关键词。"""
        text = self.toast_text(timeout)
        assert expect_text in text, f"Toast 期望含'{expect_text}'，实际'{text}'"

    # ===== 菜单跳转 =====
    def click_menu(self, *names):
        """逐级点击菜单：click_menu("系统管理", "字典管理")。"""
        for name in names:
            log.info("点击菜单: %s", name)
            # 侧边栏菜单用 link 角色；先展开父菜单
            item = self.page.get_by_role("link", name=name).first
            if not item.is_visible():
                # 尝试先点父级展开
                self.page.get_by_text(name).first.click()
            else:
                item.click()

    # ===== 表格操作（仅此处用最小 CSS，因 el-table 行无语义角色）=====
    def table_row_count(self):
        """返回当前表格数据行数。"""
        return self.page.locator(".el-table__row").count()

    def table_has_row(self, keyword):
        """表格中是否存在包含 keyword 的行。"""
        return self.page.locator(".el-table__row").filter(has_text=keyword).count() > 0

    def table_row_by_keyword(self, keyword, unique=True):
        """按关键字获取表格行。

        unique=True 时要求只匹配一行，避免误删/误改历史残留或系统数据。
        """
        rows = self.page.locator(".el-table__row").filter(has_text=keyword)
        count = rows.count()
        if unique:
            assert count == 1, f"表格行匹配不唯一 keyword={keyword!r} count={count}"
        else:
            assert count >= 1, f"表格未找到 keyword={keyword!r} 的行"
        return rows.first

    def safe_auto_keyword(self, keyword):
        """只允许 UI 删除/修改本次自动化创建的 auto 数据，防止误操作系统数据。"""
        assert str(keyword).startswith("auto"), f"拒绝操作非 auto 测试数据：{keyword}"

    # ===== 截图 =====
    def screenshot(self, path):
        """页面截图。"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.page.screenshot(path=path)
        log.info("截图保存: %s", path)
