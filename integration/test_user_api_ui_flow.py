"""纯接口联动测试：用户（RuoYi-Vue-Pro / yudao）。

覆盖 USER_FLOW_001 ~ 005：
- 接口创建 → 接口查询 → DB 校验 → 清理
- 接口禁用 → 接口登录失败
- 接口启用 → DB 验证状态恢复
- 接口重置密码 → DB 验证密码已更新
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_mobile, gen_username
from api_auto.clients.auth_client import AuthClient
from common.config import cfg


@allure.feature("纯接口联动-用户")
@pytest.mark.flow
class TestUserFlow:

    def _create_user(self, user_client, nickname="联动用户", password="Test123456"):
        username = gen_username()
        uid = user_client.create({
            "username": username,
            "nickname": nickname,
            "password": password,
            "mobile": gen_mobile(),
            "deptId": 100,
        }).json()["data"]
        return uid, username, password

    @allure.title("USER_FLOW_001 接口创建用户 → 接口查询 → DB 校验 → 清理")
    def test_api_create_api_db_verify(self, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            body = user_client.page({"pageNo": 1, "pageSize": 10, "username": username}).json()
            assert_api_ok(body)
            rows = body["data"]["list"]
            assert any(r["id"] == uid for r in rows), "接口未查到造的用户"
            row = db_utils.query_one(
                "SELECT username, deleted + 0 AS deleted FROM system_users WHERE id=%s",
                (uid,),
            )
            assert row and row["username"] == username and row["deleted"] == 0
            attach_text("用户 DB 记录", str(row))
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("USER_FLOW_002 接口创建用户 → 接口分页查询 → DB 校验 → 清理")
    def test_api_create_page_db_verify(self, user_client):
        uid, username, _ = self._create_user(user_client, nickname="分页用户")
        try:
            body = user_client.page({"pageNo": 1, "pageSize": 10, "username": username}).json()
            assert_api_ok(body)
            assert body["data"]["total"] >= 1, "分页接口未查到造的用户"
            row = db_utils.query_one("SELECT username FROM system_users WHERE id=%s", (uid,))
            assert row and row["username"] == username, "DB 未落库"
            attach_text("用户 DB 记录", str(row))
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("USER_FLOW_003 接口禁用用户 → 接口登录失败")
    def test_api_disable_login_fail(self, user_client):
        uid, username, password = self._create_user(user_client, nickname="禁用测试")
        try:
            assert_api_ok(user_client.change_status(uid, 1).json())
            body = AuthClient(cfg.base_url, cfg.tenant_id).login(username, password).json()
            assert_api_fail(body, "禁用用户登录")
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("USER_FLOW_004 接口启用用户 → DB 验证状态")
    def test_api_enable_login_success(self, user_client):
        uid, username, _ = self._create_user(user_client, nickname="启用测试")
        try:
            assert_api_ok(user_client.change_status(uid, 1).json())
            assert_api_ok(user_client.change_status(uid, 0).json())
            row = db_utils.query_one("SELECT status FROM system_users WHERE id=%s", (uid,))
            assert row and row["status"] == 0, "状态未恢复为启用"
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("USER_FLOW_005 接口重置密码 → DB 验证密码已更新")
    def test_api_reset_password_verify(self, user_client):
        uid, username, _ = self._create_user(user_client, nickname="重置测试")
        try:
            old = db_utils.query_one("SELECT password FROM system_users WHERE id=%s", (uid,))
            assert_api_ok(user_client.reset_password(uid, "New123456").json())
            new = db_utils.query_one("SELECT password FROM system_users WHERE id=%s", (uid,))
            assert new and new["password"] and new["password"] != old["password"], "密码未更新"
        finally:
            assert_api_ok(user_client.delete(uid).json())
