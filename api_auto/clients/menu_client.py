"""MenuClient：菜单管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/menu/create        body: {parentId, name, type, path, sort, status, ...}
- PUT    /system/menu/update        body: {id, parentId, name, type, path, sort, status, ...}
- DELETE /system/menu/delete?id=    Query 参数 id
- GET    /system/menu/list          params: {name?, status?}  返回 {code, data}
- GET    /system/menu/get?id=       详情
- GET    /system/menu/list-all-simple   菜单简单列表
数据库表：system_menu(主键 id, type: 1目录 2菜单 3按钮, deleted 逻辑删除)
"""
from api_auto.base.crud_client import CrudClient


class MenuClient(CrudClient):
    """菜单管理接口客户端。CRUD 继承自 CrudClient，保留 menu 特有的 list。"""

    resource = "/system/menu"

    def list(self, params=None):
        """菜单用 list（非分页 page），返回树形列表。"""
        return self.request("GET", f"{self.resource}/list", params=params or {})

    def treeselect(self):
        """菜单下拉树（同 list_all_simple，保留语义化方法名）。"""
        return self.list_all_simple()
