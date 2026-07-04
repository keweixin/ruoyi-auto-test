"""DeptClient：部门管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/dept/create        body: {parentId, name, sort, status, ...}
- PUT    /system/dept/update        body: {id, parentId, name, sort, status, ...}
- DELETE /system/dept/delete?id=    Query 参数 id
- GET    /system/dept/list          params: {name?, status?}  返回 {code, data}
- GET    /system/dept/get?id=       详情
数据库表：system_dept(主键 id, parent_id, deleted 逻辑删除)
"""
from api_auto.base.crud_client import CrudClient


class DeptClient(CrudClient):
    """部门管理接口客户端。CRUD 方法继承自 CrudClient，仅保留 dept 特有的 list。"""

    resource = "/system/dept"

    def list(self, params=None):
        """部门用 list（非分页 page），返回树形列表。"""
        return self.request("GET", f"{self.resource}/list", params=params or {})
