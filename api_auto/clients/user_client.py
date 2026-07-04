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
from api_auto.base.base_api import BaseApi


class UserClient(BaseApi):
    """用户管理接口客户端。"""

    def create(self, data):
        return self.post("/system/user/create", json=data)

    def update(self, data):
        return self.put("/system/user/update", json=data)

    def delete(self, user_id):
        return self.request("DELETE", "/system/user/delete", params={"id": user_id})

    def page(self, params):
        return self.request("GET", "/system/user/page", params=params)

    def get(self, user_id):
        return self.request("GET", "/system/user/get", params={"id": user_id})

    def update_status(self, user_id, status):
        return self.put("/system/user/update-status", json={"id": user_id, "status": status})

    def change_status(self, user_id, status):
        return self.update_status(user_id, status)

    def reset_password(self, user_id, password):
        """重置用户密码。"""
        return self.put("/system/user/update-password", json={"id": user_id, "password": password})
