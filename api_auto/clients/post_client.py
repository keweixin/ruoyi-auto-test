"""PostClient：岗位管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/post/create        body: {code, name, sort, status, remark?}
- PUT    /system/post/update        body: {id, code, name, sort, status, remark?}
- DELETE /system/post/delete?id=    Query 参数 id
- GET    /system/post/page          params: {pageNo, pageSize, code?, name?, status?}  返回 {data: {list,total}}
- GET    /system/post/get?id=       详情
数据库表：system_post(主键 id, code 唯一, deleted 逻辑删除)
"""
from api_auto.base.base_api import BaseApi


class PostClient(BaseApi):
    """岗位管理接口客户端。"""

    def create(self, data):
        return self.post("/system/post/create", json=data)

    def update(self, data):
        return self.put("/system/post/update", json=data)

    def delete(self, post_id):
        return self.request("DELETE", "/system/post/delete", params={"id": post_id})

    def page(self, params):
        return self.request("GET", "/system/post/page", params=params)

    def get(self, post_id):
        return self.request("GET", "/system/post/get", params={"id": post_id})

    def list_all_simple(self):
        return self.request("GET", "/system/post/list-all-simple")
