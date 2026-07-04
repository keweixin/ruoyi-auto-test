"""RuoYi-Vue-Pro 字典类型与字典数据接口客户端。"""
from api_auto.base.base_api import BaseApi


class DictClient(BaseApi):
    """字典管理接口客户端。"""

    # ===== 字典类型 =====
    def create_type(self, data):
        return self.post("/system/dict-type/create", json=data)

    def update_type(self, data):
        return self.put("/system/dict-type/update", json=data)

    def delete_type(self, dict_id):
        return self.request("DELETE", "/system/dict-type/delete", params={"id": dict_id})

    def get_type(self, dict_id):
        return self.get("/system/dict-type/get", params={"id": dict_id})

    def page_type(self, params):
        return self.get("/system/dict-type/page", params=params)

    def list_type(self, params):
        return self.page_type(params)

    def list_type_all(self):
        return self.get("/system/dict-type/list-all-simple")

    # ===== 字典数据 =====
    def create_data(self, data):
        return self.post("/system/dict-data/create", json=data)

    def update_data(self, data):
        return self.put("/system/dict-data/update", json=data)

    def delete_data(self, dict_code):
        return self.request("DELETE", "/system/dict-data/delete", params={"id": dict_code})

    def page_data(self, params):
        return self.get("/system/dict-data/page", params=params)

    def list_data(self, params):
        return self.page_data(params)

    def get_data(self, dict_code):
        return self.get("/system/dict-data/get", params={"id": dict_code})
