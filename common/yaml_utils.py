"""YAML 读取工具。"""
import os

import yaml


def load_yaml(path):
    """读取 yaml 文件并返回 dict。"""
    path = os.fspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        raise ValueError(f"YAML 内容为空: {path}")
    if not isinstance(data, dict):
        raise ValueError(f"YAML 根节点必须是对象: {path}")
    return data


def load_case_list(path, module, key="create_cases"):
    data = load_yaml(path)
    if module not in data or not isinstance(data[module], dict):
        raise ValueError(f"YAML 缺少模块: {module}")
    cases = data[module].get(key, [])
    if not isinstance(cases, list):
        raise ValueError(f"{module}.{key} 必须是列表")
    case_ids = []
    for case in cases:
        if not isinstance(case, dict) or not case.get("case_id"):
            raise ValueError(f"{module}.{key} 每项必须包含 case_id")
        case_ids.append(case["case_id"])
    duplicate_ids = sorted({case_id for case_id in case_ids if case_ids.count(case_id) > 1})
    if duplicate_ids:
        raise ValueError(f"case_id 重复: {duplicate_ids}")
    return cases
