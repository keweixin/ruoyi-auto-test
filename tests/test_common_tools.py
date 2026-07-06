import json

import pytest
import requests

from common import db_utils
from common.assert_utils import (
    assert_not_found,
    assert_page_result,
    assert_response_fail,
    assert_response_ok,
)
from common.faker_utils import fake_email, fake_mobile, fake_nickname, fake_remark
from data.builders import (
    valid_dept_data,
    valid_post_data,
    valid_role_data,
    valid_user_data,
)
from common.yaml_utils import load_case_list, load_yaml


pytestmark = pytest.mark.framework


def _response(body, status=200):
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(body, ensure_ascii=False).encode("utf-8")
    response.headers["Content-Type"] = "application/json"
    return response


def test_faker_helpers_generate_expected_formats():
    assert fake_nickname()
    assert "@" in fake_email()
    assert len(fake_mobile()) == 11 and fake_mobile()[:2] in {"13", "15", "18"}
    assert fake_remark()


def test_small_data_builders_support_field_overrides(monkeypatch):
    monkeypatch.setattr("data.builders.get_root_dept_id", lambda: 100)
    assert valid_user_data(mobile="123")["mobile"] == "123"
    assert valid_user_data()["deptId"] == 100
    assert valid_role_data(status=1)["status"] == 1
    assert valid_dept_data(name="auto_custom")["name"] == "auto_custom"
    assert valid_post_data(sort=9)["sort"] == 9


def test_yaml_loader_reports_missing_empty_and_duplicate_cases(tmp_path):
    with pytest.raises(FileNotFoundError, match="YAML 文件不存在"):
        load_yaml(tmp_path / "missing.yaml")

    empty = tmp_path / "empty.yaml"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="YAML 内容为空"):
        load_yaml(empty)

    duplicate = tmp_path / "duplicate.yaml"
    duplicate.write_text(
        "module:\n  create_cases:\n    - {case_id: same}\n    - {case_id: same}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="case_id 重复"):
        load_case_list(duplicate, "module")


def test_response_assertions_return_body_and_check_common_shapes():
    ok = assert_response_ok(_response({"code": 0, "msg": "", "data": True}), "成功接口")
    assert ok["data"] is True
    failed = assert_response_fail(
        _response({"code": 400, "msg": "手机号格式错误", "data": None}),
        "异常接口",
        contains="手机",
    )
    assert failed["code"] == 400
    assert_page_result({"code": 0, "msg": "", "data": {"list": [{}], "total": 1}}, min_total=1)
    assert_not_found({"code": 404, "msg": "不存在", "data": None})


def test_database_assertion_helpers(monkeypatch):
    monkeypatch.setattr(db_utils, "query_one", lambda sql, params=None: {"status": 1})
    assert db_utils.assert_db_exists("SELECT 1") == {"status": 1}
    assert db_utils.assert_db_field("SELECT status", None, "status", 1) == {"status": 1}
