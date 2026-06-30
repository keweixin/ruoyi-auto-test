"""PostClient：岗位管理接口客户端。

已核对源码 PostController.java（/system/post）：
- POST   /create     body: {name, code, sort, status, remark}   ← PostSaveReqVO
- PUT    /update      body: {id, name, code, sort, status, remark}
- DELETE /delete?id=
- GET    /page        params: {pageNo, pageSize, name?, code?, status?}
- GET    /get?id=

数据库表：system_post（继承 BaseDO，含 deleted，参与租户隔离）
"""
from api_auto.base.base_api import BaseApi


class PostClient(BaseApi):
    """岗位管理接口客户端。"""

    def create(self, data):
        """新增岗位。data: {name, code, sort, status, remark}"""
        return self.post("/system/post/create", json=data)

    def update(self, data):
        """修改岗位。data: {id, name, code, sort, status, remark}"""
        return self.put("/system/post/update", json=data)

    def delete(self, post_id):
        """删除岗位。"""
        return self.delete("/system/post/delete", params={"id": post_id})

    def page(self, params):
        """分页查询岗位。params: {pageNo, pageSize, name?, code?, status?}"""
        return self.get("/system/post/page", params=params)

    def get(self, post_id):
        """查询岗位详情。"""
        return self.get("/system/post/get", params={"id": post_id})

    def list_all_simple(self):
        """精简列表（下拉用）。"""
        return self.get("/system/post/list-all-simple")
