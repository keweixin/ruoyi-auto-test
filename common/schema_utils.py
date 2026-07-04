"""JSON Schema 契约校验工具。"""
from jsonschema import validate


_CODE_MSG_PROPERTIES = {
    "code": {"type": "integer"},
    "msg": {"type": "string"},
}

LOGIN_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        **_CODE_MSG_PROPERTIES,
        "data": {
            "type": "object",
            "required": ["accessToken"],
            "properties": {
                "accessToken": {"type": "string", "minLength": 10},
                "refreshToken": {"type": "string", "minLength": 10},
                "userId": {"type": "integer"},
                "expiresTime": {"type": "integer"},
            },
        },
    },
}

GET_INFO_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        **_CODE_MSG_PROPERTIES,
        "data": {
            "type": "object",
            "required": ["permissions", "roles", "user", "menus"],
            "properties": {
                "permissions": {"type": "array", "items": {"type": "string"}},
                "roles": {"type": "array"},
                "menus": {"type": "array"},
                "user": {"type": "object"},
            },
        },
    },
}

PAGE_LIST_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        **_CODE_MSG_PROPERTIES,
        "data": {
            "type": "object",
            "required": ["list", "total"],
            "properties": {
                "list": {"type": "array"},
                "total": {"type": "integer", "minimum": 0},
            },
        },
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
