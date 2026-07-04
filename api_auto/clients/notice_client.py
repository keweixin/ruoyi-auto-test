"""NoticeClient：通知公告接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/notice/create   body: {title, type, content, status}
- PUT    /system/notice/update   body: {id, title, type, content, status}
- DELETE /system/notice/delete?id=
- GET    /system/notice/page     params: {pageNo, pageSize, title?}
- GET    /system/notice/get?id=

通知公告是标准 CRUD，直接继承 CrudClient。
"""
from api_auto.base.crud_client import CrudClient


class NoticeClient(CrudClient):
    """通知公告接口客户端。CRUD 方法继承自 CrudClient。"""

    resource = "/system/notice"
