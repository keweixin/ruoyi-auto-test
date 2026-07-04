"""用户管理接口测试用例。

覆盖 USER_API_001 ~ 013：
- CRUD + 异常(用户名空/手机号错/重复) + 查询 + 状态(禁用登录失败/启用登录成功)
- 重置密码 + 数据库校验

学习重点：用户和部门关系、用户状态流转、重置密码、接口和 UI 双向校验。

⚠ 已核对源码：UserSaveReqVO 无 status / roleIds
   - 状态走 update_status
   - 角色绑定走 PermissionClient.assign_user_role（见 test_role / integration）
"""
import allure
import pytest

from common.config import cfg
from common import db_utils
from common.assert_utils import assert_api_ok, assert_api_fail
from common.allure_utils import attach_text
from common.random_utils import gen_username, gen_mobile
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA
from api_auto.clients.auth_client import AuthClient


@allure.feature("用户管理接口")
@pytest.mark.api
class TestUserApi:

    def _create_user(self, user_client):
        """辅助：创建一个测试用户，返回 (user_id, username, password)。"""
        username = gen_username()
        password = "Test123456"
        body = user_client.create({
            "username": username,
            "password": password,
            "nickname": "自动用户",
            "mobile": gen_mobile(),
            "deptId": 100,
        }).json()
        assert_api_ok(body, "创建用户")
        return body["data"], username, password

    @allure.story("新增")
    @allure.title("USER_API_001 新增后台用户成功")
    @pytest.mark.smoke
    def test_create_user(self, user_client):
        uid, _, _ = self._create_user(user_client)
        assert uid
        user_client.delete(uid)

    @allure.story("异常")
    @allure.title("USER_API_002 新增用户时用户名为空失败")
    def test_create_empty_username(self, user_client):
        body = user_client.create({
            "username": "", "password": "Test123456",
            "nickname": "x", "deptId": 100
        }).json()
        assert_api_fail(body, "用户名为空")

    @allure.story("异常")
    @allure.title("USER_API_003 新增用户时手机号格式错误失败")
    def test_create_bad_mobile(self, user_client):
        body = user_client.create({
            "username": gen_username(), "password": "Test123456",
            "nickname": "x", "mobile": "123", "deptId": 100
        }).json()
        assert_api_fail(body, "手机号格式错误")

    @allure.story("异常")
    @allure.title("USER_API_004 新增重复用户名失败")
    def test_create_duplicate_username(self, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            body = user_client.create({
                "username": username, "password": "Test123456",
                "nickname": "dup", "deptId": 100
            }).json()
            assert_api_fail(body, "用户名重复")
        finally:
            user_client.delete(uid)

    @allure.story("查询")
    @allure.title("USER_API_005 按用户名查询用户成功")
    @pytest.mark.smoke
    def test_page_by_username(self, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            body = user_client.page({"pageNo": 1, "pageSize": 10, "username": username}).json()
            assert_schema(body, PAGE_LIST_SCHEMA)
            assert_api_ok(body)
            assert body["data"]["total"] >= 1, "按用户名未查到"
        finally:
            user_client.delete(uid)

    @allure.story("查询")
    @allure.title("USER_API_006 按手机号查询用户成功")
    def test_page_by_mobile(self, user_client):
        uid, username, _ = self._create_user(user_client)
        # 取创建后的真实手机号
        mobile = user_client.get(uid).json()["data"]["mobile"]
        try:
            body = user_client.page({"pageNo": 1, "pageSize": 10, "mobile": mobile}).json()
            assert_api_ok(body)
            assert body["data"]["total"] >= 1, "按手机号未查到"
        finally:
            user_client.delete(uid)

    @allure.story("修改")
    @allure.title("USER_API_007 编辑用户手机号成功")
    def test_update_mobile(self, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            new_mobile = gen_mobile()
            body = user_client.update({
                "id": uid, "username": username, "nickname": "自动用户",
                "mobile": new_mobile, "deptId": 100
            }).json()
            assert_api_ok(body, "编辑手机号")
            # 确认改了
            after = user_client.get(uid).json()["data"]["mobile"]
            assert after == new_mobile
        finally:
            user_client.delete(uid)

    @allure.story("状态")
    @allure.title("USER_API_008 修改用户状态为禁用")
    def test_disable_user(self, user_client):
        uid, _, _ = self._create_user(user_client)
        try:
            body = user_client.update_status(uid, 1).json()  # 1=禁用
            assert_api_ok(body, "禁用用户")
        finally:
            user_client.delete(uid)

    @allure.story("状态")
    @allure.title("USER_API_009 禁用用户后登录失败")
    def test_disabled_user_cannot_login(self, user_client):
        uid, username, password = self._create_user(user_client)
        try:
            user_client.update_status(uid, 1)  # 禁用
            body = AuthClient(cfg.base_url, cfg.tenant_id).login(username, password).json()
            assert_api_fail(body, "禁用用户登录")
        finally:
            user_client.delete(uid)

    @allure.story("状态")
    @allure.title("USER_API_010 启用用户后登录成功")
    def test_enabled_user_can_login(self, user_client):
        uid, username, password = self._create_user(user_client)
        try:
            user_client.update_status(uid, 1)   # 先禁用
            user_client.update_status(uid, 0)   # 再启用
            body = AuthClient(cfg.base_url, cfg.tenant_id).login(username, password).json()
            assert_api_ok(body, "启用用户登录")
        finally:
            user_client.delete(uid)

    @allure.story("重置密码")
    @allure.title("USER_API_011 重置用户密码成功")
    def test_reset_password(self, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            new_pwd = "New123456"
            body = user_client.reset_password(uid, new_pwd).json()
            assert_api_ok(body, "重置密码")
            # 用新密码能登录
            login_body = AuthClient(cfg.base_url, cfg.tenant_id).login(username, new_pwd).json()
            assert_api_ok(login_body, "新密码登录")
        finally:
            user_client.delete(uid)

    @allure.story("删除")
    @allure.title("USER_API_012 删除测试用户成功")
    def test_delete_user(self, user_client):
        uid, _, _ = self._create_user(user_client)
        body = user_client.delete(uid).json()
        assert_api_ok(body, "删除用户")

    @allure.story("数据库校验")
    @allure.title("USER_API_013 数据库校验用户信息正确")
    @pytest.mark.db
    def test_db_check_user(self, user_client):
        uid, username, _ = self._create_user(user_client)
        try:
            row = db_utils.query_one(
                "SELECT username, status, deleted + 0 AS deleted FROM system_users WHERE id=%s",
                (uid,)
            )
            assert row and row["username"] == username and row["deleted"] == 0
            attach_text("用户数据库记录", str(row))
        finally:
            user_client.delete(uid)
