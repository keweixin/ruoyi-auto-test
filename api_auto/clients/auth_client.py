"""AuthClient：登录认证接口客户端（RuoYi v3.9.2 原版）。

已实测：
- POST /login            登录，返回 data.token
- POST /logout           退出
- GET  /getInfo          获取当前登录用户信息
- 无 tenant-id；登录需关闭验证码（sys_config sys.account.captchaEnabled=false）
"""
from api_auto.base.base_api import BaseApi


class AuthClient(BaseApi):
    """登录认证接口客户端。"""

    def login(self, username, password):
        """登录，返回 Response（token 在 body['data']['token']）。"""
        return self.post("/login", json={"username": username, "password": password})

    def logout(self):
        """退出登录。"""
        return self.post("/logout")

    def get_info(self):
        """获取当前登录用户信息。"""
        return self.get("/getInfo")
