"""MenuPage：菜单管理页 Page Object。

特点：树形表格，菜单类型（目录/菜单/按钮）。
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class MenuPage(BasePage):
    """菜单管理页。"""

    URL = "/system/menu"

    def open_page(self):
        self.open(cfg.web_url + self.URL)
        self.wait_visible(self.page.get_by_text("菜单名称").first)

    def search_by_name(self, name):
        self.page.get_by_placeholder("请输入菜单名称").fill(name)
        self.page.get_by_role("button", name="搜索").click()

    def reset_search(self):
        self.page.get_by_role("button", name="重置").click()

    def add(self, name, menu_type="菜单"):
        """新增菜单。menu_type: 目录/菜单/按钮。"""
        self.page.get_by_role("button", name="新增").click()
        dialog = self.visible_dialog()
        self.form_item_input(dialog, "菜单名称").fill(name)
        dialog.get_by_text(menu_type, exact=True).click()
        self.form_item_input(dialog, "显示排序").fill("1")
        if menu_type in ("目录", "菜单"):
            self.form_item_input(dialog, "路由地址").fill(name.replace("_", ""))
        self.dialog_submit()

    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def open_add_dialog(self):
        return self.open_create_dialog()

    def add_dialog_has_required_fields(self):
        dialog = self.open_add_dialog()
        return (
            dialog.get_by_text("菜单名称").is_visible()
            and dialog.get_by_text("菜单类型").is_visible()
        )

    def has_operation(self, operation):
        return self.page.get_by_role("button", name=operation).count() > 0

    def text_exists(self, text):
        return self.page.get_by_text(text, exact=True).count() > 0

    def delete_row(self, keyword):
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="删除").click()
        self.messagebox_confirm()
