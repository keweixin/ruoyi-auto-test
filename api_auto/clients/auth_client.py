"""AuthClient：登录认证接口客户端。

已核对源码 AuthController.java：
- POST /system/auth/login        登录（@PermitAll，需 tenant-id）
- POST /system/auth/logout       退出（@PermitAll）
- GET  /system/auth/get-permission-info  获取当前登录用户信息（需 token）

注意：登录默认需要验证码。若依 application*.yaml 里设置
      yudao.captcha.enable: false 后，可不传 captchaVerification。
"""
from api_auto.base.base_api import BaseApi


class AuthClient(BaseApi):
    """登录认证接口客户端。"""

    def login(self, username, password):
        """登录，返回 Response（token 在 body['data']['accessToken']）。"""
        return self.post(
            "/system/auth/login",
            json={"username": username, "password": password},
        )

    def logout(self):
        """退出登录。"""
        return self.post("/system/auth/logout")

    def get_permission_info(self):
        """获取当前登录用户的权限信息（用户/角色/菜单）。"""
        return self.get("/system/auth/get-permission-info")
