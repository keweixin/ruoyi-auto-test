"""纯接口联动测试（不依赖前端，前端未就绪时可验证联动逻辑）。

价值：体现接口造数 → 接口验证 → 数据库校验 → 接口清理 的完整闭环。
覆盖：
- DICT_API_FLOW: 接口建字典 → 接口查验证 → DB 校验 → 接口删
- USER_API_FLOW: 接口建用户 → 接口查验证 → DB 校验 → 接口删
- ROLE_API_FLOW: 接口建角色分配菜单 → 接口查角色菜单 → DB 校验中间表 → 接口删
"""
import allure
import pytest

from common.config import cfg
from common import db_utils
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_text
from common.random_utils import gen_name, gen_mobile
from api_auto.clients.dict_client import DictClient
from api_auto.clients.user_client import UserClient
from api_auto.clients.role_client import RoleClient
from api_auto.clients.permission_client import PermissionClient


@allure.feature("纯接口联动")
class TestApiFlow:

    @allure.title("DICT_API_FLOW 接口造字典→接口查→DB校验→清理")
    @pytest.mark.flow
    def test_dict_api_flow(self, dict_client):
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        # 造数
        assert_api_ok(dict_client.create_type({"dictName": name, "dictType": type_, "status": "0", "remark": "flow"}).json())
        rows = dict_client.list_type({"dictType": type_}).json()["rows"]
        dict_id = rows[0]["dictId"]
        try:
            # 接口验证
            assert any(r["dictName"] == name for r in rows), "接口未查到造的字典"
            # DB 校验
            row = db_utils.query_one("SELECT dict_name, status FROM sys_dict_type WHERE dict_id=%s", (dict_id,))
            assert row and row["dict_name"] == name, "DB 未落库"
            attach_text("字典 DB 记录", str(row))
        finally:
            assert_api_ok(dict_client.delete_type(dict_id).json())

    @allure.title("USER_API_FLOW 接口造用户→接口查→DB校验→清理")
    @pytest.mark.flow
    def test_user_api_flow(self, user_client):
        username = gen_name("auto_flow")
        assert_api_ok(user_client.create({
            "userName": username, "nickName": "联动用户",
            "password": "admin123", "phonenumber": gen_mobile(), "deptId": 100, "status": "0"
        }).json())
        rows = user_client.page({"userName": username}).json()["rows"]
        uid = rows[0]["userId"]
        try:
            assert any(r["userId"] == uid for r in rows), "接口未查到造的用户"
            row = db_utils.query_one("SELECT user_name, del_flag FROM sys_user WHERE user_id=%s", (uid,))
            assert row and row["user_name"] == username and row["del_flag"] == "0"
            attach_text("用户 DB 记录", str(row))
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("ROLE_API_FLOW 接口建角色分配菜单→查关系→DB校验→清理")
    @pytest.mark.flow
    def test_role_api_flow(self, role_client, permission_client):
        name = gen_name("auto_flow")
        assert_api_ok(role_client.create({
            "roleName": name, "roleKey": gen_name("auto_key"), "roleSort": 1, "status": "0", "menuIds": [1, 2, 3]
        }).json())
        rows = role_client.page({"roleName": name}).json()["rows"]
        rid = rows[0]["roleId"]
        try:
            ids = permission_client.get_role_menu_ids(rid)
            assert set([1, 2, 3]).issubset(set(ids)), f"菜单未分配 实际={ids}"
            db_rows = db_utils.query_all("SELECT menu_id FROM sys_role_menu WHERE role_id=%s", (rid,))
            assert set([1, 2, 3]).issubset({r["menu_id"] for r in db_rows}), "中间表关系缺失"
            attach_text("角色菜单 DB 记录", str(db_rows))
        finally:
            assert_api_ok(role_client.delete(rid).json())
