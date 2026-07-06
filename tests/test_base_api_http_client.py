"""BaseApi 的基础行为单元测试。"""
import inspect
import pytest
import requests

from api_auto.base import base_api
from api_auto.base.base_api import BaseApi


class StubResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self.text = "{}"
        self._body = body or {"code": 0, "msg": "", "data": True}

    def json(self):
        return self._body


class RecordingSession:
    def __init__(self, responses=None, error=None):
        self.responses = iter(responses or [StubResponse()])
        self.error = error
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if self.error:
            raise self.error
        return next(self.responses)


class StubTokenManager:
    def __init__(self):
        self.invalidated = False

    def get_access_token(self):
        return "refreshed" if self.invalidated else "expired"

    def invalidate_access_token(self):
        self.invalidated = True


def client_with_session(session, token_manager=None):
    client = BaseApi("http://example.test", token_manager=token_manager)
    client.session = session
    return client


def test_request_uses_default_timeout_and_tenant_header():
    session = RecordingSession()
    client = client_with_session(session)

    client.get("/system/user/get", params={"id": 1})

    _, _, kwargs = session.calls[0]
    assert kwargs["timeout"] == (3.05, 15)
    assert kwargs["headers"]["tenant-id"] == "1"


def test_default_session_retries_only_safe_methods():
    client = BaseApi("http://example.test")
    retry = client.session.get_adapter("http://").max_retries

    parameters = inspect.signature(BaseApi).parameters
    assert "session" not in parameters
    assert "retry_total" not in parameters
    assert "backoff_factor" not in parameters
    assert retry.total == 2
    assert retry.allowed_methods == frozenset({"GET", "HEAD", "OPTIONS"})
    assert set(retry.status_forcelist) == {429, 502, 503, 504}


def test_post_is_not_in_retry_methods():
    retry = BaseApi("http://example.test").session.get_adapter("http://").max_retries
    assert "POST" not in retry.allowed_methods
    assert "PUT" not in retry.allowed_methods
    assert "DELETE" not in retry.allowed_methods


def test_request_converts_network_exception_without_leaking_payload():
    session = RecordingSession(error=requests.Timeout("secret-body"))
    client = client_with_session(session)

    with pytest.raises(base_api.ApiRequestError) as exc_info:
        client.post("/system/user/create", json={"password": "secret-body"})

    message = str(exc_info.value)
    assert "POST" in message
    assert "/admin-api/system/user/create" in message
    assert "secret-body" not in message


def test_unauthorized_response_refreshes_token_and_retries_once():
    session = RecordingSession([
        StubResponse(body={"code": 401, "msg": "未登录"}),
        StubResponse(body={"code": 0, "msg": "", "data": {"id": 1}}),
    ])
    token_manager = StubTokenManager()
    client = client_with_session(session, token_manager)

    response = client.get("/system/user/get")

    assert response.json()["code"] == 0
    assert token_manager.invalidated is True
    assert len(session.calls) == 2
    assert session.calls[1][2]["headers"]["Authorization"] == "Bearer refreshed"


def test_admin_api_prefix_is_not_added_twice():
    session = RecordingSession()
    client = client_with_session(session)

    client.get("/admin-api/system/user/get")

    assert session.calls[0][1] == "http://example.test/admin-api/system/user/get"


def test_set_token_adds_authorization_header():
    session = RecordingSession()
    client = client_with_session(session)
    client.set_token("fixed-token")

    client.get("/system/user/get")

    assert session.calls[0][2]["headers"]["Authorization"] == "Bearer fixed-token"
