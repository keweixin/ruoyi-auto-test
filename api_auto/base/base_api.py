"""BaseApi：接口自动化 base 层，封装通用请求逻辑。

设计说明（解决了裸脚本的哪些问题）：
- base_url 写死      → 构造时传入，统一来自配置
- headers 重复       → get_headers 统一生成（含 token / tenant-id）
- token 没统一管理    → set_token / get_headers 内部维护
- 没有日志           → 请求/响应都记日志
- 没有报告附件       → 自动把请求/响应附加到 Allure
- 没有超时/异常处理   → timeout + try

若依原版约定（已实测 Docker 中 RuoYi v3.9.2）：
- 接口无统一前缀，直接 /login /system/...
- 登录返回 data.token（不是 accessToken）
- 鉴权头 Authorization: Bearer <token>，无 tenant-id
- 统一响应 { code, msg, data/rows }，code==200 成功
"""
import requests

from common.logger import log
from common.security_utils import mask_dict, mask_headers, mask_body_string

# 若依管理后台接口统一前缀
ADMIN_API_PREFIX = "/admin-api"


class BaseApi:
    """所有 Client 的基类，封装通用 HTTP 请求方法。"""

    def __init__(self, base_url, tenant_id=None):
        self.base_url = base_url.rstrip("/")
        self.tenant_id = str(tenant_id) if tenant_id else None
        self.token = None

    def set_token(self, token):
        """登录后设置 token，后续请求自动带上。"""
        self.token = token

    def get_headers(self, extra=None):
        """生成统一请求头：Authorization（原版无 tenant-id）。"""
        headers = {}
        if self.tenant_id:
            headers["tenant-id"] = self.tenant_id
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if extra:
            headers.update(extra)
        return headers

    def request(self, method, path, **kwargs):
        """统一请求入口：记日志 + Allure 附件。

        path 直接传如 "/login" "/system/dict/type/list"（原版无前缀）。
        kwargs 支持 params= / json= / headers= 等（透传给 requests）。
        """
        full_path = path
        url = self.base_url + full_path
        headers = self.get_headers(kwargs.pop("headers", None))

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
