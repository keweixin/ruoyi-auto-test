"""CrudClient：声明式 CRUD 客户端基类。

设计说明：
- 标准资源（dept/role/user/post/menu）的 create/update/delete/get/page 接口路径高度同构，
  仅资源前缀不同（如 /system/role vs /system/dept）。
- 子类只需声明 ``resource`` 类属性（如 ``resource = "/system/role"``），
  即可继承得到 create/update/delete(id)/get(id)/page(params) 五个方法。
- 特有接口（如 list-all-simple、权限分配）由子类自行定义。
- 双资源模块（如字典的 dict-type 和 dict-data）可实例化两个 CrudClient。

收益：新增一个标准资源模块的 client 只需声明 resource 前缀，CRUD 方法自动生成，
路径写错的风险消除；现有 6 个 client 共约 35 个一行 CRUD 方法收敛到基类 5 个。
"""
from api_auto.base.base_api import BaseApi


class CrudClient(BaseApi):
    """声明式 CRUD 客户端：子类声明 resource 前缀，自动获得标准 CRUD 方法。"""

    # 子类必须声明，如 "/system/role"
    resource = ""

    def create(self, data):
        """POST /{resource}/create"""
        return self.post(f"{self.resource}/create", json=data)

    def update(self, data):
        """PUT /{resource}/update"""
        return self.put(f"{self.resource}/update", json=data)

    def delete(self, entity_id):
        """DELETE /{resource}/delete?id={entity_id}"""
        return self.request("DELETE", f"{self.resource}/delete", params={"id": entity_id})

    def get(self, entity_id):
        """GET /{resource}/get?id={entity_id}"""
        return self.request("GET", f"{self.resource}/get", params={"id": entity_id})

    # 默认分页参数（集中管理，避免用例里重复写 {"pageNo":1,"pageSize":10}）
    DEFAULT_PAGE_NO = 1
    DEFAULT_PAGE_SIZE = 10

    def page(self, params=None):
        """GET /{resource}/page

        params: 业务过滤字段（如 {"name":"xxx"}），自动补默认分页 pageNo/pageSize。
        也可传完整 params 覆盖默认值。
        """
        full = {"pageNo": self.DEFAULT_PAGE_NO, "pageSize": self.DEFAULT_PAGE_SIZE}
        if params:
            full.update(params)
        return self.request("GET", f"{self.resource}/page", params=full)

    def list_all_simple(self):
        """GET /{resource}/list-all-simple（dept/role/post/menu 共有）。"""
        return self.request("GET", f"{self.resource}/list-all-simple")
