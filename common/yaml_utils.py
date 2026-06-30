"""YAML 读取工具。"""
import yaml


def load_yaml(path):
    """读取 yaml 文件并返回 dict。"""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
