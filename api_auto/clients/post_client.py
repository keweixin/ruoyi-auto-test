"""PostClient：岗位管理接口客户端（RuoYi v3.9.2 原版）。

- POST   /system/post        body: {postCode, postName, postSort, status, remark}
- PUT    /system/post        body: {postId, ...}
- DELETE /system/post/{postId}
- GET    /system/post/list   params: {pageNum, pageSize, postCode?, postName?, status?}  返回 {total, rows}
- GET    /system/post/{postId}
数据库表：sys_post(主键post_id, postCode唯一, del_flag)
"""
from api_auto.base.base_api import BaseApi


class PostClient(BaseApi):
    """岗位管理接口客户端。"""

    def create(self, data):
        return self.post("/system/post", json=data)

    def update(self, data):
        return self.put("/system/post", json=data)

    def delete(self, post_id):
        return self.request("DELETE", f"/system/post/{post_id}")

    def page(self, params):
        return self.request("GET", "/system/post/list", params=params)

    def get(self, post_id):
        return self.request("GET", f"/system/post/{post_id}")
