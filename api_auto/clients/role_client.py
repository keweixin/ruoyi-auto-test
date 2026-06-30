"""RoleClient：角色管理接口客户端（RuoYi v3.9.2 原版）。

- POST   /system/role        body: {roleName, roleKey, roleSort, status, remark, menuIds?}
- PUT    /system/role        body: {roleId, ...}
- DELETE /system/role/{roleId}
- GET    /system/role/list   params: {pageNum, pageSize, roleName?, roleKey?, status?}  返回 {total, rows}
- GET    /system/role/{roleId}
数据库表：sys_role(主键role_id, roleKey, del_flag)
"""
from api_auto.base.base_api import BaseApi


class RoleClient(BaseApi):
    """角色管理接口客户端。"""

    def create(self, data):
        return self.post("/system/role", json=data)

    def update(self, data):
        return self.put("/system/role", json=data)

    def delete(self, role_id):
        return self.request("DELETE", f"/system/role/{role_id}")

    def page(self, params):
        return self.request("GET", "/system/role/list", params=params)

    def get(self, role_id):
        return self.request("GET", f"/system/role/{role_id}")
