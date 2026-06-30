"""UserClient：用户管理接口客户端。

已核对源码 UserController.java（/system/user）：
- POST   /create          body: UserSaveReqVO {username, password, nickname, deptId, postIds, mobile, ...}
                          ⚠ 无 status / roleIds 字段
- PUT    /update          body: UserSaveReqVO（含 id）
- DELETE /delete?id=
- GET    /page            params: {pageNo, pageSize, username?, mobile?, status?, deptId?}
- GET    /get?id=
- PUT    /update-status   body: {id, status}   ← UserUpdateStatusReqVO（状态修改走这里）
- PUT    /update-password body: {id, password} ← UserUpdatePasswordReqVO（重置密码走这里）

角色绑定：不在 user 接口，走 PermissionClient.assign_user_role。
数据库表：system_users（继承 TenantBaseDO，含 tenantId + deleted）
"""
from api_auto.base.base_api import BaseApi


class UserClient(BaseApi):
    """用户管理接口客户端。"""

    def create(self, data):
        """新增用户。data: {username, password, nickname, deptId, postIds?, mobile?, ...}"""
        return self.post("/system/user/create", json=data)

    def update(self, data):
        """修改用户。data: {id, nickname, deptId, ...}"""
        return self.put("/system/user/update", json=data)

    def delete(self, user_id):
        """删除用户。"""
        return self.delete("/system/user/delete", params={"id": user_id})

    def page(self, params):
        """分页查询用户。params: {pageNo, pageSize, username?, mobile?, status?, deptId?}"""
        return self.get("/system/user/page", params=params)

    def get(self, user_id):
        """查询用户详情。"""
        return self.get("/system/user/get", params={"id": user_id})

    def update_status(self, user_id, status):
        """修改用户状态（0=开启 1=禁用）。"""
        return self.put("/system/user/update-status", json={"id": user_id, "status": status})

    def reset_password(self, user_id, password):
        """重置用户密码。password: 4-16 位。"""
        return self.put("/system/user/update-password", json={"id": user_id, "password": password})
