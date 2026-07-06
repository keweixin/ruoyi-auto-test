"""登记并回收本轮自动化测试签发的 access token。"""
import json

import requests

from common.logger import log


class TokenRegistry:
    def __init__(self):
        self._tokens = set()

    def register(self, token):
        if token:
            self._tokens.add(str(token))

    def register_response(self, response):
        try:
            body = response.json()
        except ValueError:
            return
        if isinstance(body, dict) and body.get("code") == 0:
            data = body.get("data")
            if isinstance(data, dict):
                self.register(data.get("accessToken"))

    def register_storage_state(self, state_path):
        try:
            with open(state_path, encoding="utf-8") as state_file:
                state = json.load(state_file)
        except (OSError, json.JSONDecodeError):
            return
        for origin in state.get("origins", []):
            for item in origin.get("localStorage", []):
                if item.get("name") == "ACCESS_TOKEN":
                    self.register(self._cached_value(item.get("value")))

    def register_page(self, page):
        try:
            token = page.evaluate(
                """() => {
                    const raw = localStorage.getItem('ACCESS_TOKEN')
                    if (!raw) return null
                    try {
                        const parsed = JSON.parse(raw)
                        const cached = parsed && typeof parsed === 'object' ? (parsed.v ?? parsed.value) : parsed
                        if (typeof cached !== 'string') return cached
                        try { return JSON.parse(cached) } catch (_) { return cached }
                    } catch (_) {
                        return raw
                    }
                }"""
            )
        except Exception:
            return
        self.register(token)

    @staticmethod
    def _cached_value(raw_value):
        if not raw_value:
            return None
        try:
            parsed = json.loads(raw_value)
        except (TypeError, json.JSONDecodeError):
            return raw_value
        if isinstance(parsed, dict):
            cached = parsed.get("v") or parsed.get("value")
            if isinstance(cached, str):
                try:
                    return json.loads(cached)
                except json.JSONDecodeError:
                    return cached
            return cached
        return parsed

    def revoke_all(self, base_url, tenant_id):
        tokens = tuple(self._tokens)
        self._tokens.clear()
        api_root = base_url.rstrip("/")
        if not api_root.endswith("/admin-api"):
            api_root += "/admin-api"
        failures = []
        for token in tokens:
            try:
                response = requests.post(
                    api_root + "/system/auth/logout",
                    headers={
                        "tenant-id": str(tenant_id),
                        "Authorization": f"Bearer {token}",
                    },
                    timeout=15,
                )
                body = response.json()
                if response.status_code >= 500 or body.get("code") not in (0, 401):
                    failures.append(f"status={response.status_code}, code={body.get('code')}")
            except (requests.RequestException, ValueError) as exc:
                failures.append(type(exc).__name__)
        log.info("本轮认证 Token 回收完成：登记 %d，失败 %d", len(tokens), len(failures))
        if failures:
            raise RuntimeError(f"有 {len(failures)} 个测试 Token 回收失败: {failures}")


TOKEN_REGISTRY = TokenRegistry()
