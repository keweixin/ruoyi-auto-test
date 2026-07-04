"""真实 UI 操作用例（REAL 系列）。

与 *_UI_005 等用例的区别：
- *_UI_005 等：API 造数 + UI 查询验证（聚焦查询/展示）
- *_UI_REAL_*：真正通过 UI 完成新增/编辑/状态切换操作 + UI 断言（聚焦表单交互）

造数与清理仍用 API，保证用例幂等可重复；中间的"操作"和"断言"完全走 UI。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok
from common.random_utils import gen_name, gen_mobile, gen_username
from common.db_utils import query_one
from ui_auto.pages.dict_page import DictPage
from ui_auto.pages.role_page import RolePage
from ui_auto.pages.user_page import UserPage


@allure.feature("真实 UI 操作")
@pytest.mark.ui
class TestRealUiOps:
    """通过 UI 完成真实增/改/状态切换操作的用例。"""

    # ------------------------------------------------------------------
    # 字典：通过 UI 新增 / 编辑字典类型
    # ------------------------------------------------------------------
    @allure.title("DICT_UI_REAL_001 通过 UI 新增字典类型")
    def test_dict_ui_real_add(self, page, dict_client):
        """UI 点击新增 → 填表单 → 提交 → 断言表格出现新数据 → API 清理。"""
        name = gen_name("auto_dict_real")
        type_ = gen_name("auto_type_real")
        try:
            dp = DictPage(page)
            dp.open_type_page()
            with allure.step("UI 点击新增并填写字典名称/类型后提交"):
                dp.add_type(name, type_)
            with allure.step("UI 搜索并断言表格出现新增的字典类型"):
                dp.search_by_name(name)
                assert dp.row_exists(name), "UI 新增后表格未查到该字典类型"
        finally:
            _safe_delete_dict_type(dict_client, type_)

    @allure.title("DICT_UI_REAL_002 通过 UI 编辑字典类型")
    def test_dict_ui_real_edit(self, page, dict_client):
        """API 造数 → UI 编辑名称 → 断言表格出现新名称 → API 清理。"""
        name = gen_name("auto_dict_real")
        type_ = gen_name("auto_type_real")
        body = dict_client.create_type({"name": name, "type": type_, "status": 0}).json()
        assert_api_ok(body, "API 造字典类型")
        new_name = gen_name("auto_edited_real")
        try:
            dp = DictPage(page)
            dp.open_type_page()
            with allure.step("UI 点击修改并把字典名称改为新值"):
                dp.edit_row(name, new_name=new_name)
            with allure.step("UI 搜索并断言表格出现编辑后的新名称"):
                dp.search_by_name(new_name)
                assert dp.row_exists(new_name), "UI 编辑后表格未查到新名称"
        finally:
            _safe_delete_dict_type(dict_client, type_)

    # ------------------------------------------------------------------
    # 角色：通过 UI 新增角色
    # ------------------------------------------------------------------
    @allure.title("ROLE_UI_REAL_001 通过 UI 新增角色")
    def test_role_ui_real_add(self, page, role_client):
        """UI 点击新增 → 填角色名/标识/顺序 → 提交 → 断言表格出现新角色 → API 清理。"""
        name = gen_name("auto_role_real")
        code = gen_name("auto_code_real")
        try:
            rp = RolePage(page)
            rp.open_page()
            with allure.step("UI 点击新增并填写角色名称/标识/顺序后提交"):
                rp.add(name, code)
            with allure.step("UI 搜索并断言表格出现新增的角色"):
                rp.search_by_name(name)
                assert rp.row_exists(name), "UI 新增后表格未查到该角色"
        finally:
            _safe_delete_role(role_client, name)

    # ------------------------------------------------------------------
    # 用户：通过 UI 修改用户状态（启用→禁用）
    # ------------------------------------------------------------------
    @allure.title("USER_UI_REAL_001 通过 UI 修改用户状态")
    def test_user_ui_real_toggle_status(self, page, user_client):
        """API 造用户 → UI 切换状态开关 → 断言开关状态已变更 → API 清理。"""
        username = gen_username()
        nickname = gen_name("auto_nick_real")
        # API 造用户（新增用户 UI 表单较复杂，造数用 API；状态切换用 UI）
        body = user_client.create({
            "username": username, "password": "Test123456",
            "nickname": nickname, "mobile": gen_mobile(), "deptId": 100,
        }).json()
        assert_api_ok(body, "API 造用户")
        uid = body["data"]
        try:
            up = UserPage(page)
            up.open_page()
            up.search_by_username(username)
            with allure.step("断言新建用户初始状态为启用"):
                before = up.is_enabled(username)
                assert before is True, "新建用户初始状态应为启用"
            with allure.step("UI 点击状态开关切换为禁用"):
                # 点击 switch 后 RuoYi 弹出二次确认框，需点“确定”
                up.toggle_status(username)
                up.messagebox_confirm()
                # 等待列表刷新
                up.page.wait_for_timeout(1000)
            with allure.step("断言切换后用户状态为禁用"):
                up.search_by_username(username)
                after = up.is_enabled(username)
                assert after is False, "切换后用户状态应为禁用"
        finally:
            _safe_delete_user(user_client, uid)


# ----------------------------------------------------------------------
# 清理辅助：API 删除，失败仅告警不阻断用例
# ----------------------------------------------------------------------
def _safe_delete_dict_type(dict_client, type_):
    """按 type 查 DB 拿 id 再调 API 删除。"""
    try:
        row = query_one("SELECT id FROM system_dict_type WHERE type=%s", (type_,))
        if row:
            dict_client.delete_type(row["id"])
    except Exception:
        pass


def _safe_delete_role(role_client, name):
    """按 name 分页查角色 id 再调 API 删除。"""
    try:
        body = role_client.page({"name": name, "pageNo": 1, "pageSize": 10}).json()
        rows = (body.get("data") or {}).get("list") or []
        for r in rows:
            if r.get("name") == name:
                role_client.delete(r["id"])
    except Exception:
        pass


def _safe_delete_user(user_client, uid):
    try:
        user_client.delete(uid)
    except Exception:
        pass
