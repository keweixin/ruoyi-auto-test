"""随机数据生成工具。

设计说明：
- 每轮测试使用独立运行前缀，避免并发执行时相互清理；
- 默认前缀仍以 auto 开头，兼容 UI 安全删除校验。
"""
import os
import time
import random

# 每次 Python 进程启动生成一个运行级前缀；也可通过环境变量覆盖，便于 CI 追踪。
RUN_ID = os.getenv("TEST_RUN_ID") or str(int(time.time()))
TEST_RUN_PREFIX = os.getenv("TEST_RUN_PREFIX") or f"auto_{RUN_ID}"


def gen_name(prefix="auto"):
    """生成随机名称，如 auto_1782864000_dict_123。"""
    # 保证所有生成数据都带本轮 TEST_RUN_PREFIX，便于精确清理。
    if prefix.startswith("auto"):
        base = f"{TEST_RUN_PREFIX}_{prefix.replace('auto_', '').replace('auto', '').strip('_')}"
    else:
        base = f"{TEST_RUN_PREFIX}_{prefix}"
    return f"{base}_{random.randint(100, 999)}"


def gen_mobile():
    """生成随机 11 位手机号（13 开头）。"""
    return "13" + "".join(random.choice("0123456789") for _ in range(9))


def gen_email():
    """生成随机邮箱。"""
    return f"{gen_name('user')}@test.com"
