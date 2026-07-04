"""RoleClient：角色管理接口客户端（RuoYi-Vue-Pro / yudao）。

- POST   /system/role/create        body: {name, code, sort, status, remark?}
- PUT    /system/role/update        body: {id, name, code, sort, status, remark?}
- DELETE /system/role/delete?id=    Query 参数 id
- GET    /system/role/page          params: {pageNo, pageSize, name?, code?, status?}  返回 {data: {list,total}}
- GET    /system/role/get?id=       详情
菜单授权走 /system/permission/assign-role-menu。
数据库表：system_role(主键 id, code, deleted 逻辑删除)
"""
from api_auto.base.crud_client import CrudClient


class RoleClient(CrudClient):
    """角色管理接口客户端。CRUD 方法继承自 CrudClient，无特有方法。"""

    resource = "/system/role"
