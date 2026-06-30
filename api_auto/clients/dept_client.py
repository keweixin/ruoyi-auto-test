"""DeptClient：部门管理接口客户端。

已核对源码 DeptController.java（/system/dept）：
- POST   /create     body: {name, parentId, sort, leaderUserId?, phone?, email?, status}
                       ← DeptSaveReqVO（无 remark，有 parentId，根=0）
- PUT    /update     body: {id, name, parentId, sort, ...}
- DELETE /delete?id=
- GET    /list       params: {name?, status?}   ← 部门用 /list 不是 /page（树形，非分页）
- GET    /get?id=

数据库表：system_dept（继承 TenantBaseDO，含 tenantId + deleted）
"""
from api_auto.base.base_api import BaseApi


class DeptClient(BaseApi):
    """部门管理接口客户端。"""

    def create(self, data):
        """新增部门。data: {name, parentId, sort, status, ...}"""
        return self.post("/system/dept/create", json=data)

    def update(self, data):
        """修改部门。data: {id, name, parentId, sort, status, ...}"""
        return self.put("/system/dept/update", json=data)

    def delete(self, dept_id):
        """删除部门。"""
        return self.delete("/system/dept/delete", params={"id": dept_id})

    def list(self, params=None):
        """查询部门列表（树形，非分页）。params: {name?, status?}"""
        return self.get("/system/dept/list", params=params or {})

    def get(self, dept_id):
        """查询部门详情。"""
        return self.get("/system/dept/get", params={"id": dept_id})

    def list_all_simple(self):
        """精简列表（下拉用）。"""
        return self.get("/system/dept/list-all-simple")
