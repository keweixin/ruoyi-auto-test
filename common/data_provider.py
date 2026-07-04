"""数据驱动工具：从 data/*.yaml 读取表驱动测试数据，生成 pytest 参数化用例。

设计说明：
- YAML 文件每个模块下有 create_cases 列表，每项是一条测试用例数据；
- payload_template: "valid" 表示用 create 字段生成合法 payload（随机化唯一字段）；
- overrides 覆盖特定字段，构造非法/边界场景；
- setup: "duplicate" 表示先创建一条，再用同关键标识再建以触发重复校验；
- 本模块只负责"读 YAML + 生成 payload"，断言逻辑仍在测试用例里。
"""
import os
import copy

from common.yaml_utils import load_yaml
from common.random_utils import gen_name, gen_username, gen_mobile, gen_email

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _valid_payload(module):
    """根据模块 create 字段生成一份合法 payload（随机化唯一字段）。"""
    cfg = load_yaml(os.path.join(_DATA_DIR, f"{module}_data.yaml"))[module]["create"]
    if module == "user":
        return {
            "username": gen_username(),
            "password": cfg["password"],
            "nickname": gen_name("auto_nick"),
            "mobile": gen_mobile(),
            "deptId": cfg["deptId"],
        }
    if module == "role":
        return {
            "name": gen_name("auto_role"),
            "code": gen_name("auto_role_code"),
            "sort": cfg["sort"],
            "status": cfg["status"],
            "remark": cfg.get("remark", ""),
        }
    if module == "dept":
        return {
            "name": gen_name("auto_dept"),
            "parentId": cfg["parentId"],
            "sort": cfg["sort"],
            "status": cfg["status"],
            "phone": cfg.get("phone", ""),
            "email": cfg.get("email", ""),
        }
    if module == "post":
        return {
            "name": gen_name("auto_post"),
            "code": gen_name("auto_code"),
            "sort": cfg["sort"],
            "status": cfg["status"],
            "remark": cfg.get("remark", ""),
        }
    raise ValueError(f"不支持的数据驱动模块: {module}")


def load_create_cases(module):
    """读取 data/{module}_data.yaml 的 create_cases，返回参数化数据列表。

    返回: list[dict]，每项含:
      - case_id: 用例编号（如 USER_API_001）
      - desc: 用例描述
      - payload: 实际请求体（已应用 overrides）
      - expect_ok: 期望业务成功 (code==0)
      - expect_msg_contains: 期望响应 msg 含的关键字（空则不校验）
      - setup: 前置动作标记，测试用例按需处理：
          "duplicate"      先用同 payload 创建一条占位，再用同 payload 再建
          "duplicate_code" 先用 payload 创建一条，再用同 code 但新 name 再建（岗位场景）
    """
    data = load_yaml(os.path.join(_DATA_DIR, f"{module}_data.yaml"))[module]
    cases = data.get("create_cases", [])
    result = []
    for c in cases:
        case = copy.deepcopy(c)
        # 生成 payload：默认用合法模板，再叠加 overrides
        payload = _valid_payload(module)
        payload.update(case.get("overrides", {}))
        case["payload"] = payload
        case.setdefault("expect_msg_contains", "")
        case.setdefault("setup", "")
        result.append(case)
    return result


def build_parametrize(cases):
    """把 load_create_cases 的结果转成 pytest.parametrize 需要的 (values, ids)。"""
    values = [c for c in cases]
    ids = [c["case_id"] for c in cases]
    return values, ids
