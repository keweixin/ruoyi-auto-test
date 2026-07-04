"""用户管理接口测试用例。

覆盖 USER_API_001 ~ 013：
- CRUD + 异常(用户名空/手机号错/重复) + 查询 + 状态(禁用登录失败/启用登录成功)
- 重置密码 + 数据库校验

USER_API_001~004 采用 YAML 表驱动（data/user_data.yaml 的 create_cases），
由 common.data_provider.load_create_cases 读取参数化数据。

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
from common.allure_utils import attach_json, attach_text
from common.test_data import valid_role_data
from common.random_utils import gen_username, gen_mobile
from common.schema_utils import assert_schema, PAGE_LIST_SCHEMA
from common.data_provider import build_case_payload, load_create_cases, build_parametrize
from common.test_data import valid_user_data, create_user, DEFAULT_RESET_PASSWORD
from api_auto.clients.auth_client import AuthClient


_USER_CASES, _USER_IDS = build_parametrize(load_create_cases("user"))


@allure.feature("用户管理接口")
@pytest.mark.api
class TestUserApi:

    def _create_user(self, user_client):
        """辅助：创建一个测试用户，返回 (user_id, username, password)。复用 common.test_data.create_user。"""
        ent = create_user(user_client)
        return ent.id, ent.name, ent.extra["password"]

    @allure.story("角色分配")
    @allure.title("USER_API_014 分配角色前后查询用户角色")
    def test_list_user_roles_before_and_after_assign(
        self, user_client, role_client, permission_client
    ):
        uid, _, _ = self._create_user(user_client)
        rid = role_client.create(valid_role_data()).json()["data"]
        try:
            before = permission_client.list_user_roles(uid).json()
            assert_api_ok(before, "分配前查询用户角色")
            permission_client.assign_user_role(uid, [rid])
            after = permission_client.list_user_roles(uid).json()
            assert_api_ok(after, "分配后查询用户角色")
            attach_json("用户角色响应", after)
            role_ids = set(after["data"])
            assert rid in role_ids
        finally:
            permission_client.assign_user_role(uid, [])
            user_client.delete(uid)
            role_client.delete(rid)

    @allure.story("新增")
    @pytest.mark.parametrize("case", _USER_CASES, ids=_USER_IDS)
    def test_create_user_ddt(self, user_client, case):
        """USER_API_001~004 表驱动：合法创建 + 用户名空 + 手机号错 + 重复用户名。

        数据来源 data/user_data.yaml 的 create_cases，新增用例只需加 YAML 行，无需改代码。
        """
        allure.dynamic.title(f"{case['case_id']} {case['desc']}")
        payload = build_case_payload("user", case)
        # 重复场景：先创建一条占住 username，再用同 username 再建
        if case["setup"] == "duplicate":
            first = user_client.create(payload).json()
            assert_api_ok(first, "前置：第一次创建")
            try:
                body = user_client.create(payload).json()
            finally:
                user_client.delete(first["data"])
        else:
            body = user_client.create(payload).json()

        if case["expect_ok"]:
            assert_api_ok(body, case["desc"])
            uid = body["data"]
            assert uid, "创建成功但未返回 id"
            user_client.delete(uid)
        else:
            assert_api_fail(body, case["desc"])
            if case["expect_msg_contains"]:
                assert case["expect_msg_contains"] in body.get("msg", ""), \
                    f"msg 期望含 {case['expect_msg_contains']!r}，实际 {body.get('msg')!r}"

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
            current = user_client.get(uid).json()["data"]
            current.update({"id": uid, "username": username, "mobile": new_mobile})
            body = user_client.update(current).json()
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
            new_pwd = DEFAULT_RESET_PASSWORD
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
            db_utils.assert_db_record("system_users", uid,
                                      {"username": username}, "用户数据库记录")
        finally:
            user_client.delete(uid)
