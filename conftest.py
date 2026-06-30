"""根 conftest.py：全项目共享 fixture。

作用：
- 把项目根目录加入 import 路径；
- 统一提供 API token、各业务 Client、Playwright page/fresh_page；
- integration 目录能直接使用 admin_token / page / fresh_page；
- logout 使用独立 token，避免污染 session 管理员 token；
- UI 失败自动截图并附加到 Allure。
"""
import os
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


def _new_auth_client_with_token(token):
    client = AuthClient(cfg.base_url, cfg.tenant_id)
    client.set_token(token)
    return client


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """每条用例结束后兜底清理 auto_* 测试数据，防止 UI/联动失败残留。"""
    yield
    try:
        from common.cleanup_utils import cleanup_auto_data
        cleanup_auto_data()
    except Exception as exc:
        log.warning("自动清理 fixture 执行失败: %s", exc)


@pytest.fixture(scope="session")
def admin_token():
    """session 级管理员 token。禁止在 logout 类用例中消费它。"""
    log.info("====== 开始登录获取 session 管理员 token ======")
    client = AuthClient(cfg.base_url, cfg.tenant_id)
    body = client.login(cfg.admin_user, cfg.admin_pwd).json()
    assert_api_ok(body, "管理员登录")
    log.info("====== session 管理员 token 获取成功 ======")
    return body["data"]["accessToken"]


@pytest.fixture
def logout_token():
    """function 级独立 token，专供退出登录测试使用，避免污染 admin_token。"""
    client = AuthClient(cfg.base_url, cfg.tenant_id)
    body = client.login(cfg.admin_user, cfg.admin_pwd).json()
    assert_api_ok(body, "退出登录专用 token 登录")
    return body["data"]["accessToken"]


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
def storage_state(tmp_path_factory):
    """登录一次保存 UI 登录态，业务 UI 用例复用。"""
    state_file = tmp_path_factory.mktemp("auth") / "state.json"
    log.info("====== UI 登录，保存 session 登录态 ======")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(cfg.web_url)
        page.get_by_placeholder("请输入账号").fill(cfg.admin_user)
        page.get_by_placeholder("请输入密码").fill(cfg.admin_pwd)
        page.get_by_role("button", name="登 录").click()
        page.wait_for_url("**/index**", timeout=15000)
        page.context.storage_state(path=str(state_file))
        browser.close()
    log.info("====== UI session 登录态保存完成 ======")
    return str(state_file)


@pytest.fixture
def page(storage_state):
    """带登录态的页面，供业务 UI 与联动测试使用。"""
    os.makedirs(TRACES_DIR, exist_ok=True)
    trace_path = os.path.join(TRACES_DIR, f"trace_{int(time.time())}.zip")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_state)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        pg = context.new_page()
        yield pg
        context.tracing.stop(path=trace_path)
        browser.close()


@pytest.fixture
def fresh_page():
    """无登录态页面，供登录/退出/权限隔离类测试使用。"""
    os.makedirs(TRACES_DIR, exist_ok=True)
    trace_path = os.path.join(TRACES_DIR, f"trace_fresh_{int(time.time())}.zip")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        pg = context.new_page()
        yield pg
        context.tracing.stop(path=trace_path)
        browser.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """UI 用例失败时自动截图。"""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        pg = item.funcargs.get("page") or item.funcargs.get("fresh_page")
        if pg is not None:
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            shot_path = os.path.join(SCREENSHOTS_DIR, f"{item.name}_{int(time.time())}.png")
            try:
                pg.screenshot(path=shot_path)
                attach_png("失败截图", shot_path)
                log.info("失败截图已保存: %s", shot_path)
            except Exception as e:
                log.warning("截图失败: %s", e)
