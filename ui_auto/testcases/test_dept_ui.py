"""部门管理 UI 测试用例（原版 element-ui，全语义化定位）。

原版特点：
- 表格无 switch 组件，状态是文本"正常"/"停用"
- 禁用/启用通过"修改"弹窗里的状态单选框切换
- 按钮用 get_by_role("button", name="修改"/"删除")
"""
import allure
from common.random_utils import gen_name
from ui_auto.pages.dept_page import DeptPage

@allure.feature("部门管理 UI")
class TestDeptUi:

    @allure.title("DEPT_UI_001 进入部门管理页面成功")
    def test_open_dept_page(self, page):
        dp = DeptPage(page); dp.open_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("DEPT_UI_002 新增部门成功")
    def test_add_dept(self, page, dept_client):
        name = gen_name("auto_dept")
        dept_client.create({"parentId": 100, "deptName": name, "orderNum": 1, "status": "0"})
        rows = dept_client.list({"deptName": name}).json()["data"]
        dept_id = rows[0]["deptId"] if rows else None
        try:
            dp = DeptPage(page); dp.open_page()
            dp.search_by_name(name)
            assert dp.row_exists(name), "新增后表格未查到"
        finally:
            if dept_id:
                dept_client.delete(dept_id)

    @allure.title("DEPT_UI_003 按部门名称查询成功")
    def test_search_dept(self, page):
        dp = DeptPage(page); dp.open_page()
        dp.search_by_name("研发部")
        assert dp.table_row_count() >= 1

    @allure.title("DEPT_UI_004 编辑部门名称成功")
    def test_edit_dept(self, page, dept_client):
        name = gen_name("auto_dept")
        dept_client.create({"parentId": 100, "deptName": name, "orderNum": 1, "status": "0"})
        rows = dept_client.list({"deptName": name}).json()["data"]
        dept_id = rows[0]["deptId"]
        try:
            dp = DeptPage(page); dp.open_page()
            dp.search_by_name(name)
            new_name = gen_name("auto_edited")
            dp.page.locator(".el-table__row").filter(has_text=name).get_by_role("button", name="修改").click()
            dialog = dp.page.get_by_role("dialog")
            inp = dialog.get_by_placeholder("请输入部门名称")
            inp.fill("")
            inp.fill(new_name)
            dialog.get_by_text("确 定").click()
            dialog.wait_for(state="hidden", timeout=5000)
            dp.search_by_name(new_name)
            assert dp.row_exists(new_name), "编辑后未查到新名称"
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_UI_005 禁用部门成功")
    def test_disable_dept(self, page, dept_client):
        """API 建部门 → UI 修改弹窗切停用 → API get 验证 status=1。"""
        name = gen_name("auto_dept")
        dept_client.create({"parentId": 100, "deptName": name, "orderNum": 1, "status": "0"})
        rows = dept_client.list({"deptName": name}).json()["data"]
        dept_id = rows[0]["deptId"]
        try:
            dp = DeptPage(page); dp.open_page()
            dp.search_by_name(name)
            # 点修改 → 弹窗内选"停用"单选 → 确定
            dp.page.locator(".el-table__row").filter(has_text=name).get_by_role("button", name="修改").click()
            dialog = dp.page.get_by_role("dialog")
            dialog.get_by_text("停用").click()
            dialog.get_by_text("确 定").click()
            dialog.wait_for(state="hidden", timeout=5000)
            # API 验证
            dept = dept_client.get(dept_id).json()
            assert dept["data"]["status"] == "1", f"状态未变为禁用: {dept}"
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_UI_006 启用部门成功")
    def test_enable_dept(self, page, dept_client):
        """API 建部门(status=1) → UI 修改弹窗切正常 → API get 验证 status=0。"""
        name = gen_name("auto_dept")
        dept_client.create({"parentId": 100, "deptName": name, "orderNum": 1, "status": "1"})
        rows = dept_client.list({"deptName": name}).json()["data"]
        dept_id = rows[0]["deptId"]
        try:
            dp = DeptPage(page); dp.open_page()
            dp.search_by_name(name)
            dp.page.locator(".el-table__row").filter(has_text=name).get_by_role("button", name="修改").click()
            dialog = dp.page.get_by_role("dialog")
            dialog.get_by_text("正常").click()
            dialog.get_by_text("确 定").click()
            dialog.wait_for(state="hidden", timeout=5000)
            dept = dept_client.get(dept_id).json()
            assert dept["data"]["status"] == "0", f"状态未变为启用: {dept}"
        finally:
            dept_client.delete(dept_id)

    @allure.title("DEPT_UI_007 删除部门成功")
    def test_delete_dept(self, page, dept_client):
        name = gen_name("auto_dept")
        dept_client.create({"parentId": 100, "deptName": name, "orderNum": 1, "status": "0"})
        rows = dept_client.list({"deptName": name}).json()["data"]
        dept_id = rows[0]["deptId"]
        try:
            dp = DeptPage(page); dp.open_page()
            dp.search_by_name(name)
            dp.delete_row(name)
            dp.page.wait_for_timeout(800)
            dp.search_by_name(name)
            assert not dp.row_exists(name), "删除后仍能查到"
        finally:
            try:
                dept_client.delete(dept_id)
            except Exception:
                pass
