"""根 conftest.py：全项目共享 fixture。

优化点：
- API/UI/integration 共用一套 fixture；
- Playwright 浏览器 session 级复用，每条用例只新建 context/page；
- Trace 仅在失败时保存，成功用例不落盘；
- 失败截图仅失败时保存并附加 Allure；
- 每条用例结束后执行本轮前缀数据清理。
"""
import os
import re
import sys
import time
import pytest
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.config import cfg
from common.logger import log
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_png
from api_auto.clients.auth_client import AuthClient
from api_auto.clients.dict_client import DictClient
from api_auto.clients.dept_client import DeptClient
from api_auto.clients.post_client import PostClient
from api_auto.clients.user_client import UserClient
from api_auto.clients.role_client import RoleClient
from api_auto.clients.menu_client import MenuClient
from api_auto.clients.permission_client import PermissionClient
from api_auto.auth.token_manager import TokenManager
from api_auto.auth.token_registry import TOKEN_REGISTRY
from ui_auto.auth.auth_state_manager import AuthStateManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACES_DIR = os.path.join(BASE_DIR, "traces")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")


def _safe_artifact_name(node_name):
    """把 pytest 用例名转成安全文件名，避免参数化用例名包含路径特殊字符。"""
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", node_name).strip("_") or "test"

def _client_with_token_manager(client_class, token_manager):
    return client_class(cfg.base_url, cfg.tenant_id, token_manager=token_manager)


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """每条用例结束后兜底清理本轮 TEST_RUN_PREFIX 测试数据。"""
    yield
    from common.cleanup_utils import cleanup_auto_data
    cleanup_auto_data()


@pytest.fixture(scope="session", autouse=True)
def revoke_test_tokens():
    """测试会话结束时精确注销本轮 API/UI 登录签发的 Token。"""
    yield
    TOKEN_REGISTRY.revoke_all(cfg.base_url, cfg.tenant_id)


def _web_ready():
    import requests
    try:
        r = requests.get(cfg.web_url, timeout=3)
        return r.status_code != 404
    except Exception:
        return False


@pytest.fixture(scope="session")
def token_manager():
    """整轮 API 测试共享认证状态，过期时自动刷新。"""
    return TokenManager(
        cfg.base_url,
        cfg.tenant_id,
        cfg.admin_user,
        cfg.admin_pwd,
        cfg.tenant_name,
    )


@pytest.fixture(scope="session")
def admin_token(token_manager):
    """兼容仍需裸 token 的测试；新 Client 应直接依赖 token_manager。"""
    return token_manager.get_access_token()


@pytest.fixture
def logout_token():
    client = AuthClient(cfg.base_url, cfg.tenant_id)
    body = client.login(cfg.admin_user, cfg.admin_pwd).json()
    assert_api_ok(body, "退出登录专用 token 登录")
    return body["data"]["accessToken"]


@pytest.fixture
def auth_client(token_manager):
    return _client_with_token_manager(AuthClient, token_manager)


@pytest.fixture
def dict_client(token_manager):
    return _client_with_token_manager(DictClient, token_manager)


@pytest.fixture
def dept_client(token_manager):
    return _client_with_token_manager(DeptClient, token_manager)


@pytest.fixture
def post_client(token_manager):
    return _client_with_token_manager(PostClient, token_manager)


@pytest.fixture
def user_client(token_manager):
    return _client_with_token_manager(UserClient, token_manager)


@pytest.fixture
def role_client(token_manager):
    return _client_with_token_manager(RoleClient, token_manager)


@pytest.fixture
def menu_client(token_manager):
    return _client_with_token_manager(MenuClient, token_manager)


@pytest.fixture
def permission_client(token_manager):
    return _client_with_token_manager(PermissionClient, token_manager)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    if not _web_ready():
        pytest.skip("前端未启动，跳过 UI 用例")
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def auth_state_manager(browser, tmp_path_factory):
    state_file = tmp_path_factory.mktemp("auth") / "state.json"
    manager = AuthStateManager(browser, state_file, cfg)
    manager.create_state()
    return manager


@pytest.fixture(scope="session")
def storage_state(auth_state_manager):
    """兼容需要直接读取状态文件路径的用例。"""
    return auth_state_manager.ensure_state()


@pytest.fixture
def page(auth_state_manager, request):
    """带登录态的页面。session 级 browser 复用；失败时才保存 trace。"""
    context, pg = auth_state_manager.new_authenticated_page()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    try:
        yield pg
    finally:
        failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
        if failed:
            os.makedirs(TRACES_DIR, exist_ok=True)
            trace_path = os.path.join(
                TRACES_DIR,
                f"trace_{_safe_artifact_name(request.node.name)}_{int(time.time())}.zip",
            )
            context.tracing.stop(path=trace_path)
            log.info("失败 trace 已保存: %s", trace_path)
        else:
            context.tracing.stop()
        context.close()


@pytest.fixture
def fresh_page(browser, request):
    """无登录态页面。session 级 browser 复用；失败时才保存 trace。"""
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    pg = context.new_page()
    try:
        yield pg
    finally:
        TOKEN_REGISTRY.register_page(pg)
        failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
        if failed:
            os.makedirs(TRACES_DIR, exist_ok=True)
            trace_path = os.path.join(
                TRACES_DIR,
                f"trace_fresh_{_safe_artifact_name(request.node.name)}_{int(time.time())}.zip",
            )
            context.tracing.stop(path=trace_path)
            log.info("失败 trace 已保存: %s", trace_path)
        else:
            context.tracing.stop()
        context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)
    if report.when == "call" and report.failed:
        pg = item.funcargs.get("page") or item.funcargs.get("fresh_page")
        if pg is not None:
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            shot_path = os.path.join(SCREENSHOTS_DIR, f"{_safe_artifact_name(item.name)}_{int(time.time())}.png")
            try:
                pg.screenshot(path=shot_path)
                attach_png("失败截图", shot_path)
                log.info("失败截图已保存: %s", shot_path)
            except Exception as e:
                log.warning("截图失败: %s", e)
