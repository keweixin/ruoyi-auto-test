"""MenuClient：菜单管理接口客户端。

已核对源码 MenuController.java（/system/menu）：
- POST   /create     body: MenuSaveVO {parentId, name, type, path, icon, sort, status, ...}
- PUT    /update      body: MenuSaveVO（含 id）
- DELETE /delete?id=
- GET    /list        params: {name?, status?}   ← 菜单用 /list 不是 /page（树形，非分页）
- GET    /get?id=

type: 1=目录 2=菜单 3=按钮
数据库表：system_menu（继承 BaseDO + @TenantIgnore，含 deleted，不按租户隔离）
"""
from api_auto.base.base_api import BaseApi


class MenuClient(BaseApi):
    """菜单管理接口客户端。"""

    def create(self, data):
        """新增菜单。data: {parentId, name, type, path, sort, status}"""
        return self.post("/system/menu/create", json=data)

    def update(self, data):
        """修改菜单。data: {id, parentId, name, type, path, sort, status}"""
        return self.put("/system/menu/update", json=data)

    def delete(self, menu_id):
        """删除菜单。"""
        return self.delete("/system/menu/delete", params={"id": menu_id})

    def list(self, params=None):
        """查询菜单列表（树形，非分页）。params: {name?, status?}"""
        return self.get("/system/menu/list", params=params or {})

    def get(self, menu_id):
        """查询菜单详情。"""
        return self.get("/system/menu/get", params={"id": menu_id})

    def list_all_simple(self):
        """精简列表（下拉/授权树用）。"""
        return self.get("/system/menu/list-all-simple")
