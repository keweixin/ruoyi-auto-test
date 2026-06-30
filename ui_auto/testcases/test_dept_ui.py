"""部门管理 UI 测试用例。

覆盖 DEPT_UI_001 ~ 007：
- 进入页面/新增/查询/编辑/禁用/启用/删除

学习重点：树形结构、上级部门选择、状态切换。
"""
import allure
import pytest

from common.config import cfg
from common.random_utils import gen_name
from ui_auto.pages.dept_page import DeptPage


@allure.feature("部门管理 UI")
class TestDeptUi:

    @allure.title("DEPT_UI_001 进入部门管理页面成功")
    def test_open_dept_page(self, page):
        dp = DeptPage(page)
        dp.open_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("DEPT_UI_002 新增部门成功")
    def test_add_dept(self, page):
        dp = DeptPage(page)
        dp.open_page()
        name = gen_name("auto_dept")
        dp.add(name)
        dp.expect_toast("成功")
        dp.search_by_name(name)
        assert dp.row_exists(name), "新增后表格未查到"

    @allure.title("DEPT_UI_003 按部门名称查询成功")
    def test_search_dept(self, page):
        dp = DeptPage(page)
        dp.open_page()
        dp.search_by_name("研发部")  # 若依自带部门
        assert dp.table_row_count() >= 1

    @allure.title("DEPT_UI_004 编辑部门名称成功")
    def test_edit_dept(self, page):
        dp = DeptPage(page)
        dp.open_page()
        name = gen_name("auto_dept")
        dp.add(name)
        dp.search_by_name(name)
        row = dp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("button", name="修改").click()
        dialog = dp.page.locator(".el-dialog").first
        dept_name = dialog.get_by_label("部门名称")
        dept_name.fill("")
        dept_name.fill(gen_name("auto_edited"))
        dialog.get_by_role("button", name="确 定").click()
        dp.expect_toast("成功")

    @allure.title("DEPT_UI_005 禁用部门成功")
    def test_disable_dept(self, page):
        dp = DeptPage(page)
        dp.open_page()
        name = gen_name("auto_dept")
        dp.add(name)
        dp.search_by_name(name)
        row = dp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("switch").click()
        dp.expect_toast("成功")

    @allure.title("DEPT_UI_006 启用部门成功")
    def test_enable_dept(self, page):
        dp = DeptPage(page)
        dp.open_page()
        name = gen_name("auto_dept")
        dp.add(name)
        dp.search_by_name(name)
        row = dp.page.locator(".el-table__row").filter(has_text=name)
        row.get_by_role("switch").click()
        row.get_by_role("switch").click()
        dp.expect_toast("成功")

    @allure.title("DEPT_UI_007 删除部门成功")
    def test_delete_dept(self, page):
        dp = DeptPage(page)
        dp.open_page()
        name = gen_name("auto_dept")
        dp.add(name)
        dp.search_by_name(name)
        dp.delete_row(name)
        dp.expect_toast("成功")
