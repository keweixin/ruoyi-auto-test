"""UserClient：用户管理接口客户端（RuoYi v3.9.2 原版）。

已实测：
- POST   /system/user        body: {userName, nickName, password, phonenumber, deptId, ...}
- PUT    /system/user        body: {userId, ...}
- DELETE /system/user/{userId}  或 /system/user/{userIds} (支持逗号分隔)
- GET    /system/user/list   params: {pageNum, pageSize, userName?, phonenumber?, status?}  返回 {total, rows}
- GET    /system/user/{userId}
- PUT    /system/user/changeStatus   body: {userId, status}    修改状态
- PUT    /system/user/resetPwd       body: {userId, password} 重置密码
数据库表：sys_user(主键user_id, userName, phonenumber, del_flag)
"""
from api_auto.base.base_api import BaseApi


class UserClient(BaseApi):
    """用户管理接口客户端。"""

    def create(self, data):
        return self.post("/system/user", json=data)

    def update(self, data):
        return self.put("/system/user", json=data)

    def delete(self, user_id):
        return self.request("DELETE", f"/system/user/{user_id}")

    def page(self, params):
        return self.request("GET", "/system/user/list", params=params)

    def get(self, user_id):
        return self.request("GET", f"/system/user/{user_id}")

    def change_status(self, user_id, status):
        """修改用户状态（0=正常 1=停用）。"""
        return self.put("/system/user/changeStatus", json={"userId": user_id, "status": status})

    def reset_password(self, user_id, password):
        """重置用户密码。"""
        return self.put("/system/user/resetPwd", json={"userId": user_id, "password": password})
