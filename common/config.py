"""配置中心：支持环境变量优先，可选读取 data/env.yaml。

设计说明：
- 敏感字段优先从环境变量读取，防止明文提交到 Git；
- 环境变量未设置时回退到 YAML 配置；
- data/env.example.yaml 作为模板，env.yaml 本身已加入 .gitignore。
"""
import os
import yaml

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    """全局配置对象。用法：from common.config import cfg"""

    def __init__(self):
        # 尝试加载 YAML 作为本地开发配置（可选）
        env_path = os.path.join(_BASE_DIR, "data", "env.yaml")
        yaml_cfg = {}
        if os.path.isfile(env_path):
            with open(env_path, encoding="utf-8") as f:
                yaml_cfg = yaml.safe_load(f) or {}

        # 环境变量优先；若未设置则回退到 YAML
        def _get(key, yaml_section, yaml_key):
            return os.getenv(key) or yaml_cfg.get(yaml_section, {}).get(yaml_key, "")

        self.base_url = _get("BASE_URL", "env", "base_url") or "http://localhost:48080"
        self.web_url = _get("WEB_URL", "env", "web_url") or "http://localhost:80"
        self.tenant_id = _get("TENANT_ID", "env", "tenant_id") or "1"

        self.admin_user = _get("ADMIN_USERNAME", "admin", "username") or "admin"
        self.admin_pwd = _get("ADMIN_PASSWORD", "admin", "password") or "admin123"

        self.db_host = _get("DB_HOST", "db", "host") or "localhost"
        self.db_port = int(_get("DB_PORT", "db", "port") or "3306")
        self.db_user = _get("DB_USER", "db", "user") or "root"
        self.db_pwd = _get("DB_PASSWORD", "db", "password") or ""
        self.db_name = _get("DB_NAME", "db", "database") or "ruoyi-vue-pro"


cfg = Config()