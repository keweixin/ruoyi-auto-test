"""RuoYi-Vue-Pro 字典类型与字典数据接口客户端。

字典有两类资源（dict-type 和 dict-data），各自的 CRUD 路径同构。
为避免一个 client 里写两套几乎相同的方法，内部用两个 CrudClient 子类委托实现，
对外保留 create_type/create_data 等语义化方法名（兼容现有调用方）。
"""
from api_auto.base.crud_client import CrudClient


class _DictTypeResource(CrudClient):
    resource = "/system/dict-type"


class _DictDataResource(CrudClient):
    resource = "/system/dict-data"


class DictClient(_DictTypeResource):
    """字典管理接口客户端。

    字典类型方法（create_type/update_type/...）继承自 _DictTypeResource；
    字典数据方法（create_data/update_data/...）委托给内部的 _DictDataResource 实例。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = _DictDataResource(*args, **kwargs)

    # ===== 字典类型（create_type 等继承自 CrudClient，重命名以区分数据）=====
    def create_type(self, data):
        return self.create(data)

    def update_type(self, data):
        return self.update(data)

    def delete_type(self, dict_id):
        return self.delete(dict_id)

    def get_type(self, dict_id):
        return self.get(dict_id)

    def page_type(self, params):
        return self.page(params)

    def list_type(self, params):
        """兼容别名：同 page_type。"""
        return self.page(params)

    def list_type_all(self):
        return self.list_all_simple()

    # ===== 字典数据（委托给 _DictDataResource）=====
    def create_data(self, data):
        return self._data.create(data)

    def update_data(self, data):
        return self._data.update(data)

    def delete_data(self, dict_code):
        return self._data.delete(dict_code)

    def page_data(self, params):
        return self._data.page(params)

    def list_data(self, params):
        """兼容别名：同 page_data。"""
        return self._data.page(params)

    def get_data(self, dict_code):
        return self._data.get(dict_code)
