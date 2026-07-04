"""BaseApi：接口自动化请求层，封装连接复用、重试、超时和文件传输。

设计说明（解决了裸脚本的哪些问题）：
- base_url 写死      → 构造时传入，统一来自配置
- headers 重复       → get_headers 统一生成（含 token / tenant-id）
- token 没统一管理    → set_token / get_headers 内部维护
- 没有日志           → 请求/响应都记日志
- 没有报告附件       → 自动把请求/响应附加到 Allure
- 没有超时/异常处理   → 连接/读取超时 + 统一 ApiRequestError
- 每次请求新建连接    → requests.Session 连接池复用
- 瞬时网络波动        → 仅安全方法自动退避重试

RuoYi-Vue-Pro 约定（已按本地源码与 48080 服务核对）：
- 管理端统一前缀 /admin-api
- 登录返回 data.accessToken
- 鉴权头 Authorization: Bearer <accessToken>，并携带 tenant-id
- 统一响应 { code, msg, data }，code==0 成功
"""
import os
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from common.logger import log
from common.security_utils import mask_dict, mask_headers, mask_body_string

# 若依管理后台接口统一前缀
ADMIN_API_PREFIX = "/admin-api"
DEFAULT_TIMEOUT = (3.05, 15)
RETRYABLE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
RETRYABLE_STATUS_CODES = (429, 502, 503, 504)


class ApiRequestError(RuntimeError):
    """统一表示 API 网络、超时和 HTTP 传输异常，不暴露请求敏感数据。"""

    def __init__(self, method, url, cause):
        self.method = str(method).upper()
        self.url = url
        self.cause = cause
        super().__init__(f"{self.method} {url} 请求失败: {type(cause).__name__}")


class BaseApi:
    """所有 Client 的基类，封装通用 HTTP 请求方法。"""

    def __init__(
        self,
        base_url,
        tenant_id="1",
        token_manager=None,
        session=None,
        timeout=DEFAULT_TIMEOUT,
        retry_total=2,
        backoff_factor=0.2,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_root = self.base_url if self.base_url.endswith(ADMIN_API_PREFIX) \
            else self.base_url + ADMIN_API_PREFIX
        self.tenant_id = str(tenant_id) if tenant_id else "1"
        self.token = None
        self.token_manager = token_manager
        self.timeout = timeout
        self._owns_session = session is None
        self.session = session or self._build_session(retry_total, backoff_factor)

    @staticmethod
    def _build_session(retry_total, backoff_factor):
        retry_total = max(0, int(retry_total))
        retry = Retry(
            total=retry_total,
            connect=retry_total,
            read=0,
            status=retry_total,
            allowed_methods=RETRYABLE_METHODS,
            status_forcelist=RETRYABLE_STATUS_CODES,
            backoff_factor=max(0, float(backoff_factor)),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def close(self):
        """关闭本实例创建的 Session；外部注入的 Session 由调用方管理。"""
        if self._owns_session:
            self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
        return False

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
        method = str(method).upper()
        full_path = path if path.startswith("/") else "/" + path
        if full_path.startswith(ADMIN_API_PREFIX + "/"):
            full_path = full_path[len(ADMIN_API_PREFIX):]
        url = self.api_root + full_path
        extra_headers = kwargs.pop("headers", None)
        headers = self.get_headers(extra_headers)
        timeout = kwargs.pop("timeout", self.timeout)

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

        resp = self._send(method, url, headers, timeout, kwargs)
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
            resp = self._send(method, url, headers, timeout, kwargs)
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

    def _send(self, method, url, headers, timeout, kwargs):
        try:
            return self.session.request(
                method,
                url,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            log.error("请求失败 %s %s: %s", method, url, type(exc).__name__)
            raise ApiRequestError(method, url, exc) from exc

    # 四个常用方法的快捷封装
    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def upload(
        self,
        path,
        file_path,
        field_name="file",
        data=None,
        filename=None,
        content_type=None,
        **kwargs,
    ):
        """以 multipart/form-data 上传单个文件。"""
        source = Path(file_path)
        if not source.is_file():
            raise FileNotFoundError(f"上传文件不存在: {source}")

        with source.open("rb") as file_obj:
            file_value = (filename or source.name, file_obj)
            if content_type:
                file_value = (filename or source.name, file_obj, content_type)
            kwargs["files"] = {field_name: file_value}
            if data is not None:
                kwargs["data"] = data
            return self.post(path, **kwargs)

    def download(self, path, destination, chunk_size=8192, **kwargs):
        """流式下载到临时文件，成功后原子替换目标文件。"""
        if chunk_size <= 0:
            raise ValueError("chunk_size 必须大于 0")

        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(target.name + ".part")
        kwargs["stream"] = True

        try:
            with self.get(path, **kwargs) as response:
                response.raise_for_status()
                with partial.open("wb") as file_obj:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file_obj.write(chunk)
            os.replace(partial, target)
        except requests.RequestException as exc:
            partial.unlink(missing_ok=True)
            raise ApiRequestError("GET", str(path), exc) from exc
        except Exception:
            partial.unlink(missing_ok=True)
            raise
        return target
