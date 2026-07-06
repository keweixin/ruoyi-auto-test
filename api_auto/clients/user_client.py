"""UserClient：用户管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/user/create             body: {username, nickname, password, mobile, deptId, ...}
- PUT    /system/user/update             body: {id, username, nickname, mobile, deptId, ...}
- DELETE /system/user/delete?id=         Query 参数 id
- GET    /system/user/page               params: {pageNo, pageSize, username?, mobile?, status?} 返回 {data: {list,total}}
- GET    /system/user/get?id=            详情
- PUT    /system/user/update-status      body: {id, status}
- PUT    /system/user/update-password    body: {id, password}
数据库表：system_users(主键 id, username, mobile, deleted 逻辑删除)
"""
from api_auto.base.crud_client import CrudClient


class UserClient(CrudClient):
    """用户管理接口客户端。CRUD 继承自 CrudClient，保留 update_status / reset_password 特有方法。"""

    resource = "/system/user"

    def update_status(self, user_id, status):
        """修改用户状态（启用/禁用）。"""
        return self.put(f"{self.resource}/update-status", json={"id": user_id, "status": status})

    def reset_password(self, user_id, password):
        """重置用户密码。"""
        return self.put(f"{self.resource}/update-password", json={"id": user_id, "password": password})
