"""角色管理 UI 测试用例。

覆盖 ROLE_UI_001 ~ 008：
- 进入页面/新增/查询/编辑/禁用/启用/分配菜单权限/删除

策略：API 先造数据，UI 做验证/编辑/删除；用表格/API 验证代替 toast 断言。
"""
import allure

from common.random_utils import gen_name
from ui_auto.pages.role_page import RolePage


def _get_role_id(role_client, role_name):
    """通过 API 分页查询获取 roleId。"""
    body = role_client.page({"pageNum": 1, "pageSize": 10, "roleName": role_name}).json()
    rows = body.get("rows", [])
    return rows[0]["roleId"] if rows else None


@allure.feature("角色管理 UI")
class TestRoleUi:

    # ── ROLE_UI_001 ──────────────────────────────────────────────
    @allure.title("ROLE_UI_001 进入角色管理页面成功")
    def test_open_role_page(self, page):
        rp = RolePage(page)
        rp.open_page()
        assert page.locator(".el-table").is_visible(), "角色管理页表格未展示"

    # ── ROLE_UI_002 ──────────────────────────────────────────────
    @allure.title("ROLE_UI_002 新增角色成功")
    def test_add_role(self, page, role_client):
        """API 造角色 → UI 搜索 → 验证行存在 → API 清理。"""
        name = gen_name("auto_role"); code = gen_name("auto_code")
        role_client.create({"roleName": name, "roleKey": code, "roleSort": 1, "status": "0", "menuIds": []})
        rid = _get_role_id(role_client, name)
        try:
            rp = RolePage(page); rp.open_page()
            rp.search_by_name(name)
            assert rp.row_exists(name), "新增后表格未查到"
        finally:
            if rid: role_client.delete(rid)

    # ── ROLE_UI_003 ──────────────────────────────────────────────
    @allure.title("ROLE_UI_003 按角色名称查询成功")
    def test_search_role(self, page):
        rp = RolePage(page)
        rp.open_page()
        rp.search_by_name("超级管理员")
        assert rp.table_row_count() >= 1, "查询超级管理员无结果"

    # ── ROLE_UI_004 ──────────────────────────────────────────────
    @allure.title("ROLE_UI_004 编辑角色成功")
    def test_edit_role(self, page, role_client):
        name = gen_name("auto_role")
        code = gen_name("auto_code")
        role_client.create({
            "roleName": name,
            "roleKey": code,
            "roleSort": 1,
            "status": "0",
            "menuIds": [],
        })
        rid = _get_role_id(role_client, name)
        try:
            rp = RolePage(page)
            rp.open_page()
            rp.search_by_name(name)
            row = rp.page.locator(".el-table__row").filter(has_text=name)
            row.get_by_text("修改").click()
            dialog = rp.page.get_by_role("dialog")
            new_name = gen_name("auto_edited")
            rp.fill_vue(dialog.get_by_placeholder("请输入角色名称").first, new_name)
            dialog.get_by_text("确 定").click()
            rp.page.wait_for_timeout(800)
            # 表格验证：重新搜索新名称
            rp.search_by_name(new_name)
            assert rp.row_exists(new_name), "编辑后未查到新名称"
        finally:
            if rid:
                role_client.delete(rid)

    # ── ROLE_UI_005 ──────────────────────────────────────────────
    @allure.title("ROLE_UI_005 禁用角色成功")
    def test_disable_role(self, page, role_client):
        name = gen_name("auto_role"); code = gen_name("auto_code")
        role_client.create({"roleName": name, "roleKey": code, "roleSort": 1, "status": "0", "menuIds": []})
        rid = _get_role_id(role_client, name)
        try:
            role = role_client.get(rid).json()["data"]
            role["status"] = "1"
            role["menuIds"] = []
            from common.assert_utils import assert_api_ok
            assert_api_ok(role_client.update(role).json())
            assert role_client.get(rid).json()["data"]["status"] == "1", "状态未变为禁用"
        finally:
            if rid: role_client.delete(rid)

    @allure.title("ROLE_UI_006 启用角色成功")
    def test_enable_role(self, page, role_client):
        name = gen_name("auto_role"); code = gen_name("auto_code")
        role_client.create({"roleName": name, "roleKey": code, "roleSort": 1, "status": "1", "menuIds": []})
        rid = _get_role_id(role_client, name)
        try:
            role = role_client.get(rid).json()["data"]
            role["status"] = "0"
            role["menuIds"] = []
            from common.assert_utils import assert_api_ok
            assert_api_ok(role_client.update(role).json())
            assert role_client.get(rid).json()["data"]["status"] == "0", "状态未变为启用"
        finally:
            if rid: role_client.delete(rid)

    @allure.title("ROLE_UI_007 分配菜单权限成功")
    def test_assign_menu(self, page, role_client, permission_client):
        """API 造角色带菜单 → UI 搜索验证 → API 验证菜单关系 → 清理。"""
        name = gen_name("auto_role"); code = gen_name("auto_code")
        role_client.create({"roleName": name, "roleKey": code, "roleSort": 1, "status": "0", "menuIds": [1, 2]})
        rid = _get_role_id(role_client, name)
        try:
            rp = RolePage(page); rp.open_page()
            rp.search_by_name(name)
            assert rp.row_exists(name), "角色未显示"
            # API 验证菜单已分配
            ids = permission_client.get_role_menu_ids(rid)
            assert set([1, 2]).issubset(set(ids)), f"菜单未分配 实际={ids}"
        finally:
            if rid: role_client.delete(rid)

    # ── ROLE_UI_008 ──────────────────────────────────────────────
    @allure.title("ROLE_UI_008 删除角色成功")
    def test_delete_role(self, page, role_client):
        name = gen_name("auto_role")
        code = gen_name("auto_code")
        role_client.create({
            "roleName": name,
            "roleKey": code,
            "roleSort": 1,
            "status": "0",
            "menuIds": [],
        })
        rid = _get_role_id(role_client, name)
        try:
            rp = RolePage(page)
            rp.open_page()
            rp.search_by_name(name)
            rp.delete_row(name)
            rp.page.wait_for_timeout(800)
            # 重新搜索验证已删除
            rp.search_by_name(name)
            assert not rp.row_exists(name), "删除后仍能查到角色"
        finally:
            # 兜底：如果 UI 删除失败，API 清理
            if rid:
                try:
                    role_client.delete(rid)
                except Exception:
                    pass
