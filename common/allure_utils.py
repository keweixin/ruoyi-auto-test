"""Allure 附件工具：把请求/响应/数据库结果/截图附加到报告。

设计说明：
- Allure 报告的价值在于"让别人看懂测了什么、怎么测的"。
- 本工具封装附件操作，供 BaseApi 和用例调用。
"""
import allure


def attach_text(name, content):
    """附加文本内容。"""
    allure.attach(str(content), name=name, attachment_type=allure.attachment_type.TEXT)


def attach_json(name, content):
    """附加 JSON 内容。"""
    allure.attach(str(content), name=name, attachment_type=allure.attachment_type.JSON)


def attach_png(name, path):
    """附加图片（失败截图用）。"""
    with open(path, "rb") as f:
        allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
