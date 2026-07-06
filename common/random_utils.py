"""随机数据生成工具。

每轮测试使用带时间的 auto 前缀，既方便清理，也能避免普通串行运行重名。
"""
import os
import random
from datetime import datetime


def _build_run_prefix():
    """构建简短运行前缀，例如 auto_0706113045。"""
    if os.getenv("TEST_RUN_PREFIX"):
        return os.getenv("TEST_RUN_PREFIX")
    return "auto_" + datetime.now().strftime("%m%d%H%M%S")


TEST_RUN_PREFIX = _build_run_prefix()
TEST_USER_PREFIX = TEST_RUN_PREFIX.replace("_", "")


def gen_name(prefix="auto"):
    """生成随机名称，如 auto_0706113045_dept_456。"""
    if prefix.startswith("auto"):
        suffix = prefix.replace("auto_", "").replace("auto", "").strip("_")
        # 控制 suffix 长度，避免组合后超过数据库字段长度
        suffix = suffix[:8]
        base = f"{TEST_RUN_PREFIX}_{suffix}" if suffix else TEST_RUN_PREFIX
    else:
        base = f"{TEST_RUN_PREFIX}_{prefix[:8]}"
    return f"{base}_{random.randint(100, 999)}"


def gen_mobile():
    """生成随机 11 位手机号（13 开头）。"""
    return "13" + "".join(random.choice("0123456789") for _ in range(9))


def gen_username():
    """生成只包含字母和数字的用户名，满足管理端账号格式校验。"""
    return f"{TEST_USER_PREFIX}u{random.randint(100, 999)}"


def gen_email():
    """使用 Faker 生成格式合法的邮箱。"""
    from common.faker_utils import fake_email
    return fake_email()
