"""BaseApi：接口自动化 base 层，封装通用请求逻辑。

设计说明（解决了裸脚本的哪些问题）：
- base_url 写死      → 构造时传入，统一来自配置
- headers 重复       → get_headers 统一生成（含 token / tenant-id）
- token 没统一管理    → set_token / get_headers 内部维护
- 没有日志           → 请求/响应都记日志
- 没有报告附件       → 自动把请求/响应附加到 Allure
- 没有超时/异常处理   → timeout + try

RuoYi-Vue-Pro 约定（已按本地源码与 48080 服务核对）：
- 管理端统一前缀 /admin-api
- 登录返回 data.accessToken
- 鉴权头 Authorization: Bearer <accessToken>，并携带 tenant-id
- 统一响应 { code, msg, data }，code==0 成功
"""
import requests

from common.logger import log
from common.security_utils import mask_dict, mask_headers, mask_body_string

# 若依管理后台接口统一前缀
ADMIN_API_PREFIX = "/admin-api"


class BaseApi:
    """所有 Client 的基类，封装通用 HTTP 请求方法。"""

    def __init__(self, base_url, tenant_id="1", token_manager=None):
        self.base_url = base_url.rstrip("/")
        self.api_root = self.base_url if self.base_url.endswith(ADMIN_API_PREFIX) \
            else self.base_url + ADMIN_API_PREFIX
        self.tenant_id = str(tenant_id) if tenant_id else "1"
        self.token = None
        self.token_manager = token_manager

    def set_token(self, token):
        """显式设置固定 token，并停止使用构造时传入的 TokenManager。"""
        self.token = token
        self.token_manager = None

    @staticmethod
    def _is_unauthorized(response):
        """兼容 RuoYi 将鉴权失败包装为 HTTP 200 + 业务 code=401 的行为。"""
        if response.status_code == 401:
            return True
        try:
            return response.json().get("code") == 401
        except (ValueError, AttributeError):
            return False

    def get_headers(self, extra=None):
        """生成统一请求头：tenant-id + Authorization。"""
        headers = {"tenant-id": self.tenant_id}
        token = self.token_manager.get_access_token() if self.token_manager else self.token
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if extra:
            headers.update(extra)
        return headers

    def request(self, method, path, **kwargs):
        """统一请求入口：记日志 + Allure 附件。

        path 传入管理端相对路径，如 "/system/auth/login"。
        kwargs 支持 params= / json= / headers= 等（透传给 requests）。
        """
        full_path = path if path.startswith("/") else "/" + path
        if full_path.startswith(ADMIN_API_PREFIX + "/"):
            full_path = full_path[len(ADMIN_API_PREFIX):]
        url = self.api_root + full_path
        extra_headers = kwargs.pop("headers", None)
        headers = self.get_headers(extra_headers)

        params = kwargs.get("params")
        json_body = kwargs.get("json")
        safe_params = mask_dict(params)
        safe_json = mask_dict(json_body)
        safe_headers = mask_headers(headers)
        log.info("请求 %s %s params=%s json=%s", method, url, safe_params, safe_json)

        # 记录请求到 Allure（脱敏后）
        try:
            from common.allure_utils import attach_text
            attach_text(f"请求 {method} {full_path}",
                        f"params={safe_params}\njson={safe_json}\nheaders={safe_headers}")
        except Exception:
            pass

        resp = requests.request(method, url, headers=headers, timeout=15, **kwargs)
        auth_paths = {
            "/system/auth/login",
            "/system/auth/refresh-token",
            "/system/auth/logout",
        }
        can_retry_auth = (
            self.token_manager is not None
            and full_path not in auth_paths
            and not (extra_headers and "Authorization" in extra_headers)
        )
        if self._is_unauthorized(resp) and can_retry_auth:
            log.warning("请求 %s 返回 401，刷新认证后重试一次", full_path)
            self.token_manager.invalidate_access_token()
            headers = self.get_headers(extra_headers)
            resp = requests.request(method, url, headers=headers, timeout=15, **kwargs)
        safe_resp_text = mask_body_string(resp.text[:2000])
        log.info("响应 %s -> %s body=%s", full_path, resp.status_code, mask_body_string(resp.text[:500]))

        # 记录响应到 Allure（脱敏后）
        try:
            from common.allure_utils import attach_text
            attach_text(f"响应 {full_path}",
                        f"status={resp.status_code}\nbody={safe_resp_text}")
        except Exception:
            pass

        return resp

    # 四个常用方法的快捷封装
    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)
