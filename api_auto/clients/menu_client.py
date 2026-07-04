"""MenuClient：菜单管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/menu/create        body: {parentId, name, type, path, sort, status, ...}
- PUT    /system/menu/update        body: {id, parentId, name, type, path, sort, status, ...}
- DELETE /system/menu/delete?id=    Query 参数 id
- GET    /system/menu/list          params: {name?, status?}  返回 {code, data}
- GET    /system/menu/get?id=       详情
- GET    /system/menu/list-all-simple   菜单简单列表
数据库表：system_menu(主键 id, type: 1目录 2菜单 3按钮, deleted 逻辑删除)
"""
from api_auto.base.base_api import BaseApi


class MenuClient(BaseApi):
    """菜单管理接口客户端。"""

    def create(self, data):
        return self.post("/system/menu/create", json=data)

    def update(self, data):
        return self.put("/system/menu/update", json=data)

    def delete(self, menu_id):
        return self.request("DELETE", "/system/menu/delete", params={"id": menu_id})

    def list(self, params=None):
        return self.request("GET", "/system/menu/list", params=params or {})

    def get(self, menu_id):
        return self.request("GET", "/system/menu/get", params={"id": menu_id})

    def treeselect(self):
        return self.request("GET", "/system/menu/list-all-simple")

    def list_all_simple(self):
        return self.request("GET", "/system/menu/list-all-simple")
