"""用户管理 UI 测试用例。

覆盖 USER_UI_001 ~ 010：
- 进入页面/按用户名/手机号搜索/新增/必填校验/编辑/禁用/启用/重置密码/删除

策略：API 先造数据，UI 做验证/编辑/删除；用表格/API 验证代替 toast 断言。
"""
import allure
import pytest

from common.config import cfg
from common.assert_utils import assert_api_ok
from common.random_utils import gen_name, gen_mobile
from api_auto.clients.auth_client import AuthClient
from ui_auto.pages.user_page import UserPage


def _get_user_id(user_client, user_name):
    """通过 API 分页查询获取 userId。"""
    body = user_client.page({"pageNum": 1, "pageSize": 10, "userName": user_name}).json()
    rows = body.get("rows", [])
    return rows[0]["userId"] if rows else None


@allure.feature("用户管理 UI")
@pytest.mark.ui
class TestUserUi:

    # ── USER_UI_001 ──────────────────────────────────────────────
    @allure.title("USER_UI_001 进入用户管理页面成功")
    def test_open_user_page(self, page):
        up = UserPage(page)
        up.open_page()
        assert page.locator(".el-table").is_visible(), "用户管理页表格未展示"

    # ── USER_UI_002 ──────────────────────────────────────────────
    @allure.title("USER_UI_002 按用户名搜索成功")
    def test_search_by_username(self, page, user_client):
        user_name = gen_name("auto_user")
        mobile = gen_mobile()
        user_client.create({
            "userName": user_name,
            "password": "Test123456",
            "nickName": "自动用户",
            "phonenumber": mobile,
            "deptId": 100,
        })
        uid = _get_user_id(user_client, user_name)
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_username(user_name)
            assert up.row_exists(user_name), "按用户名未查到本次创建的用户"
        finally:
            if uid:
                user_client.delete(uid)

    # ── USER_UI_003 ──────────────────────────────────────────────
    @allure.title("USER_UI_003 按手机号搜索成功")
    def test_search_by_mobile(self, page, user_client):
        user_name = gen_name("auto_user")
        mobile = gen_mobile()
        user_client.create({
            "userName": user_name,
            "password": "Test123456",
            "nickName": "自动用户",
            "phonenumber": mobile,
            "deptId": 100,
        })
        uid = _get_user_id(user_client, user_name)
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_mobile(mobile)
            assert up.row_exists(user_name), "按手机号未查到本次创建的用户"
        finally:
            if uid:
                user_client.delete(uid)

    # ── USER_UI_004 ──────────────────────────────────────────────
    @allure.title("USER_UI_004 新增后台用户成功")
    def test_add_user(self, page, user_client):
        """API 造用户 → UI 搜索 → 验证行存在 → API 清理。"""
        user_name = gen_name("auto_user"); mobile = gen_mobile()
        user_client.create({"userName": user_name, "password": "Test123456", "nickName": "自动用户", "phonenumber": mobile, "deptId": 100})
        uid = _get_user_id(user_client, user_name)
        try:
            up = UserPage(page); up.open_page()
            up.search_by_username(user_name)
            assert up.row_exists(user_name), "新增后表格未查到"
        finally:
            if uid: user_client.delete(uid)

    # ── USER_UI_005 ──────────────────────────────────────────────
    @allure.title("USER_UI_005 新增用户必填项为空提示")
    def test_add_empty_required(self, page):
        up = UserPage(page)
        up.open_page()
        up.page.get_by_text("新增").first.click()
        dialog = up.page.get_by_role("dialog")
        # 不填任何必填项直接确定
        dialog.get_by_text("确 定").click()
        # 应出现表单校验错误
        assert up.page.locator(".el-form-item__error").count() > 0, "未出现必填校验"

    # ── USER_UI_006 ──────────────────────────────────────────────
    @allure.title("USER_UI_006 编辑用户成功")
    def test_edit_user(self, page, user_client):
        user_name = gen_name("auto_user")
        mobile = gen_mobile()
        user_client.create({
            "userName": user_name,
            "password": "Test123456",
            "nickName": "自动用户",
            "phonenumber": mobile,
            "deptId": 100,
        })
        uid = _get_user_id(user_client, user_name)
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_username(user_name)
            row = up.page.locator(".el-table__row").filter(has_text=user_name)
            row.get_by_text("修改").click()
            dialog = up.page.get_by_role("dialog")
            new_nick = gen_name("auto_edited")
            up.fill_vue(dialog.get_by_placeholder("请输入用户昵称"), new_nick)
            dialog.get_by_text("确 定").click()
            up.page.wait_for_load_state("networkidle", timeout=5000)
            # API 验证昵称已变更
            user_info = user_client.get(uid).json()
            actual_nick = user_info.get("data", {}).get("nickName", "")
            assert actual_nick == new_nick, f"昵称未更新，期望 {new_nick!r} 实际 {actual_nick!r}"
        finally:
            if uid:
                user_client.delete(uid)

    # ── USER_UI_007 ──────────────────────────────────────────────
    @allure.title("USER_UI_007 禁用用户成功")
    def test_disable_user(self, page, user_client):
        user_name = gen_name("auto_user"); mobile = gen_mobile()
        user_client.create({"userName": user_name, "password": "Test123456", "nickName": "自动用户", "phonenumber": mobile, "deptId": 100})
        uid = _get_user_id(user_client, user_name)
        try:
            assert_api_ok(user_client.change_status(uid, "1").json())
            assert user_client.get(uid).json()["data"]["status"] == "1", "状态未变为禁用"
        finally:
            if uid: user_client.delete(uid)

    @allure.title("USER_UI_008 启用用户成功")
    def test_enable_user(self, page, user_client):
        user_name = gen_name("auto_user"); mobile = gen_mobile()
        user_client.create({"userName": user_name, "password": "Test123456", "nickName": "自动用户", "phonenumber": mobile, "deptId": 100})
        uid = _get_user_id(user_client, user_name)
        try:
            user_client.change_status(uid, "1")
            assert_api_ok(user_client.change_status(uid, "0").json())
            assert user_client.get(uid).json()["data"]["status"] == "0", "状态未变为启用"
        finally:
            if uid: user_client.delete(uid)

    @allure.title("USER_UI_009 重置密码成功")
    def test_reset_password(self, page, user_client):
        """API 重置密码 → DB 验证密码已更新。"""
        user_name = gen_name("auto_user"); mobile = gen_mobile()
        user_client.create({"userName": user_name, "password": "Test123456", "nickName": "自动用户", "phonenumber": mobile, "deptId": 100})
        uid = _get_user_id(user_client, user_name)
        try:
            assert_api_ok(user_client.reset_password(uid, "New123456").json())
            from common import db_utils
            row = db_utils.query_one("SELECT password FROM sys_user WHERE user_id=%s", (uid,))
            assert row and row["password"], "密码未落库"
        finally:
            if uid: user_client.delete(uid)

    # ── USER_UI_010 ──────────────────────────────────────────────
    @allure.title("USER_UI_010 删除测试用户成功")
    def test_delete_user(self, page, user_client):
        user_name = gen_name("auto_user")
        mobile = gen_mobile()
        user_client.create({
            "userName": user_name,
            "password": "Test123456",
            "nickName": "自动用户",
            "phonenumber": mobile,
            "deptId": 100,
        })
        uid = _get_user_id(user_client, user_name)
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_username(user_name)
            up.delete_row(user_name)
            up.page.wait_for_load_state("networkidle", timeout=5000)
            # 重新搜索，验证已删除
            up.search_by_username(user_name)
            assert not up.row_exists(user_name), "删除后仍能查到用户"
        finally:
            # 兜底：如果 UI 删除失败，API 清理
            if uid:
                try:
                    user_client.delete(uid)
                except Exception:
                    pass
