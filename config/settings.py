"""配置加载器 —— 学习要点：单例式配置读取 + 环境切换

企业项目惯例：
  - 配置文件（yaml/json/ini）与代码分离
  - 通过环境变量 TEST_ENV 切换环境，CI 上非常常用
  - 敏感信息（密码、token）用 os.environ 读取，绝不写进配置文件
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

CONFIG_PATH = Path(__file__).parent / "config.yaml"


class Settings:
    """加载并缓存环境配置，用法：

        settings = Settings()           # 默认环境
        settings = Settings("dev")      # 指定环境
        settings.base_url
    """

    def __init__(self, env: str | None = None):
        raw: Dict[str, Any] = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
        self.env = env or os.environ.get("TEST_ENV", raw.get("default", "test"))
        if self.env not in raw:
            raise ValueError(f"未知环境 {self.env!r}，可选：{[k for k in raw if k != 'default']}")
        self._conf = raw[self.env]

    def __getattr__(self, name: str) -> Any:
        try:
            return self._conf[name]
        except KeyError:
            raise AttributeError(f"环境 {self.env!r} 缺少配置项：{name}")


# 模块级单例：整个测试进程共享一份配置
settings = Settings()
