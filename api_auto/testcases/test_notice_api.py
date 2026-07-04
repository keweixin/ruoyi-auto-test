"""通知公告接口测试用例。

覆盖 NOTICE_API_001 ~ 006：
- CRUD（新增/查询/编辑/删除）
- 分页查询按标题筛选
- 删除后查不到

通知公告是标准 CRUD，复用 CrudClient，与 dept/role 等模块测试模式一致。
"""
import allure
import pytest

from common.assert_utils import assert_api_ok, assert_api_fail
from common.random_utils import gen_name
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA
from common.test_data import with_created_entity


@allure.feature("通知公告接口")
@pytest.mark.api
class TestNoticeApi:

    @allure.story("新增")
    @allure.title("NOTICE_API_001 新增通知公告成功")
    @pytest.mark.smoke
    def test_create_notice(self, notice_client):
        title = gen_name("auto_notice")
        body = notice_client.create({
            "title": title, "type": 1, "content": "<p>auto test</p>", "status": 0
        }).json()
        assert_api_ok(body, "新增通知")
        assert body["data"], "未返回 id"
        notice_client.delete(body["data"])

    @allure.story("异常")
    @allure.title("NOTICE_API_002 新增通知标题为空失败")
    def test_create_empty_title(self, notice_client):
        body = notice_client.create({
            "title": "", "type": 1, "content": "x", "status": 0
        }).json()
        assert_api_fail(body, "标题为空")

    @allure.story("查询")
    @allure.title("NOTICE_API_003 分页查询通知公告成功")
    @pytest.mark.smoke
    def test_page_notice(self, notice_client):
        title = gen_name("auto_notice")
        nid = notice_client.create({
            "title": title, "type": 1, "content": "x", "status": 0
        }).json()["data"]
        try:
            body = notice_client.page({"pageNo": 1, "pageSize": 10, "title": title}).json()
            assert_schema(body, PAGE_LIST_SCHEMA)
            assert_api_ok(body)
            rows = body["data"]["list"]
            assert any(r["id"] == nid and r["title"] == title for r in rows), "未查到本次创建的通知"
        finally:
            notice_client.delete(nid)

    @allure.story("修改")
    @allure.title("NOTICE_API_004 编辑通知公告成功")
    def test_update_notice(self, notice_client):
        title = gen_name("auto_notice")
        nid = notice_client.create({
            "title": title, "type": 1, "content": "x", "status": 0
        }).json()["data"]
        try:
            new_title = gen_name("auto_edited")
            body = notice_client.update({
                "id": nid, "title": new_title, "type": 2, "content": "<p>edited</p>", "status": 0
            }).json()
            assert_api_ok(body, "编辑通知")
            # 验证已更新
            detail = notice_client.get(nid).json()["data"]
            assert detail["title"] == new_title, f"标题期望 {new_title}，实际 {detail['title']}"
            assert detail["type"] == 2, f"类型期望 2，实际 {detail['type']}"
        finally:
            notice_client.delete(nid)

    @allure.story("删除")
    @allure.title("NOTICE_API_005 删除通知公告成功")
    def test_delete_notice(self, notice_client):
        title = gen_name("auto_notice")
        nid = notice_client.create({
            "title": title, "type": 1, "content": "x", "status": 0
        }).json()["data"]
        body = notice_client.delete(nid).json()
        assert_api_ok(body, "删除通知")
        # 删除后查不到
        detail = notice_client.get(nid).json()
        assert detail.get("code") != 0 or not detail.get("data"), "删除后不应查到"

    @allure.story("删除")
    @allure.title("NOTICE_API_006 删除不存在的通知公告失败")
    def test_delete_not_found(self, notice_client):
        body = notice_client.delete(999999).json()
        assert_api_fail(body, "删除不存在的通知")
