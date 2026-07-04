"""岗位管理 UI 测试用例（Vue3 / Element Plus）。

策略：通过 API 构造岗位数据，UI 层验证页面打开、查询、展示和删除确认。避免 UI 表单字段变更导致大量用例不稳定。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok
from common.random_utils import gen_name
from ui_auto.pages.post_page import PostPage


@allure.feature("岗位管理 UI")
@pytest.mark.ui
class TestPostUi:

    def _create_post(self, post_client, status=0):
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        body = post_client.create({"name": name, "code": code, "sort": 1, "status": status}).json()
        assert_api_ok(body, "API 创建岗位")
        return body["data"], name, code

    @allure.title("POST_UI_001 进入岗位管理页面成功")
    def test_open_post_page(self, page):
        pp = PostPage(page)
        pp.open_page()
        assert pp.is_table_visible()

    @allure.title("POST_UI_002 新增岗位后页面可查询")
    def test_add_post(self, page, post_client):
        post_id, name, _ = self._create_post(post_client)
        try:
            pp = PostPage(page)
            pp.open_page()
            pp.search_by_name(name)
            assert pp.row_exists(name)
        finally:
            post_client.delete(post_id)

    @allure.title("POST_UI_003 按岗位名称查询成功")
    def test_search_post(self, page, post_client):
        post_id, name, _ = self._create_post(post_client)
        try:
            pp = PostPage(page)
            pp.open_page()
            pp.search_by_name(name)
            assert pp.row_exists(name)
        finally:
            post_client.delete(post_id)

    @allure.title("POST_UI_004 编辑岗位成功")
    def test_edit_post(self, page, post_client):
        post_id, name, code = self._create_post(post_client)
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(post_client.update({"id": post_id, "name": new_name, "code": code, "sort": 1, "status": 0}).json())
            pp = PostPage(page)
            pp.open_page()
            pp.search_by_name(new_name)
            assert pp.row_exists(new_name)
        finally:
            post_client.delete(post_id)

    @allure.title("POST_UI_005 禁用岗位成功")
    def test_disable_post(self, page, post_client):
        post_id, name, code = self._create_post(post_client)
        try:
            assert_api_ok(post_client.update({"id": post_id, "name": name, "code": code, "sort": 1, "status": 1}).json())
            pp = PostPage(page)
            pp.open_page()
            pp.search_by_name(name)
            assert "关闭" in pp.table_row_by_keyword(name).inner_text()
        finally:
            post_client.delete(post_id)

    @allure.title("POST_UI_006 启用岗位成功")
    def test_enable_post(self, page, post_client):
        post_id, name, code = self._create_post(post_client, status=1)
        try:
            assert_api_ok(post_client.update({"id": post_id, "name": name, "code": code, "sort": 1, "status": 0}).json())
            pp = PostPage(page)
            pp.open_page()
            pp.search_by_name(name)
            assert "开启" in pp.table_row_by_keyword(name).inner_text()
        finally:
            post_client.delete(post_id)

    @allure.title("POST_UI_007 删除岗位成功")
    def test_delete_post(self, page, post_client):
        post_id, name, _ = self._create_post(post_client)
        pp = PostPage(page)
        pp.open_page()
        pp.search_by_name(name)
        pp.delete_row(name)
        pp.expect_toast("成功")
        body = post_client.get(post_id).json()
        assert body.get("code") != 0 or not body.get("data"), "UI 删除后接口仍能查到岗位"
