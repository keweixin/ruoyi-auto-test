"""UI 操作后接口校验联动测试。

覆盖 4 个场景：UI 新增数据 → 接口查询确认 → 数据库校验 → 接口清理。

价值：体现 UI 操作不是只看页面成功，而是通过接口和数据库验证最终结果。
"""
import allure
import pytest

from common.config import cfg
from common import db_utils
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_text
from common.random_utils import gen_name
from api_auto.clients.dept_client import DeptClient
from api_auto.clients.post_client import PostClient
from ui_auto.pages.dept_page import DeptPage
from ui_auto.pages.post_page import PostPage


@allure.feature("UI操作后接口校验联动")
class TestUiApiDbFlow:

    @allure.title("FLOW_001 UI 新增部门 → 接口查询 → 数据库校验 → 接口清理")
    def test_ui_add_dept_api_db_verify(self, page, admin_token):
        """UI 新增部门 → 接口确认存在 → 数据库校验字段 → 接口清理。"""
        # 1. UI 新增
        dp = DeptPage(page)
        dp.open_page()
        name = gen_name("auto_flow")
        dp.add(name)
        dp.expect_toast("成功")

        # 2. 接口查询确认存在
        api = DeptClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        body = api.list({"name": name}).json()
        assert_api_ok(body)
        target = next((d for d in body["data"] if d["name"] == name), None)
        assert target, "接口未查到 UI 新建的部门"

        # 3. 数据库校验
        row = db_utils.query_one(
            "SELECT name, deleted FROM system_dept WHERE id=%s", (target["id"],)
        )
        assert row and row["name"] == name and row["deleted"] == 0
        attach_text("部门数据库记录", str(row))

        # 4. 接口清理
        api.delete(target["id"])

    @allure.title("FLOW_002 UI 新增岗位 → 接口查询 → 数据库校验 → 接口清理")
    def test_ui_add_post_api_db_verify(self, page, admin_token):
        """UI 新增岗位 → 接口确认 → 数据库校验 → 接口清理。"""
        pp = PostPage(page)
        pp.open_page()
        name = gen_name("auto_flow")
        code = gen_name("auto_code")
        pp.add(name, code)
        pp.expect_toast("成功")

        api = PostClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        body = api.page({"pageNo": 1, "pageSize": 10, "name": name}).json()
        assert_api_ok(body)
        assert body["data"]["total"] >= 1, "接口未查到 UI 新建的岗位"
        target = body["data"]["list"][0]

        row = db_utils.query_one(
            "SELECT name, code, deleted FROM system_post WHERE id=%s", (target["id"],)
        )
        assert row and row["name"] == name and row["deleted"] == 0
        attach_text("岗位数据库记录", str(row))

        api.delete(target["id"])

    @allure.title("FLOW_003 UI 编辑部门 → 接口查询确认修改 → 数据库校验")
    def test_ui_edit_dept_api_db_verify(self, page, admin_token):
        """接口造数 → UI 编辑 → 接口确认 → 数据库校验 → 接口清理。"""
        # 接口造数
        api = DeptClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        name = gen_name("auto_flow")
        new_id = api.create({"name": name, "parentId": 0, "sort": 1, "status": 0}).json()["data"]
        try:
            # UI 编辑
            dp = DeptPage(page)
            dp.open_page()
            dp.search_by_name(name)
            new_name = gen_name("auto_edited")
            row = dp.page.locator(".el-table__row").filter(has_text=name)
            row.get_by_role("button", name="修改").click()
            dialog = dp.page.locator(".el-dialog").first
            dept_name = dialog.get_by_label("部门名称")
            dept_name.fill("")
            dept_name.fill(new_name)
            dialog.get_by_role("button", name="确 定").click()
            dp.expect_toast("成功")

            # 接口确认
            body = api.get(new_id).json()
            assert_api_ok(body)
            assert body["data"]["name"] == new_name, "接口查到的名称未更新"

            # 数据库校验
            row_db = db_utils.query_one("SELECT name FROM system_dept WHERE id=%s", (new_id,))
            assert row_db and row_db["name"] == new_name
            attach_text("编辑后部门数据库记录", str(row_db))
        finally:
            api.delete(new_id)

    @allure.title("FLOW_004 UI 删除部门 → 接口查询确认已删除 → 数据库校验逻辑删除")
    def test_ui_delete_dept_api_db_verify(self, page, admin_token):
        """接口造数 → UI 删除 → 接口确认已删 → 数据库校验逻辑删除。"""
        api = DeptClient(cfg.base_url, cfg.tenant_id)
        api.set_token(admin_token)
        name = gen_name("auto_flow")
        new_id = api.create({"name": name, "parentId": 0, "sort": 1, "status": 0}).json()["data"]

        # UI 删除
        dp = DeptPage(page)
        dp.open_page()
        dp.search_by_name(name)
        dp.delete_row(name)
        dp.expect_toast("成功")

        # 接口确认：再查应查不到或失败
        body = api.get(new_id).json()
        assert body.get("code") != 0 or not body.get("data"), "接口仍能查到已删部门"

        # 数据库校验：逻辑删除 deleted=1
        row = db_utils.query_one("SELECT deleted FROM system_dept WHERE id=%s", (new_id,))
        assert row is None or row["deleted"] == 1, "数据库未标记逻辑删除"
        attach_text("删除后部门数据库记录", str(row))
