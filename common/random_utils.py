"""随机数据生成工具。

设计说明：
- 每轮测试使用独立运行前缀，避免并发执行时互相清理；
- 前缀包含 UUID、进程号、xdist worker ID，避免两个进程同一秒启动时撞车；
- 前缀保持较短，避免 RuoYi 字段长度（如部门名称 30 字符）超限；
- 默认前缀仍以 auto 开头，兼容 UI 安全删除校验。
"""
import os
import random
import uuid


_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def _base36(num):
    num = int(num)
    if num == 0:
        return "0"
    out = []
    while num:
        num, rem = divmod(num, 36)
        out.append(_DIGITS[rem])
    return "".join(reversed(out))


def _build_run_prefix():
    """构建本进程唯一且短的运行前缀。

    外部可通过 TEST_RUN_PREFIX 覆盖；否则使用：
    auto_<worker>_<pid36>_<uuid4>
    例如 auto_m_13dw_a1b2，既能避免并发碰撞，又不超字段长度。
    """
    if os.getenv("TEST_RUN_PREFIX"):
        return os.getenv("TEST_RUN_PREFIX")
    worker = os.getenv("PYTEST_XDIST_WORKER", "m").replace("gw", "g")[:3]
    pid = _base36(os.getpid())
    unique = uuid.uuid4().hex[:4]
    return f"auto_{worker}_{pid}_{unique}"


RUN_ID = os.getenv("TEST_RUN_ID") or uuid.uuid4().hex
TEST_RUN_PREFIX = _build_run_prefix()
TEST_USER_PREFIX = TEST_RUN_PREFIX.replace("_", "")


def gen_name(prefix="auto"):
    """生成随机名称，如 auto_m_13dw_a1b2_dept_456。"""
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
