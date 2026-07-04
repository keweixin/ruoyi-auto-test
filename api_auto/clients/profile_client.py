"""ProfileClient：个人中心接口客户端（RuoYi-Vue-Pro / yudao）。

- GET  /system/user/profile/get              获取当前登录用户个人信息
- PUT  /system/user/profile/update           修改个人信息（nickname/email 等）
- PUT  /system/user/profile/update-password  修改个人密码（oldPassword + newPassword）

个人中心是每个登录用户都会用的入口，区别于管理员视角的 user 管理。
"""
from api_auto.base.base_api import BaseApi


class ProfileClient(BaseApi):
    """个人中心接口客户端。

    注意：BaseApi 已有 get(path) 方法，本类用 get_profile/update_profile 命名避免覆盖。
    """

    def get_profile(self):
        """获取当前登录用户的个人信息。"""
        return self.get("/system/user/profile/get")

    def update_profile(self, data):
        """修改个人信息（nickname/email/mobile 等可改字段）。"""
        return self.put("/system/user/profile/update", json=data)

    def update_password(self, old_password, new_password):
        """修改个人密码（需提供旧密码）。"""
        return self.put("/system/user/profile/update-password", json={
            "oldPassword": old_password,
            "newPassword": new_password,
        })
