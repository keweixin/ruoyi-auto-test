from pathlib import Path

import pytest
import requests

from api_auto.base import base_api
from api_auto.base.base_api import BaseApi


class StubResponse:
    def __init__(self, chunks=(), status_code=200, body=None):
        self.status_code = status_code
        self.text = "{}"
        self._chunks = chunks
        self._body = body or {"code": 0, "msg": "", "data": True}

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)

    def iter_content(self, chunk_size):
        assert chunk_size > 0
        return iter(self._chunks)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class RecordingSession:
    def __init__(self, response=None, error=None):
        self.response = response or StubResponse()
        self.error = error
        self.calls = []
        self.uploaded_content = None
        self.closed = False
        self.adapters = {}

    def mount(self, prefix, adapter):
        self.adapters[prefix] = adapter

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        files = kwargs.get("files")
        if files:
            self.uploaded_content = files["file"][1].read()
        if self.error:
            raise self.error
        return self.response

    def close(self):
        self.closed = True


class SequenceSession(RecordingSession):
    def __init__(self, responses):
        super().__init__()
        self.responses = iter(responses)

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return next(self.responses)


class StubTokenManager:
    def __init__(self):
        self.token = "expired"
        self.invalidated = False

    def get_access_token(self):
        return "refreshed" if self.invalidated else self.token

    def invalidate_access_token(self):
        self.invalidated = True


def test_request_reuses_injected_session_and_applies_default_timeout():
    session = RecordingSession()
    client = BaseApi("http://example.test", session=session, timeout=(1, 5))

    client.get("/system/user/get", params={"id": 1})
    client.get("/system/user/get", timeout=9)

    assert len(session.calls) == 2
    assert session.calls[0][2]["timeout"] == (1, 5)
    assert session.calls[1][2]["timeout"] == 9


def test_default_session_retries_only_safe_methods():
    client = BaseApi("http://example.test", retry_total=2, backoff_factor=0.1)

    retry = client.session.get_adapter("http://").max_retries

    assert retry.total == 2
    assert retry.status == 2
    assert retry.read == 0
    assert retry.allowed_methods == frozenset({"GET", "HEAD", "OPTIONS"})
    assert set(retry.status_forcelist) == {429, 502, 503, 504}


def test_request_converts_requests_exception_without_leaking_payload():
    session = RecordingSession(error=requests.Timeout("secret-body"))
    client = BaseApi("http://example.test", session=session)

    with pytest.raises(base_api.ApiRequestError) as exc_info:
        client.post("/system/user/create", json={"password": "secret-body"})

    message = str(exc_info.value)
    assert "POST" in message
    assert "/admin-api/system/user/create" in message
    assert "secret-body" not in message


def test_request_preserves_single_token_refresh_retry():
    session = SequenceSession(
        [
            StubResponse(status_code=200, body={"code": 401, "msg": "未登录"}),
            StubResponse(body={"code": 0, "msg": "", "data": {"id": 1}}),
        ]
    )
    token_manager = StubTokenManager()
    client = BaseApi(
        "http://example.test",
        token_manager=token_manager,
        session=session,
    )

    response = client.get("/system/user/get")

    assert response.json()["code"] == 0
    assert token_manager.invalidated is True
    assert len(session.calls) == 2
    assert session.calls[1][2]["headers"]["Authorization"] == "Bearer refreshed"


def test_upload_opens_file_in_binary_mode_and_sends_multipart(tmp_path):
    source = tmp_path / "users.csv"
    source.write_bytes(b"name\nalice\n")
    session = RecordingSession()
    client = BaseApi("http://example.test", session=session)

    client.upload("/infra/file/upload", source, data={"folder": "test"})

    _, _, kwargs = session.calls[0]
    assert kwargs["data"] == {"folder": "test"}
    assert kwargs["files"]["file"][0] == "users.csv"
    assert session.uploaded_content == b"name\nalice\n"


def test_download_streams_to_a_temporary_file_then_replaces_destination(tmp_path):
    session = RecordingSession(response=StubResponse(chunks=(b"ab", b"", b"cd")))
    client = BaseApi("http://example.test", session=session)
    destination = tmp_path / "exports" / "users.csv"

    result = client.download("/infra/file/download", destination, chunk_size=2)

    assert result == Path(destination)
    assert destination.read_bytes() == b"abcd"
    assert not destination.with_name("users.csv.part").exists()
    assert session.calls[0][2]["stream"] is True


def test_close_only_closes_a_session_owned_by_base_api(monkeypatch):
    injected = RecordingSession()
    owned = RecordingSession()
    monkeypatch.setattr(base_api.requests, "Session", lambda: owned)
    injected_client = BaseApi("http://example.test", session=injected)
    owned_client = BaseApi("http://example.test")

    injected_client.close()
    owned_client.close()

    assert injected.closed is False
    assert owned.closed is True
