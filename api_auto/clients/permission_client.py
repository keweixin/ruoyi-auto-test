"""PermissionClient：权限分配接口客户端（RuoYi v3.9.2 原版）。

- GET  /system/role/menuTreeselect/{roleId}  查询某角色菜单树
- POST /system/role/dataScope  给角色分配数据权限
- 隐含：角色创建/修改时通过 body.menuIds 分配菜单（原版在 role 接口）

数据库表：sys_role_menu(role_id, menu_id)
"""
from api_auto.base.base_api import BaseApi


class PermissionClient(BaseApi):
    """权限分配接口客户端（原版通过 role 接口的 menuIds 分配菜单）。"""

    def role_menu_treeselect(self, role_id):
        """查询某角色的菜单树（含已选 checkedKeys）。"""
        return self.request("GET", f"/system/menu/roleMenuTreeselect/{role_id}")

    def get_role_menu_ids(self, role_id):
        """从菜单树响应中取出已选菜单 id 列表（checkedKeys）。"""
        resp = self.role_menu_treeselect(role_id).json()
        if resp.get("code") == 200:
            return resp.get("checkedKeys", [])
        return []
