"""MenuClient：菜单管理接口客户端（RuoYi v3.9.2 原版）。

- POST   /system/menu        body: {parentId, menuName, menuType, path, ...}
- PUT    /system/menu        body: {menuId, ...}
- DELETE /system/menu/{menuId}
- GET    /system/menu/list   params: {menuName?, status?}  返回 {code, rows}
- GET    /system/menu/{menuId}
- GET    /system/menu/treeselect   菜单树
数据库表：sys_menu(主键menu_id, menuType: M目录 C菜单 F按钮, del_flag)
"""
from api_auto.base.base_api import BaseApi


class MenuClient(BaseApi):
    """菜单管理接口客户端。"""

    def create(self, data):
        return self.post("/system/menu", json=data)

    def update(self, data):
        return self.put("/system/menu", json=data)

    def delete(self, menu_id):
        return self.request("DELETE", f"/system/menu/{menu_id}")

    def list(self, params=None):
        return self.request("GET", "/system/menu/list", params=params or {})

    def get(self, menu_id):
        return self.request("GET", f"/system/menu/{menu_id}")

    def treeselect(self):
        return self.request("GET", "/system/menu/treeselect")
