"""RoleClient：角色管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/role/create        body: {name, code, sort, status, remark?}
- PUT    /system/role/update        body: {id, name, code, sort, status, remark?}
- DELETE /system/role/delete?id=    Query 参数 id
- GET    /system/role/page          params: {pageNo, pageSize, name?, code?, status?}  返回 {data: {list,total}}
- GET    /system/role/get?id=       详情
菜单授权走 /system/permission/assign-role-menu。
数据库表：system_role(主键 id, code, deleted 逻辑删除)
"""
from api_auto.base.base_api import BaseApi


class RoleClient(BaseApi):
    """角色管理接口客户端。"""

    def create(self, data):
        return self.post("/system/role/create", json=data)

    def update(self, data):
        return self.put("/system/role/update", json=data)

    def delete(self, role_id):
        return self.request("DELETE", "/system/role/delete", params={"id": role_id})

    def page(self, params):
        return self.request("GET", "/system/role/page", params=params)

    def get(self, role_id):
        return self.request("GET", "/system/role/get", params={"id": role_id})

    def list_all_simple(self):
        return self.request("GET", "/system/role/list-all-simple")
