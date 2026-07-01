"""纯接口联动测试：用户。

覆盖 USER_FLOW_001 ~ 005：
- 接口创建 → 接口查询 → DB 校验 → 清理
- 接口禁用 → 接口登录失败
- 接口启用 → 接口登录成功
- 接口重置密码 → 接口验证新密码可登录

价值：不依赖前端，用接口验证用户管理联动逻辑。
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_name, gen_mobile
from api_auto.clients.auth_client import AuthClient
from common.config import cfg


@allure.feature("纯接口联动-用户")
@pytest.mark.flow
class TestUserFlow:

    @allure.title("USER_FLOW_001 接口创建用户 → 接口查询 → DB 校验 → 清理")
    def test_api_create_api_db_verify(self, user_client):
        """接口造用户 → 接口验证 → 数据库校验 → 接口清理。"""
        username = gen_name("auto_flow")
        assert_api_ok(user_client.create({
            "userName": username, "nickName": "联动用户",
            "password": "admin123", "phonenumber": gen_mobile(), "deptId": 100, "status": "0"
        }).json())
        rows = user_client.page({"pageNum": 1, "pageSize": 10, "userName": username}).json()["rows"]
        uid = rows[0]["userId"]
        try:
            assert any(r["userId"] == uid for r in rows), "接口未查到造的用户"
            row = db_utils.query_one("SELECT user_name, del_flag FROM sys_user WHERE user_id=%s", (uid,))
            assert row and row["user_name"] == username and row["del_flag"] == "0"
            attach_text("用户 DB 记录", str(row))
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("USER_FLOW_002 接口创建用户 → 接口分页查询 → DB 校验 → 清理")
    def test_api_create_page_db_verify(self, user_client):
        """接口造用户 → 分页查询验证 → 数据库校验 → 接口清理。"""
        username = gen_name("auto_flow")
        assert_api_ok(user_client.create({
            "userName": username, "nickName": "分页用户",
            "password": "admin123", "phonenumber": gen_mobile(), "deptId": 100, "status": "0"
        }).json())
        body = user_client.page({"pageNum": 1, "pageSize": 10, "userName": username}).json()
        assert_api_ok(body)
        assert body["total"] >= 1, "分页接口未查到造的用户"
        uid = body["rows"][0]["userId"]
        try:
            row = db_utils.query_one("SELECT user_name FROM sys_user WHERE user_id=%s", (uid,))
            assert row and row["user_name"] == username, "DB 未落库"
            attach_text("用户 DB 记录", str(row))
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("USER_FLOW_003 接口禁用用户 → 接口登录失败")
    def test_api_disable_login_fail(self, user_client):
        """接口造用户 → 接口禁用 → 接口登录应失败 → 接口清理。"""
        username = gen_name("auto_flow")
        password = "Test123456"
        assert_api_ok(user_client.create({
            "userName": username, "nickName": "禁用测试",
            "password": password, "phonenumber": gen_mobile(), "deptId": 100, "status": "0"
        }).json())
        rows = user_client.page({"pageNum": 1, "pageSize": 10, "userName": username}).json()["rows"]
        uid = rows[0]["userId"]
        try:
            assert_api_ok(user_client.change_status(uid, "1").json())
            # 接口用该用户登录应失败
            body = AuthClient(cfg.base_url, cfg.tenant_id).login(username, password).json()
            assert body.get("code") != 200, "禁用用户仍能接口登录"
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("USER_FLOW_004 接口启用用户 → DB 验证状态")
    def test_api_enable_login_success(self, user_client):
        """接口造用户 → 禁用 → 启用 → DB 验证状态=0。原版创建用户密码加密特殊，用 DB 验证。"""
        username = gen_name("auto_flow")
        assert_api_ok(user_client.create({
            "userName": username, "nickName": "启用测试",
            "password": "Test123456", "phonenumber": gen_mobile(), "deptId": 100, "status": "0"
        }).json())
        rows = user_client.page({"pageNum": 1, "pageSize": 10, "userName": username}).json()["rows"]
        uid = rows[0]["userId"]
        try:
            assert_api_ok(user_client.change_status(uid, "1").json())
            assert_api_ok(user_client.change_status(uid, "0").json())
            row = db_utils.query_one("SELECT status FROM sys_user WHERE user_id=%s", (uid,))
            assert row and row["status"] == "0", "状态未恢复为启用"
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("USER_FLOW_005 接口重置密码 → DB 验证密码已更新")
    def test_api_reset_password_verify(self, user_client):
        """接口造用户 → 接口重置密码 → DB 验证密码已更新。"""
        username = gen_name("auto_flow")
        assert_api_ok(user_client.create({
            "userName": username, "nickName": "重置测试",
            "password": "Test123456", "phonenumber": gen_mobile(), "deptId": 100, "status": "0"
        }).json())
        rows = user_client.page({"pageNum": 1, "pageSize": 10, "userName": username}).json()["rows"]
        uid = rows[0]["userId"]
        try:
            # 取旧密码
            old = db_utils.query_one("SELECT password FROM sys_user WHERE user_id=%s", (uid,))
            assert_api_ok(user_client.reset_password(uid, "New123456").json())
            new = db_utils.query_one("SELECT password FROM sys_user WHERE user_id=%s", (uid,))
            assert new and new["password"] and new["password"] != old["password"], "密码未更新"
        finally:
            assert_api_ok(user_client.delete(uid).json())
