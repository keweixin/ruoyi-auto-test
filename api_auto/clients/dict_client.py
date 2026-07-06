"""字典类型和字典数据接口客户端。"""
from api_auto.base.base_api import BaseApi


class DictClient(BaseApi):
    """显式列出字典接口，便于直接对照后端 URL。"""

    def create_type(self, data):
        return self.post("/system/dict-type/create", json=data)

    def update_type(self, data):
        return self.put("/system/dict-type/update", json=data)

    def delete_type(self, dict_id):
        return self.delete("/system/dict-type/delete", params={"id": dict_id})

    def get_type(self, dict_id):
        return self.get("/system/dict-type/get", params={"id": dict_id})

    def page_type(self, params):
        return self.get("/system/dict-type/page", params=params)

    def list_type(self, params):
        return self.page_type(params)

    def list_type_all(self):
        return self.get("/system/dict-type/list-all-simple")

    def create_data(self, data):
        return self.post("/system/dict-data/create", json=data)

    def update_data(self, data):
        return self.put("/system/dict-data/update", json=data)

    def delete_data(self, dict_id):
        return self.delete("/system/dict-data/delete", params={"id": dict_id})

    def get_data(self, dict_id):
        return self.get("/system/dict-data/get", params={"id": dict_id})

    def page_data(self, params):
        return self.get("/system/dict-data/page", params=params)

    def list_data(self, params):
        return self.page_data(params)
