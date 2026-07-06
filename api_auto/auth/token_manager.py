"""RuoYi-Vue-Pro access token 生命周期管理。"""
import time

from common.logger import log


class AuthenticationError(RuntimeError):
    """登录或刷新令牌失败。"""


class TokenManager:
    """集中登录、刷新并向所有 API Client 提供同一份 access token。"""

    def __init__(
        self,
        base_url,
        tenant_id,
        username,
        password,
        tenant_name=None,
        refresh_skew_seconds=60,
    ):
        self.base_url = base_url
        self.tenant_id = tenant_id
        self.username = username
        self.password = password
        self.tenant_name = tenant_name
        self.refresh_skew_ms = max(0, int(refresh_skew_seconds * 1000))
        self.access_token = None
        self.refresh_token = None
        self.expires_time_ms = 0

    def _auth_client(self):
        # 延迟导入，避免 AuthClient -> BaseApi -> TokenManager 的循环依赖。
        from api_auto.clients.auth_client import AuthClient
        return AuthClient(self.base_url, self.tenant_id)

    @staticmethod
    def _successful_data(response, action):
        try:
            body = response.json()
        except ValueError as exc:
            raise AuthenticationError(f"{action}失败：响应不是 JSON") from exc
        if not isinstance(body, dict):
            raise AuthenticationError(f"{action}失败：响应 JSON 不是对象")
        if response.status_code >= 400 or body.get("code") != 0 or not body.get("data"):
            raise AuthenticationError(
                f"{action}失败：status={response.status_code}, code={body.get('code')}, msg={body.get('msg')}"
            )
        return body["data"]

    def _update(self, data):
        if not isinstance(data, dict) or not data.get("accessToken"):
            raise AuthenticationError("认证响应缺少 data.accessToken")
        self.access_token = data["accessToken"]
        self.refresh_token = data.get("refreshToken") or self.refresh_token
        try:
            self.expires_time_ms = int(data.get("expiresTime") or 0)
        except (TypeError, ValueError) as exc:
            raise AuthenticationError("认证响应 data.expiresTime 格式错误") from exc

    def _login(self):
        response = self._auth_client().login(
            self.username,
            self.password,
            tenant_name=self.tenant_name,
        )
        self._update(self._successful_data(response, "管理员登录"))
        log.info("TokenManager 登录成功，access token 已更新")

    def _refresh(self):
        response = self._auth_client().refresh_token(self.refresh_token)
        self._update(self._successful_data(response, "刷新 access token"))
        log.info("TokenManager 刷新成功，access token 已更新")

    def _is_expiring(self):
        return not self.expires_time_ms or (
            int(time.time() * 1000) + self.refresh_skew_ms >= self.expires_time_ms
        )

    def get_access_token(self):
        """返回有效 token；临近过期时优先刷新，刷新失败则重新登录。"""
        if self.access_token and not self._is_expiring():
            return self.access_token
        if self.refresh_token:
            try:
                self._refresh()
                return self.access_token
            except AuthenticationError as exc:
                log.warning("refresh token 不可用，回退重新登录: %s", exc)
        self._login()
        return self.access_token

    def refresh_access_token(self):
        """主动刷新 token；无 refresh token 时重新登录。"""
        if self.refresh_token:
            try:
                self._refresh()
                return self.access_token
            except AuthenticationError as exc:
                log.warning("主动刷新失败，回退重新登录: %s", exc)
        self._login()
        return self.access_token

    def invalidate_access_token(self):
        """标记 access token 失效，让下一次请求刷新或重新登录。"""
        self.access_token = None
        self.expires_time_ms = 0
