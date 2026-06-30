"""岗位管理 UI 测试用例。

覆盖 POST_UI_001 ~ 007：
- 进入页面/新增/查询/编辑/禁用/启用/删除

学习重点：普通表格 CRUD、状态切换。
"""
import allure
import pytest

from common.config import cfg
from common.random_utils import gen_name
from ui_auto.pages.post_page import PostPage


@allure.feature("岗位管理 UI")
class TestPostUi:

    @allure.title("POST_UI_001 进入岗位管理页面成功")
    def test_open_post_page(self, page):
        pp = PostPage(page)
        pp.open_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("POST_UI_002 新增岗位成功")
    def test_add_post(self, page):
        pp = PostPage(page)
        pp.open_page()
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        pp.add(name, code)
        pp.expect_toast("成功")
        pp.search_by_name(name)
        assert pp.row_exists(name)

    @allure.title("POST_UI_003 按岗位名称查询成功")
    def test_search_post(self, page):
        pp = PostPage(page)
        pp.open_page()
        pp.search_by_name("CEO")
        assert pp.table_row_count() >= 1

    @allure.title("POST_UI_004 编辑岗位成功")
    def test_edit_post(self, page):
        pp = PostPage(page)
        pp.open_page()
        name = gen_name("auto_post")
        pp.add(name, gen_name("auto_code"))
        pp.search_by_name(name)
        row = pp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("button", name="修改").click()
        dialog = pp.page.locator(".el-dialog").first
        n = dialog.get_by_label("岗位名称")
        n.fill("")
        n.fill(gen_name("auto_edited"))
        dialog.get_by_role("button", name="确 定").click()
        pp.expect_toast("成功")

    @allure.title("POST_UI_005 禁用岗位成功")
    def test_disable_post(self, page):
        pp = PostPage(page)
        pp.open_page()
        name = gen_name("auto_post")
        pp.add(name, gen_name("auto_code"))
        pp.search_by_name(name)
        row = pp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("switch").click()
        pp.expect_toast("成功")

    @allure.title("POST_UI_006 启用岗位成功")
    def test_enable_post(self, page):
        pp = PostPage(page)
        pp.open_page()
        name = gen_name("auto_post")
        pp.add(name, gen_name("auto_code"))
        pp.search_by_name(name)
        row = pp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("switch").click()
        row.get_by_role("switch").click()
        pp.expect_toast("成功")

    @allure.title("POST_UI_007 删除岗位成功")
    def test_delete_post(self, page):
        pp = PostPage(page)
        pp.open_page()
        name = gen_name("auto_post")
        pp.add(name, gen_name("auto_code"))
        pp.search_by_name(name)
        pp.delete_row(name)
        pp.expect_toast("成功")
