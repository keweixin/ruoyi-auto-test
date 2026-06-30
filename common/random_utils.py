"""随机数据生成工具。

设计说明：
- 新增类用例必须用随机数据，避免：
  1) 数据重复导致重复执行失败；
  2) 和系统已有数据冲突。
- 用时间戳 + 随机数保证唯一性。
"""
import time
import random


def gen_name(prefix="auto"):
    """生成随机名称，如 auto_dict_1719700000_456"""
    return f"{prefix}_{int(time.time())}_{random.randint(100, 999)}"


def gen_mobile():
    """生成随机 11 位手机号（13 开头）。"""
    return "13" + "".join(random.choice("0123456789") for _ in range(9))


def gen_email():
    """生成随机邮箱。"""
    return f"{gen_name('user')}@test.com"
