"""DeptClient：部门管理接口客户端（RuoYi v3.9.2 原版）。

已实测：
- POST   /system/dept        body: {parentId, deptName, orderNum, status, ...}
- PUT    /system/dept        body: {deptId, ...}
- DELETE /system/dept/{deptId}
- GET    /system/dept/list   params: {deptName?, status?}  返回 {code, rows}
- GET    /system/dept/{deptId}
数据库表：sys_dept(主键dept_id, parentId, del_flag 逻辑删除)
"""
from api_auto.base.base_api import BaseApi


class DeptClient(BaseApi):
    """部门管理接口客户端。"""

    def create(self, data):
        return self.post("/system/dept", json=data)

    def update(self, data):
        return self.put("/system/dept", json=data)

    def delete(self, dept_id):
        return self.request("DELETE", f"/system/dept/{dept_id}")

    def list(self, params=None):
        return self.request("GET", "/system/dept/list", params=params or {})

    def get(self, dept_id):
        return self.request("GET", f"/system/dept/{dept_id}")
