"""RuoYi-Vue-Pro 角色菜单与用户角色权限接口客户端。"""
from api_auto.base.base_api import BaseApi


class PermissionClient(BaseApi):
    """权限分配接口客户端。"""

    def list_role_menus(self, role_id):
        return self.get("/system/permission/list-role-menus", params={"roleId": role_id})

    def assign_role_menu(self, role_id, menu_ids):
        return self.post("/system/permission/assign-role-menu",
                         json={"roleId": role_id, "menuIds": menu_ids})

    def assign_role_data_scope(self, role_id, data_scope, data_scope_dept_ids=None):
        return self.post("/system/permission/assign-role-data-scope",
                         json={"roleId": role_id, "dataScope": data_scope,
                               "dataScopeDeptIds": data_scope_dept_ids or []})

    def list_user_roles(self, user_id):
        return self.get("/system/permission/list-user-roles", params={"userId": user_id})

    def assign_user_role(self, user_id, role_ids):
        return self.post("/system/permission/assign-user-role",
                         json={"userId": user_id, "roleIds": role_ids})

    def get_role_menu_ids(self, role_id):
        """从菜单树响应中取出已选菜单 id 列表（checkedKeys）。"""
        body = self.list_role_menus(role_id).json()
        return body.get("data", []) if body.get("code") == 0 else []
