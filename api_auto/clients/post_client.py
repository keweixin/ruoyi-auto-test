"""PostClient：岗位管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/post/create        body: {code, name, sort, status, remark?}
- PUT    /system/post/update        body: {id, code, name, sort, status, remark?}
- DELETE /system/post/delete?id=    Query 参数 id
- GET    /system/post/page          params: {pageNo, pageSize, code?, name?, status?}  返回 {data: {list,total}}
- GET    /system/post/get?id=       详情
数据库表：system_post(主键 id, code 唯一, deleted 逻辑删除)
"""
from api_auto.base.crud_client import CrudClient


class PostClient(CrudClient):
    """岗位管理接口客户端。CRUD 方法继承自 CrudClient，无特有方法。"""

    resource = "/system/post"
