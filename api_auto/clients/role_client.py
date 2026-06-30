"""RoleClient：角色管理接口客户端。

已核对源码 RoleController.java（/system/role）：
- POST   /create     body: {name, code, sort, status, remark}   ← RoleSaveReqVO
- PUT    /update      body: {id, name, code, sort, status, remark}
- DELETE /delete?id=
- GET    /page        params: {pageNo, pageSize, name?, code?, status?}
- GET    /get?id=

⚠ 角色的菜单权限、数据权限不在 role 接口，走 PermissionClient：
  - assign_role_menu（菜单）
  - assign_role_data_scope（数据权限）

数据库表：system_role（继承 TenantBaseDO，含 tenantId + deleted）
"""
from api_auto.base.base_api import BaseApi


class RoleClient(BaseApi):
    """角色管理接口客户端。"""

    def create(self, data):
        """新增角色。data: {name, code, sort, status, remark}"""
        return self.post("/system/role/create", json=data)

    def update(self, data):
        """修改角色。data: {id, name, code, sort, status, remark}"""
        return self.put("/system/role/update", json=data)

    def delete(self, role_id):
        """删除角色。"""
        return self.delete("/system/role/delete", params={"id": role_id})

    def page(self, params):
        """分页查询角色。params: {pageNo, pageSize, name?, code?, status?}"""
        return self.get("/system/role/page", params=params)

    def get(self, role_id):
        """查询角色详情。"""
        return self.get("/system/role/get", params={"id": role_id})

    def list_all_simple(self):
        """精简列表（下拉用）。"""
        return self.get("/system/role/list-all-simple")
