"""部门管理 UI 测试用例（Vue3 / Element Plus）。

策略：复杂弹窗造数优先由 API 完成，UI 层验证页面打开、搜索、展示与删除确认等用户可见行为。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok, assert_not_found
from common.random_utils import gen_name
from common.test_data import create_dept
from ui_auto.pages.dept_page import DeptPage


@allure.feature("部门管理 UI")
@pytest.mark.ui
class TestDeptUi:

    def _create_dept(self, dept_client, status=0):
        """辅助：创建测试部门，返回 (dept_id, name)。复用 common.test_data.create_dept。"""
        ent = create_dept(dept_client, status=status)
        return ent.id, ent.name

    @allure.title("DEPT_UI_001 进入部门管理页面成功")
    def test_open_dept_page(self, page):
        dp = DeptPage(page)
        dp.open_page()
        assert dp.is_table_visible()

    @allure.title("DEPT_UI_002 新增部门后页面可查询")
    def test_add_dept(self, page, dept_client):
        dept_id, name = self._create_dept(dept_client)
        try:
            dp = DeptPage(page)
            dp.open_page()
            dp.search_by_name(name)
            assert dp.row_exists(name), "新增后表格未查到"
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_UI_003 按部门名称查询成功")
    def test_search_dept(self, page, dept_client):
        dept_id, name = self._create_dept(dept_client)
        try:
            dp = DeptPage(page)
            dp.open_page()
            dp.search_by_name(name)
            assert dp.table_row_count() >= 1
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_UI_004 编辑部门名称后页面可查询")
    def test_edit_dept(self, page, dept_client):
        dept_id, name = self._create_dept(dept_client)
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(dept_client.update({"id": dept_id, "name": new_name, "parentId": 0, "sort": 1, "status": 0}).json())
            dp = DeptPage(page)
            dp.open_page()
            dp.search_by_name(new_name)
            assert dp.row_exists(new_name)
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_UI_005 禁用部门后页面展示关闭")
    def test_disable_dept(self, page, dept_client):
        dept_id, name = self._create_dept(dept_client)
        try:
            assert_api_ok(dept_client.update({"id": dept_id, "name": name, "parentId": 0, "sort": 1, "status": 1}).json())
            dp = DeptPage(page)
            dp.open_page()
            dp.search_by_name(name)
            assert "关闭" in dp.table_row_by_keyword(name).inner_text()
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_UI_006 启用部门后页面展示开启")
    def test_enable_dept(self, page, dept_client):
        dept_id, name = self._create_dept(dept_client, status=1)
        try:
            assert_api_ok(dept_client.update({"id": dept_id, "name": name, "parentId": 0, "sort": 1, "status": 0}).json())
            dp = DeptPage(page)
            dp.open_page()
            dp.search_by_name(name)
            assert "开启" in dp.table_row_by_keyword(name).inner_text()
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_UI_007 删除部门成功")
    def test_delete_dept(self, page, dept_client):
        dept_id, name = self._create_dept(dept_client)
        dp = DeptPage(page)
        dp.open_page()
        dp.search_by_name(name)
        dp.delete_row(name)
        dp.expect_toast("成功")
        body = dept_client.get(dept_id).json()
        assert_not_found(body)
