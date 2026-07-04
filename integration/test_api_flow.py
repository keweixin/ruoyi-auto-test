"""纯接口联动测试（RuoYi-Vue-Pro / yudao）。

价值：体现接口造数 → 接口验证 → 数据库校验 → 接口清理 的完整闭环。
覆盖：
- DICT_API_FLOW: 接口建字典 → 接口查验证 → DB 校验 → 接口删
- USER_API_FLOW: 接口建用户 → 接口查验证 → DB 校验 → 接口删
- ROLE_API_FLOW: 接口建角色分配菜单 → 接口查角色菜单 → DB 校验中间表 → 接口删
"""
import allure
import pytest

from common import db_utils
from common.assert_utils import assert_api_ok
from common.allure_utils import attach_text
from common.random_utils import gen_name, gen_mobile, gen_username
from common.test_data import DEFAULT_PASSWORD


@allure.feature("纯接口联动")
@pytest.mark.flow
class TestApiFlow:

    @allure.title("DICT_API_FLOW 接口造字典→接口查→DB校验→清理")
    @pytest.mark.flow
    def test_dict_api_flow(self, dict_client):
        name = gen_name("auto_flow")
        type_ = gen_name("auto_flow_type")
        new_id = dict_client.create_type(
            {"name": name, "type": type_, "status": 0, "remark": "flow"}
        ).json()["data"]
        try:
            body = dict_client.page_type({"pageNo": 1, "pageSize": 10, "type": type_}).json()
            assert_api_ok(body)
            rows = body["data"]["list"]
            assert any(r["name"] == name and r["id"] == new_id for r in rows), "接口未查到造的字典"
            row = db_utils.query_one(
                "SELECT name, type, status, deleted + 0 AS deleted FROM system_dict_type WHERE id=%s",
                (new_id,),
            )
            assert row and row["name"] == name and row["deleted"] == 0, "DB 未落库"
            attach_text("字典 DB 记录", str(row))
        finally:
            assert_api_ok(dict_client.delete_type(new_id).json())

    @allure.title("USER_API_FLOW 接口造用户→接口查→DB校验→清理")
    @pytest.mark.flow
    def test_user_api_flow(self, user_client):
        username = gen_username()
        uid = user_client.create({
            "username": username,
            "nickname": "联动用户",
            "password": DEFAULT_PASSWORD,
            "mobile": gen_mobile(),
            "deptId": 100,
        }).json()["data"]
        try:
            body = user_client.page({"pageNo": 1, "pageSize": 10, "username": username}).json()
            assert_api_ok(body)
            rows = body["data"]["list"]
            assert any(r["id"] == uid for r in rows), "接口未查到造的用户"
            row = db_utils.query_one(
                "SELECT username, deleted + 0 AS deleted FROM system_users WHERE id=%s",
                (uid,),
            )
            assert row and row["username"] == username and row["deleted"] == 0
            attach_text("用户 DB 记录", str(row))
        finally:
            assert_api_ok(user_client.delete(uid).json())

    @allure.title("ROLE_API_FLOW 接口建角色分配菜单→查关系→DB校验→清理")
    @pytest.mark.flow
    def test_role_api_flow(self, role_client, permission_client, menu_client):
        name = gen_name("auto_flow")
        rid = role_client.create({
            "name": name,
            "code": gen_name("auto_key"),
            "sort": 1,
            "status": 0,
            "remark": "flow",
        }).json()["data"]
        menu_body = menu_client.list_all_simple().json()
        assert_api_ok(menu_body, "查询可分配菜单")
        menu_ids = [item["id"] for item in menu_body["data"][:3]]
        assert menu_ids, "没有可分配菜单"
        try:
            assert_api_ok(permission_client.assign_role_menu(rid, menu_ids).json(), "分配菜单")
            ids = permission_client.get_role_menu_ids(rid)
            assert set(menu_ids).issubset(set(ids)), f"菜单未分配 实际={ids}"
            db_rows = db_utils.query_all(
                "SELECT menu_id FROM system_role_menu WHERE role_id=%s AND deleted=0",
                (rid,),
            )
            assert set(menu_ids).issubset({r["menu_id"] for r in db_rows}), "中间表关系缺失"
            attach_text("角色菜单 DB 记录", str(db_rows))
        finally:
            permission_client.assign_role_menu(rid, [])
            assert_api_ok(role_client.delete(rid).json())
