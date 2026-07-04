# BUG_001 Token 过期后接口返回 401 导致批量用例失败

## 缺陷标题
Token 过期后接口返回 401，未自动刷新，导致同一 session 内后续用例批量失败

## 基本信息
| 项 | 值 |
|---|---|
| 缺陷编号 | BUG_001 |
| 模块 | 登录认证 / 接口客户端 |
| 严重程度 | Critical |
| 优先级 | P0 |
| 状态 | Fixed（已修复） |
| 发现阶段 | 接口自动化联调 |

## 测试环境
| 项 | 值 |
|---|---|
| 后端 | RuoYi-Vue-Pro，`http://localhost:48080` |
| accessToken 有效期 | 30 分钟（后端 `application-local.yaml` 配置） |
| 测试框架 | pytest 7.4.4 + requests 2.31.0 |

## 前置条件
1. 后端服务正常启动，`admin/admin123` 可登录
2. 测试运行时间超过 accessToken 有效期，或手工将有效期调短至 1 分钟以复现

## 复现步骤
1. 执行全量 API 测试：`pytest api_auto/testcases -q`
2. 让运行时间超过 accessToken 有效期（实际可在后端将 `yudao.security.token-expire-time` 调为 60 秒）
3. 观察后续用例的执行结果

## 实际结果
首个用例登录成功拿到 token，约 30 分钟后 token 过期，后续所有需要鉴权的用例返回 HTTP 200 + `code=401`（RuoYi 将鉴权失败包装为业务码而非 HTTP 401），用例在断言 `code==0` 处批量失败。

关键报错：
```
AssertionError: assert 401 == 0
  +  401
  -  0
```

## 预期结果
token 过期时框架应自动感知并刷新（refreshToken 换新 token）或重新登录，对用例透明，不应出现因 token 过期导致的批量失败。

## 原因分析
1. **RuoYi 的 401 包装**：后端把鉴权失败返回为 HTTP 200 + JSON `{code: 401}`，而非标准 HTTP 401 状态码。原实现只判断 `response.status_code == 401`，漏判了这种业务码包装，导致 401 未被识别。
2. **缺少 token 失效感知**：原实现拿到 token 后缓存在 session 级 fixture，没有过期检测，也没有失效后自动恢复机制。
3. **无重试**：请求失败后直接返回，没有"识别 401 → 刷新 → 重试一次"的闭环。

## 解决方案
在 `api_auto/auth/token_manager.py` 与 `api_auto/base/base_api.py` 中实现三层恢复机制：

1. **主动刷新（过期前）**：`TokenManager.get_access_token()` 在 `当前时间 + 60s 提前量 >= expires_time` 时，优先用 refreshToken 刷新，避免临过期才请求。
2. **失效感知 + 重试（过期后）**：`BaseApi._is_unauthorized()` 同时识别 HTTP 401 与业务码 `code==401`；命中后调用 `token_manager.invalidate_access_token()` 标记失效，刷新 token 后重试该请求一次（限次，避免死循环）。
3. **降级重新登录**：refreshToken 也失效时，`refresh_access_token()` 自动回退到重新登录，保证恢复成功。

核心代码（`base_api.py`）：
```python
def _is_unauthorized(self, response):
    """兼容 RuoYi 将鉴权失败包装为 HTTP 200 + 业务 code=401 的行为。"""
    if response.status_code == 401:
        return True
    # RuoYi 把 401 包成业务码
    return response.json().get("code") == 401

# 请求后命中 401 且配置了 token_manager → 标记失效 + 刷新 + 重试一次
if self._is_unauthorized(resp) and can_retry_auth:
    self.token_manager.invalidate_access_token()
    self.token_manager.refresh_access_token()
    resp = self._do_request(...)  # 重试一次
```

## 关联用例
- `AUTH_API_006` 未携带 token 访问用户信息失败（验证 401 识别）
- `AUTH_API_010` refreshToken 可换取新 accessToken
- `AUTH_API_011` accessToken 失效后自动刷新并重试（直接验证本修复）
- 所有 `ROLE_API_*` / `USER_API_*` 等长链路用例（间接受益）

## 验证方式
1. 将后端 token 有效期调为 60 秒
2. 执行 `pytest api_auto/testcases -q`，运行时间必然超过 60 秒
3. 全部 75 条通过，无 401 批量失败
4. Allure 报告中可见 `AUTH_API_011` 的"自动刷新重试"步骤

## 经验沉淀
- 被测系统把 HTTP 状态码包装成业务码是常见坑，鉴权拦截要兼容两种形式
- 长时间运行的测试套件必须有 token 生命周期管理，不能假设 token 永不过期
- "识别→刷新→重试"的限次重试模式，比单纯的"用例开始前重新登录"更高效
