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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACES_DIR = os.path.join(BASE_DIR, "traces")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")


def _safe_artifact_name(node_name):
    """把 pytest 用例名转成安全文件名，避免参数化用例名包含路径特殊字符。"""
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", node_name).strip("_") or "test"

def _new_auth_client_with_token(token):
    client = AuthClient(cfg.base_url, cfg.tenant_id)
    client.set_token(token)
    return client


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """每条用例结束后兜底清理本轮 TEST_RUN_PREFIX 测试数据。"""
    yield
    try:
        from common.cleanup_utils import cleanup_auto_data
        cleanup_auto_data()
    except Exception as exc:
        log.warning("自动清理 fixture 执行失败: %s", exc)


def _web_ready():
    import requests
    try:
        r = requests.get(cfg.web_url, timeout=3)
        return r.status_code != 404
    except Exception:
        return False


@pytest.fixture(scope="session")
def admin_token():
    log.info("====== 开始登录获取 session 管理员 token ======")
    client = AuthClient(cfg.base_url, cfg.tenant_id)
    body = client.login(cfg.admin_user, cfg.admin_pwd).json()
    assert_api_ok(body, "管理员登录")
    log.info("====== session 管理员 token 获取成功 ======")
    return body["data"]["token"] if isinstance(body.get("data"), dict) else body["token"]


@pytest.fixture
def logout_token():
    client = AuthClient(cfg.base_url, cfg.tenant_id)
    body = client.login(cfg.admin_user, cfg.admin_pwd).json()
    assert_api_ok(body, "退出登录专用 token 登录")
    return body["data"]["token"] if isinstance(body.get("data"), dict) else body["token"]


@pytest.fixture
def auth_client(admin_token):
    return _new_auth_client_with_token(admin_token)


@pytest.fixture
def dict_client(admin_token):
    c = DictClient(cfg.base_url, cfg.tenant_id); c.set_token(admin_token); return c


@pytest.fixture
def dept_client(admin_token):
    c = DeptClient(cfg.base_url, cfg.tenant_id); c.set_token(admin_token); return c


@pytest.fixture
def post_client(admin_token):
    c = PostClient(cfg.base_url, cfg.tenant_id); c.set_token(admin_token); return c


@pytest.fixture
def user_client(admin_token):
    c = UserClient(cfg.base_url, cfg.tenant_id); c.set_token(admin_token); return c


@pytest.fixture
def role_client(admin_token):
    c = RoleClient(cfg.base_url, cfg.tenant_id); c.set_token(admin_token); return c


@pytest.fixture
def menu_client(admin_token):
    c = MenuClient(cfg.base_url, cfg.tenant_id); c.set_token(admin_token); return c


@pytest.fixture
def permission_client(admin_token):
    c = PermissionClient(cfg.base_url, cfg.tenant_id); c.set_token(admin_token); return c


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
def storage_state(browser, tmp_path_factory):
    """登录一次保存 UI 登录态，业务 UI 用例复用。"""
    state_file = tmp_path_factory.mktemp("auth") / "state.json"
    log.info("====== UI 登录，保存 session 登录态 ======")
    context = browser.new_context()
    page = context.new_page()
    page.goto(cfg.web_url)
    page.get_by_placeholder("账号").fill(cfg.admin_user)
    page.get_by_placeholder("密码").fill(cfg.admin_pwd)
    page.get_by_role("button", name="登 录").click()
    page.wait_for_url("**/index**", timeout=15000)
    context.storage_state(path=str(state_file))
    context.close()
    log.info("====== UI session 登录态保存完成 ======")
    return str(state_file)


@pytest.fixture
def page(browser, storage_state, request):
    """带登录态的页面。session 级 browser 复用；失败时才保存 trace。"""
    context = browser.new_context(storage_state=storage_state)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    pg = context.new_page()
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
