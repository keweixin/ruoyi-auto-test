"""通过 LoginPage 创建、复用并校验 Playwright storage_state。"""
import json
import os
import threading
from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError

from common.logger import log
from ui_auto.base.base_page import is_ci, TIMEOUT_NAV, TIMEOUT_CI_NAV
from common.token_registry import TOKEN_REGISTRY
from ui_auto.pages.login_page import LoginPage


class AuthStateManager:
    """管理 UI 登录快照，并在快照失效时重新登录一次。"""

    def __init__(self, browser, state_path, config):
        self.browser = browser
        self.state_path = str(state_path)
        self.config = config
        self._lock = threading.RLock()

    def create_state(self):
        """调用 LoginPage 登录并写入可复用的 storage_state。"""
        with self._lock:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            context = self.browser.new_context()
            page = context.new_page()
            try:
                login_page = LoginPage(page, self.config.web_url)
                login_page.open()
                login_page.login(
                    self.config.admin_user,
                    self.config.admin_pwd,
                    self.config.tenant_name,
                )
                login_page.wait_logged_in()
                context.storage_state(path=self.state_path)
                TOKEN_REGISTRY.register_storage_state(self.state_path)
                log.info("UI 登录态已写入: %s", self.state_path)
            finally:
                context.close()
        return self.state_path

    def ensure_state(self):
        if not os.path.isfile(self.state_path):
            self.create_state()
        return self.state_path

    def new_authenticated_page(self):
        """创建已登录 Context/Page；快照失效时重新生成并重试一次。"""
        # CI（Vite dev server 首次编译较慢）下放宽超时
        nav_timeout = TIMEOUT_CI_NAV if is_ci() else TIMEOUT_NAV
        for attempt in range(2):
            try:
                context = self.browser.new_context(storage_state=self.ensure_state())
            except (PlaywrightError, json.JSONDecodeError):
                if attempt == 0:
                    log.warning("UI storage_state 文件损坏，重新登录生成快照")
                    self.create_state()
                    continue
                raise
            page = context.new_page()
            # domcontentloaded 比 load 更早触发，避免 dev server 首编时长时间等 load 事件
            page.goto(self.config.web_url + "/index", wait_until="domcontentloaded", timeout=nav_timeout)
            page.wait_for_url(
                lambda url: urlparse(str(url)).path in ("/", "/index", "/login"),
                timeout=nav_timeout,
            )
            if urlparse(page.url).path != "/login":
                return context, page
            context.close()
            if attempt == 0:
                log.warning("UI storage_state 已失效，重新登录生成快照")
                self.create_state()
        raise AssertionError("重新登录后 UI storage_state 仍然无效")
