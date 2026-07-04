"""RuoYi-Vue-Pro 管理端登录认证接口客户端。

已实测：
- POST /system/auth/login               登录，返回 data.accessToken
- POST /system/auth/logout              退出
- GET  /system/auth/get-permission-info 获取用户权限信息
"""
from api_auto.base.base_api import BaseApi


class AuthClient(BaseApi):
    """登录认证接口客户端。"""

    def login(self, username, password, tenant_name=None):
        """登录，返回 Response（token 在 body['data']['accessToken']）。

        Vue3 登录页会额外提交 tenantName；接口在 tenant-id 已明确时也兼容不传。
        这里默认带上 tenantName，保持和真实前端请求一致。
        """
        from common.config import cfg
        data = {"username": username, "password": password}
        tenant_name = tenant_name if tenant_name is not None else getattr(cfg, "tenant_name", "")
        if tenant_name:
            data["tenantName"] = tenant_name
        response = self.post("/system/auth/login", json=data)
        from common.token_registry import TOKEN_REGISTRY
        TOKEN_REGISTRY.register_response(response)
        return response

    def logout(self):
        """退出登录。"""
        return self.post("/system/auth/logout")

    def refresh_token(self, refresh_token):
        """使用 refresh token 换取新的登录信息。"""
        response = self.post(
            "/system/auth/refresh-token",
            params={"refreshToken": refresh_token},
        )
        from common.token_registry import TOKEN_REGISTRY
        TOKEN_REGISTRY.register_response(response)
        return response

    def get_permission_info(self):
        """获取当前登录用户、角色、权限和菜单。"""
        return self.get("/system/auth/get-permission-info")

    # 保留旧调用名，迁移期间避免 fixture/用例出现两套实现。
    def get_info(self):
        return self.get_permission_info()
