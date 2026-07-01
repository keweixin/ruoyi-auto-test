"""JSON Schema 契约校验工具。"""
from jsonschema import validate


_CODE_MSG_PROPERTIES = {
    "code": {"type": "integer"},
    "msg": {"type": "string"},
}

COMMON_RESULT_SCHEMA = {
    "type": "object",
    "required": ["code", "msg"],
    "properties": _CODE_MSG_PROPERTIES,
}

LOGIN_SCHEMA = {
    "type": "object",
    "required": ["code", "msg"],
    "properties": {
        **_CODE_MSG_PROPERTIES,
        # 兼容 RuoYi 原版 data.token 与部分封装返回 token 的两种形态。
        "token": {"type": "string", "minLength": 10},
        "data": {
            "type": "object",
            "required": ["token"],
            "properties": {
                "token": {"type": "string", "minLength": 10},
            },
        },
    },
    "anyOf": [
        {"required": ["token"]},
        {"required": ["data"]},
    ],
}

GET_INFO_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "permissions", "roles", "user"],
    "properties": {
        **_CODE_MSG_PROPERTIES,
        "permissions": {"type": "array", "items": {"type": "string"}},
        "roles": {"type": "array", "items": {"type": "string"}},
        "user": {
            "type": "object",
            "required": ["userId", "userName"],
            "properties": {
                "userId": {"type": "integer"},
                "userName": {"type": "string", "minLength": 1},
            },
        },
    },
}

PAGE_LIST_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "rows", "total"],
    "properties": {
        **_CODE_MSG_PROPERTIES,
        "rows": {"type": "array"},
        "total": {"type": "integer", "minimum": 0},
    },
}

LIST_DATA_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        **_CODE_MSG_PROPERTIES,
        "data": {"type": "array"},
    },
}

DETAIL_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        **_CODE_MSG_PROPERTIES,
        "data": {"type": "object"},
    },
}


def assert_schema(instance, schema):
    validate(instance=instance, schema=schema)
