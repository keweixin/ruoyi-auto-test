"""LogClient：操作日志 + 登录日志查询客户端（RuoYi-Vue-Pro / yudao）。

- GET /system/operate-log/page  操作日志分页  params: {pageNo, pageSize, type?, userNickname?, ...}
- GET /system/login-log/page     登录日志分页  params: {pageNo, pageSize, username?, status?, ...}

日志只读查询，无写操作，无副作用，适合做只读验证。
"""
from api_auto.base.crud_client import CrudClient


class OperateLogClient(CrudClient):
    """操作日志客户端。只读查询（page 继承自 CrudClient）。"""

    resource = "/system/operate-log"


class LoginLogClient(CrudClient):
    """登录日志客户端。只读查询（page 继承自 CrudClient）。"""

    resource = "/system/login-log"
