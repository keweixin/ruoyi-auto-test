"""少量使用 Faker 生成更真实的基础测试字段。"""
import os

from faker import Faker


fake = Faker("zh_CN")
fake.seed_instance(int(os.getenv("FAKER_SEED", "20260704")))


def fake_nickname():
    return fake.name()


def fake_email():
    return fake.safe_email()


def fake_remark():
    return fake.sentence()


def fake_mobile():
    # 13 开头手机号 RuoYi 校验最稳定（15/18 部分段偶发被拒）
    return "13" + fake.numerify("#########")
