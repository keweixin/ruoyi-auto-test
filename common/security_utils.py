"""安全工具：递归脱敏 password / token / secret 等敏感字段。

调用方：BaseApi 记录日志和 Allure 附件时使用。
"""
import re


SENSITIVE_KEYS = {"password", "pwd", "token", "access_token", "accessToken",
                  "refresh_token", "refreshToken", "secret", "authorization"}


def _mask_value(value):
    """对单个值脱敏。"""
    s = str(value)
    if len(s) <= 6:
        return "***"
    return s[:4] + "****" + s[-4:]


def mask_dict(data):
    """递归脱敏 dict / list / str，返回脱敏后副本。"""
    if isinstance(data, dict):
        return {k: _mask_value(v) if k in SENSITIVE_KEYS or "token" in k.lower() or "password" in k.lower()
                else mask_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [mask_dict(i) for i in data]
    return data


def mask_headers(headers):
    """脱敏请求头中的 Authorization 和 token 头。"""
    if not headers:
        return headers
    masked = {}
    for k, v in headers.items():
        if k.lower() == "authorization":
            # "Bearer eyJhbGciOi..." -> "Bearer eyJh****..."
            parts = v.split(" ", 1)
            if len(parts) == 2:
                masked[k] = parts[0] + " " + _mask_value(parts[1])
            else:
                masked[k] = _mask_value(v)
        elif "token" in k.lower() or "secret" in k.lower():
            masked[k] = _mask_value(v)
        else:
            masked[k] = v
    return masked


def mask_body_string(text):
    """对日志/Allure 输出体按敏感关键词正则脱敏。"""
    text = text or ""
    # JSON 字段脱敏："password": "xxx"
    for key in SENSITIVE_KEYS:
        pattern = re.compile(rf'("{re.escape(key)}"\s*:\s*")[^"]+(")', re.IGNORECASE)
        text = pattern.sub(r'\1****\2', text)
    # Bearer token 脱敏：Bearer xxxxxx -> Bearer ****
    text = re.sub(r'(Bearer\s+)[^\s",}]+', r'\1****', text)
    return text