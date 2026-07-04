"""常用合法请求体与造数 helper；只封装重复最多的四类数据。

设计说明：
- valid_xxx_data：返回合法请求体（带随机化唯一字段），支持 overrides；
- create_xxx：调用 valid_xxx_data + client.create + assert_api_ok，返回 CreatedEntity。
  消除各 testclass 里重复的 _create_xxx 辅助方法。
- with_created：上下文管理器，自动创建 + 退出时 best-effort 删除，
  消除用例里重复的 try/finally create-delete 模板。
"""
from collections import namedtuple
from contextlib import contextmanager

from common.assert_utils import assert_api_ok
from common.environment_utils import get_root_dept_id
from common.faker_utils import fake_mobile, fake_nickname, fake_remark
from common.logger import log
from common.random_utils import gen_email, gen_name, gen_username

# 统一的默认测试密码（避免散落硬编码）
DEFAULT_PASSWORD = "Test123456"
DEFAULT_RESET_PASSWORD = "New123456"

# 统一的造数返回结构：id + 关键标识字段，调用方按需取
CreatedEntity = namedtuple("CreatedEntity", ["id", "name", "code", "extra"])


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


def create_user(user_client, **overrides):
    """创建测试用户，返回 CreatedEntity(id=uid, name=username, extra={'password':...})。"""
    data = valid_user_data(**overrides)
    body = user_client.create(data).json()
    assert_api_ok(body, "创建用户")
    return CreatedEntity(id=body["data"], name=data["username"], code=None,
                         extra={"password": data["password"], "mobile": data["mobile"],
                                "nickname": data["nickname"]})


def create_role(role_client, **overrides):
    """创建测试角色，返回 CreatedEntity(id=rid, name=name, code=code)。"""
    data = valid_role_data(**overrides)
    body = role_client.create(data).json()
    assert_api_ok(body, "创建角色")
    return CreatedEntity(id=body["data"], name=data["name"], code=data["code"], extra={})


def create_dept(dept_client, **overrides):
    """创建测试部门，返回 CreatedEntity(id=did, name=name)。"""
    data = valid_dept_data(**overrides)
    body = dept_client.create(data).json()
    assert_api_ok(body, "创建部门")
    return CreatedEntity(id=body["data"], name=data["name"], code=None, extra={})


def create_post(post_client, **overrides):
    """创建测试岗位，返回 CreatedEntity(id=pid, name=name, code=code)。"""
    data = valid_post_data(**overrides)
    body = post_client.create(data).json()
    assert_api_ok(body, "创建岗位")
    return CreatedEntity(id=body["data"], name=data["name"], code=data["code"], extra={})


@contextmanager
def with_created_entity(client, entity_type, **overrides):
    """上下文管理器：自动创建 + 退出时 best-effort 删除。

    用法：
        with with_created_entity(role_client, "role") as entity:
            # entity.id, entity.name 可用
            ...

    entity_type: "user" / "role" / "dept" / "post"
    清理失败只记 warning，不掩盖用例断言结果。
    """
    creators = {
        "user": create_user,
        "role": create_role,
        "dept": create_dept,
        "post": create_post,
    }
    if entity_type not in creators:
        raise ValueError(f"不支持的实体类型: {entity_type}，可选: {list(creators)}")
    entity = creators[entity_type](client, **overrides)
    try:
        yield entity
    finally:
        try:
            client.delete(entity.id)
        except Exception as exc:
            log.warning("清理 %s id=%s 失败(不影响用例结果): %s", entity_type, entity.id, exc)

