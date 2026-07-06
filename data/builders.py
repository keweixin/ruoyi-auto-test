"""四类常用合法请求体。

这里只准备字典数据。发送请求、断言结果和清理数据仍写在测试用例中，
便于直接看到一条测试的完整执行过程。
"""
from common.environment_utils import get_root_dept_id
from common.faker_utils import fake_mobile, fake_nickname, fake_remark
from common.random_utils import gen_email, gen_name, gen_username


DEFAULT_PASSWORD = "Test123456"
DEFAULT_RESET_PASSWORD = "New123456"


def _with_overrides(data, overrides):
    data.update(overrides)
    return data


def valid_user_data(**overrides):
    return _with_overrides({
        "username": gen_username(),
        "password": DEFAULT_PASSWORD,
        "nickname": fake_nickname(),
        "mobile": fake_mobile(),
        "email": gen_email(),
        "deptId": get_root_dept_id(),
    }, overrides)


def valid_role_data(**overrides):
    return _with_overrides({
        "name": gen_name("auto_role"),
        "code": gen_name("auto_role_code"),
        "sort": 1,
        "status": 0,
        "remark": fake_remark(),
    }, overrides)


def valid_dept_data(**overrides):
    return _with_overrides({
        "name": gen_name("auto_dept"),
        "parentId": 0,
        "sort": 1,
        "status": 0,
        "phone": fake_mobile(),
        "email": gen_email(),
    }, overrides)


def valid_post_data(**overrides):
    return _with_overrides({
        "name": gen_name("auto_post"),
        "code": gen_name("auto_code"),
        "sort": 1,
        "status": 0,
        "remark": fake_remark(),
    }, overrides)
