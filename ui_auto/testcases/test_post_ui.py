"""岗位管理 UI 测试用例。

覆盖 POST_UI_001 ~ 007：
- 进入页面/新增/查询/编辑/禁用/启用/删除

策略：API 造数据 → UI 打开页面 → UI 搜索验证 → API 清理。增删改操作用 API 而非 UI 交互。
"""
import allure

from common.random_utils import gen_name
from common.assert_utils import assert_api_ok
from ui_auto.pages.post_page import PostPage


@allure.feature("岗位管理 UI")
class TestPostUi:

    @allure.title("POST_UI_001 进入岗位管理页面成功")
    def test_open_post_page(self, page):
        pp = PostPage(page)
        pp.open_page()
        assert page.locator(".el-table").is_visible()

    @allure.title("POST_UI_002 新增岗位成功")
    def test_add_post(self, page, post_client):
        """API 造岗位 → UI 搜索 → 验证行存在 → API 清理。"""
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        assert_api_ok(post_client.create({
            "postCode": code, "postName": name, "postSort": 1, "status": "0"
        }).json())
        rows = post_client.page({"pageNum": 1, "pageSize": 10, "postName": name}).json()["rows"]
        pid = rows[0]["postId"] if rows else None
        try:
            pp = PostPage(page)
            pp.open_page()
            pp.search_by_name(name)
            assert pp.row_exists(name), "新增后表格未查到"
        finally:
            if pid:
                post_client.delete(pid)

    @allure.title("POST_UI_003 按岗位名称查询成功")
    def test_search_post(self, page, post_client):
        """API 造岗位 → UI 搜索 → 验证行存在 → API 清理。"""
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        assert_api_ok(post_client.create({"postCode": code, "postName": name, "postSort": 1, "status": "0"}).json())
        try:
            pp = PostPage(page); pp.open_page()
            pp.search_by_name(name)
            assert pp.row_exists(name), "查询未查到本次岗位"
        finally:
            rows = post_client.page({"postName": name}).json()["rows"]
            if rows:
                post_client.delete(rows[0]["postId"])

    @allure.title("POST_UI_004 编辑岗位成功")
    def test_edit_post(self, page, post_client):
        """API 造岗位 → API 编辑名称 → UI 搜索新名称 → 验证 → API 清理。"""
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        assert_api_ok(post_client.create({
            "postCode": code, "postName": name, "postSort": 1, "status": "0"
        }).json())
        rows = post_client.page({"pageNum": 1, "pageSize": 10, "postName": name}).json()["rows"]
        pid = rows[0]["postId"]
        new_name = gen_name("auto_edited")
        try:
            assert_api_ok(post_client.update({
                "postId": pid, "postName": new_name, "postCode": code, "postSort": 1, "status": "0"
            }).json())
            pp = PostPage(page)
            pp.open_page()
            pp.search_by_name(new_name)
            assert pp.row_exists(new_name), "编辑后未查到新名称"
        finally:
            post_client.delete(pid)

    @allure.title("POST_UI_005 禁用岗位成功")
    def test_disable_post(self, page, post_client):
        name = gen_name("auto_post"); code = gen_name("auto_code")
        assert_api_ok(post_client.create({"postCode": code, "postName": name, "postSort": 1, "status": "0"}).json())
        rows = post_client.page({"postName": name}).json()["rows"]
        pid = rows[0]["postId"]
        try:
            # 原版 update 要求完整字段
            assert_api_ok(post_client.update({"postId": pid, "postName": name, "postCode": code, "postSort": 1, "status": "1"}).json())
            assert post_client.get(pid).json()["data"]["status"] == "1", "状态未变为禁用"
        finally:
            post_client.delete(pid)

    @allure.title("POST_UI_006 启用岗位成功")
    def test_enable_post(self, page, post_client):
        name = gen_name("auto_post"); code = gen_name("auto_code")
        assert_api_ok(post_client.create({"postCode": code, "postName": name, "postSort": 1, "status": "1"}).json())
        rows = post_client.page({"postName": name}).json()["rows"]
        pid = rows[0]["postId"]
        try:
            assert_api_ok(post_client.update({"postId": pid, "postName": name, "postCode": code, "postSort": 1, "status": "0"}).json())
            assert post_client.get(pid).json()["data"]["status"] == "0", "状态未变为启用"
        finally:
            post_client.delete(pid)

    @allure.title("POST_UI_007 删除岗位成功")
    def test_delete_post(self, page, post_client):
        """API 造岗位 → UI 搜索验证存在 → API 删除 → UI 搜索验证不存在。"""
        name = gen_name("auto_post")
        code = gen_name("auto_code")
        assert_api_ok(post_client.create({
            "postCode": code, "postName": name, "postSort": 1, "status": "0"
        }).json())
        rows = post_client.page({"pageNum": 1, "pageSize": 10, "postName": name}).json()["rows"]
        pid = rows[0]["postId"]
        pp = PostPage(page)
        pp.open_page()
        pp.search_by_name(name)
        assert pp.row_exists(name), "删除前应能查到"
        assert_api_ok(post_client.delete(pid).json())
        pp.search_by_name(name)
        assert not pp.row_exists(name), "删除后仍能查到"
