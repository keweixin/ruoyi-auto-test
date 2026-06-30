"""DictClient：字典管理接口客户端。

已核对源码 DictTypeController.java / DictDataController.java：

字典类型（/system/dict-type）：
- POST   /create     body: {name, type, status, remark}        ← DictTypeSaveReqVO（无 sort）
- PUT    /update     body: {id, name, type, status, remark}
- DELETE /delete?id=
- GET    /page       params: {pageNo, pageSize, name?, type?}
- GET    /get?id=
- GET    /list-all-simple

字典数据（/system/dict-data）：
- POST   /create     body: {sort, label, value, dictType, status, ...}  ← DictDataSaveReqVO（字段名 dictType）
- PUT    /update
- DELETE /delete?id=
- GET    /page
- GET    /get?id=

数据库表：system_dict_type / system_dict_data（均有 deleted 逻辑删除字段，@TenantIgnore 不按租户隔离）
"""
from api_auto.base.base_api import BaseApi


class DictClient(BaseApi):
    """字典管理接口客户端。"""

    # ===== 字典类型 =====
    def create_type(self, data):
        """新增字典类型。data: {name, type, status, remark}"""
        return self.post("/system/dict-type/create", json=data)

    def update_type(self, data):
        """修改字典类型。data: {id, name, type, status, remark}"""
        return self.put("/system/dict-type/update", json=data)

    def delete_type(self, dict_type_id):
        """删除字典类型（query 参数 id）。"""
        return self.delete("/system/dict-type/delete", params={"id": dict_type_id})

    def get_type(self, dict_type_id):
        """查询字典类型详情。"""
        return self.get("/system/dict-type/get", params={"id": dict_type_id})

    def page_type(self, params):
        """分页查询字典类型。params: {pageNo, pageSize, name?, type?}"""
        return self.get("/system/dict-type/page", params=params)

    def list_all_simple_type(self):
        """精简列表（下拉用）。"""
        return self.get("/system/dict-type/list-all-simple")

    # ===== 字典数据 =====
    def create_data(self, data):
        """新增字典数据。data: {sort, label, value, dictType, status}"""
        return self.post("/system/dict-data/create", json=data)

    def update_data(self, data):
        """修改字典数据。data: {id, sort, label, value, dictType, status}"""
        return self.put("/system/dict-data/update", json=data)

    def delete_data(self, dict_data_id):
        """删除字典数据。"""
        return self.delete("/system/dict-data/delete", params={"id": dict_data_id})

    def page_data(self, params):
        """分页查询字典数据。params: {pageNo, pageSize, dictType?}"""
        return self.get("/system/dict-data/page", params=params)

    def get_data(self, dict_data_id):
        """查询字典数据详情。"""
        return self.get("/system/dict-data/get", params={"id": dict_data_id})
