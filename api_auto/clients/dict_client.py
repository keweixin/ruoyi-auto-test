"""DictClient：字典管理接口客户端（RuoYi v3.9.2 原版）。

已实测：
字典类型（/system/dict/type）：
- POST   /            body: {dictName, dictType, status, remark}   返回 {code:200}
- PUT    /            body: {dictId, dictName, dictType, status}
- DELETE /{dictId}
- GET    /list        params: {pageNum, pageSize, dictName?, dictType?}  返回 {total, rows}
- GET    /{dictId}
字典数据（/system/dict/data）：
- POST   /
- PUT    /
- DELETE /{dictCode}
- GET    /list        params: {dictType}
数据库表：sys_dict_type(主键dict_id) / sys_dict_data(主键dict_code)
"""
from api_auto.base.base_api import BaseApi


class DictClient(BaseApi):
    """字典管理接口客户端。"""

    # ===== 字典类型 =====
    def create_type(self, data):
        return self.post("/system/dict/type", json=data)

    def update_type(self, data):
        return self.put("/system/dict/type", json=data)

    def delete_type(self, dict_id):
        return self.request("DELETE", f"/system/dict/type/{dict_id}")

    def get_type(self, dict_id):
        return self.request("GET", f"/system/dict/type/{dict_id}")

    def list_type(self, params):
        return self.request("GET", "/system/dict/type/list", params=params)

    def list_type_all(self):
        return self.request("GET", "/system/dict/type/optionselect")

    # ===== 字典数据 =====
    def create_data(self, data):
        return self.post("/system/dict/data", json=data)

    def update_data(self, data):
        return self.put("/system/dict/data", json=data)

    def delete_data(self, dict_code):
        return self.request("DELETE", f"/system/dict/data/{dict_code}")

    def list_data(self, params):
        return self.request("GET", "/system/dict/data/list", params=params)

    def get_data(self, dict_code):
        return self.request("GET", f"/system/dict/data/{dict_code}")
