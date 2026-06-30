"""日志工具：统一格式，同时输出到控制台和 logs/test.log。

设计说明：
- 用 logging 而非 print：可分级（INFO/WARNING/ERROR）、可落文件、CI 友好。
- BaseApi 里记录请求/响应，失败时日志是排查第一手资料。
"""
import logging
import os

_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(_LOG_DIR, "test.log"), encoding="utf-8"),
    ],
)

# 全局 logger，各模块 import log 使用
log = logging.getLogger("ruoyi-auto")
