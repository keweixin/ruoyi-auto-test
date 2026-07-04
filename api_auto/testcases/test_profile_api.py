"""个人中心接口测试用例。

覆盖 PROFILE_API_001 ~ 003：
- 获取当前登录用户个人信息
- 修改个人密码（旧密码→新密码→验证新密码登录→改回）
- 修改个人信息（昵称→验证→改回）

个人中心是每个登录用户都会用的入口，区别于管理员视角的 user 管理。
"""
import allure
import pytest

from common.config import cfg
from common.assert_utils import assert_api_ok, assert_api_fail, assert_response_ok, assert_response_fail
from common.test_data import DEFAULT_PASSWORD
from api_auto.clients.auth_client import AuthClient


@allure.feature("个人中心接口")
@pytest.mark.api
class TestProfileApi:

    @allure.story("个人信息")
    @allure.title("PROFILE_API_001 获取当前登录用户信息成功")
    @pytest.mark.smoke
    def test_get_profile(self, profile_client):
        """获取当前登录用户个人信息：返回 admin 的 id/username/nickname。"""
        body = assert_response_ok(profile_client.get_profile())
        user = body["data"]
        assert user["id"], "未返回用户 id"
        assert user["username"] == cfg.admin_user, \
            f"个人信息 username 期望 {cfg.admin_user}，实际 {user['username']}"
        assert user["nickname"], "nickname 不应为空"

    @allure.story("修改密码")
    @allure.title("PROFILE_API_002 修改个人密码成功")
    def test_update_password(self, profile_client):
        """修改个人密码：旧密码→新密码→用新密码能登录→改回原密码。

        会真实修改 admin 密码，用完务必改回，否则影响其他用例。
        """
        old_pwd = cfg.admin_pwd
        new_pwd = "New" + old_pwd  # 简单变换，确保与原密码不同
        try:
            # 修改密码
            assert_response_ok(profile_client.update_password(old_pwd, new_pwd), "修改密码")
            # 用新密码能登录
            login_body = assert_response_ok(AuthClient(cfg.base_url, cfg.tenant_id).login(
                cfg.admin_user, new_pwd
            ), "新密码登录")
        finally:
            # 改回原密码（best-effort）
            try:
                profile_client.update_password(new_pwd, old_pwd)
            except Exception:
                pass

    @allure.story("修改密码")
    @allure.title("PROFILE_API_003 旧密码错误时修改密码失败")
    def test_update_password_wrong_old(self, profile_client):
        """旧密码错误时修改密码应失败。"""
        assert_response_fail(profile_client.update_password("wrong_old_pwd", "NewPwd123456"), "旧密码错误")

    @allure.story("个人信息")
    @allure.title("PROFILE_API_004 修改个人昵称成功")
    def test_update_nickname(self, profile_client):
        """修改个人昵称：改→验证→改回。"""
        # 先获取当前昵称
        original = profile_client.get_profile().json()["data"]["nickname"]
        new_nickname = "auto_test_nickname"
        try:
            assert_response_ok(profile_client.update_profile({"nickname": new_nickname}), "修改昵称")
            # 验证已更新
            updated = profile_client.get_profile().json()["data"]["nickname"]
            assert updated == new_nickname, f"昵称期望 {new_nickname}，实际 {updated}"
        finally:
            # 改回
            try:
                profile_client.update_profile({"nickname": original})
            except Exception:
                pass
