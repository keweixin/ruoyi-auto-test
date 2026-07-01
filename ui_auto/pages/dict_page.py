"""DictPage：字典管理页 Page Object（原版 RuoYi element-ui）。

定位策略（全语义化，不用 CSS/XPath）：
- 弹窗：get_by_role("dialog")
- 弹窗 input：dialog.get_by_placeholder("...")
- 按钮：get_by_text("新增") / get_by_role("button", name="修改")
- 表格行：.el-table__row（无语义替代，唯一例外）
"""
from ui_auto.base.base_page import BasePage
from common.config import cfg


class DictPage(BasePage):

    TYPE_URL = "/system/dict"
    DATA_URL = "/system/dict-data/index"  # 原版字典数据路由

    def open_type_page(self):
        self.open(cfg.web_url + self.TYPE_URL)
        self.page.locator(".el-table__row").first.wait_for(state="visible", timeout=10000)

    def open_data_page(self, dict_id):
        """打开字典数据页。原版路由 /system/dict-data/index/:dictId。
        新建字典类型可能无数据，等 .el-table 而非 .el-table__row。"""
        self.open(f"{cfg.web_url}{self.DATA_URL}/{dict_id}")
        self.page.wait_for_timeout(2000)
        self.page.locator(".el-table").first.wait_for(state="visible", timeout=10000)

    # ===== 查询 =====
    def search_by_name(self, name):
        self.page.get_by_placeholder("请输入字典名称").first.fill(name)
        self.page.get_by_text("搜索").first.click()

    def search_by_type(self, type_):
        self.page.get_by_placeholder("请输入字典类型").fill(type_)
        self.page.get_by_text("搜索").first.click()

    def reset_search(self):
        self.page.get_by_text("重置").first.click()

    # ===== 新增 =====
    def add_type(self, name, type_):
        self.page.get_by_text("新增").first.click()
        dialog = self.page.get_by_role("dialog")
        dialog.get_by_placeholder("请输入字典名称").fill(name)
        dialog.get_by_placeholder("请输入字典类型").fill(type_)
        dialog.get_by_text("确 定").click()
        dialog.wait_for(state="hidden", timeout=5000)

    # ===== 操作表格行 =====
    def row_exists(self, keyword):
        return self.table_has_row(keyword)

    def edit_row(self, keyword, new_name=None):
        """编辑某行。"""
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="修改").click()
        dialog = self.page.get_by_role("dialog")
        if new_name:
            inp = dialog.get_by_placeholder("请输入字典名称")
            inp.fill("")
            inp.fill(new_name)
        dialog.get_by_text("确 定").click()
        dialog.wait_for(state="hidden", timeout=5000)

    def delete_row(self, keyword):
        """删除某行（含确认框）。原版确认框按钮文本是"确定"无空格。"""
        self.safe_auto_keyword(keyword)
        row = self.table_row_by_keyword(keyword)
        row.get_by_role("button", name="删除").click()
        confirm = self.page.locator(".el-message-box")
        confirm.get_by_text("确定").click()
