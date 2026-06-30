"""PermissionClient：权限分配接口客户端（角色↔菜单、用户↔角色）。

已核对源码 PermissionController.java（/system/permission）：
- GET  /list-role-menus?roleId=           查询某角色的菜单 id 集合（返回 Set<Long>）
- POST /assign-role-menu   body: {roleId, menuIds}   ← 给角色分配菜单权限
- POST /assign-role-data-scope  body: {roleId, dataScope, dataScopeDeptIds}
- GET  /list-user-roles?userId=          查询某用户的角色 id 集合
- POST /assign-user-role   body: {userId, roleIds}   ← 给用户分配角色

数据库表：
- system_role_menu（角色菜单关系，继承 TenantBaseDO）
- system_user_role（用户角色关系，继承 BaseDO）
"""
from api_auto.base.base_api import BaseApi


class PermissionClient(BaseApi):
    """权限分配接口客户端。"""

    # ===== 角色 ↔ 菜单 =====
    def list_role_menus(self, role_id):
        """查询某角色已分配的菜单 id 集合。"""
        return self.get("/system/permission/list-role-menus", params={"roleId": role_id})

    def assign_role_menu(self, role_id, menu_ids):
        """给角色分配菜单权限。menu_ids: list[int]。"""
        return self.post("/system/permission/assign-role-menu",
                         json={"roleId": role_id, "menuIds": menu_ids})

    def assign_role_data_scope(self, role_id, data_scope, data_scope_dept_ids=None):
        """给角色分配数据权限。data_scope 见 DataScopeEnum。"""
        return self.post("/system/permission/assign-role-data-scope",
                         json={"roleId": role_id, "dataScope": data_scope,
                               "dataScopeDeptIds": data_scope_dept_ids or []})

    # ===== 用户 ↔ 角色 =====
    def list_user_roles(self, user_id):
        """查询某用户已绑定的角色 id 集合。"""
        return self.get("/system/permission/list-user-roles", params={"userId": user_id})

    def assign_user_role(self, user_id, role_ids):
        """给用户分配角色。role_ids: list[int]。"""
        return self.post("/system/permission/assign-user-role",
                         json={"userId": user_id, "roleIds": role_ids})
