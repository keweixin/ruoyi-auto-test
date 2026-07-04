"""DeptClient：部门管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/dept/create        body: {parentId, name, sort, status, ...}
- PUT    /system/dept/update        body: {id, parentId, name, sort, status, ...}
- DELETE /system/dept/delete?id=    Query 参数 id
- GET    /system/dept/list          params: {name?, status?}  返回 {code, data}
- GET    /system/dept/get?id=       详情
数据库表：system_dept(主键 id, parent_id, deleted 逻辑删除)
"""
from api_auto.base.base_api import BaseApi


class DeptClient(BaseApi):
    """部门管理接口客户端。"""

    def create(self, data):
        return self.post("/system/dept/create", json=data)

    def update(self, data):
        return self.put("/system/dept/update", json=data)

    def delete(self, dept_id):
        return self.request("DELETE", "/system/dept/delete", params={"id": dept_id})

    def list(self, params=None):
        return self.request("GET", "/system/dept/list", params=params or {})

    def get(self, dept_id):
        return self.request("GET", "/system/dept/get", params={"id": dept_id})

    def list_all_simple(self):
        return self.request("GET", "/system/dept/list-all-simple")
