# -*- coding: utf-8 -*-
"""用户配置读写：API Key、API Base URL、模型名称"""
import json
from pathlib import Path


def get_config_path() -> Path:
    """配置路径：统一用用户目录，避免 .app 包内无写权限"""
    return Path.home() / ".ai-cli" / "config.json"


def load_config() -> dict:
    """加载配置，返回空 dict 表示无配置"""
    path = get_config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_config(api_key: str, api_base: str, model: str) -> None:
    """保存配置"""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "OPENAI_API_KEY": api_key.strip(),
                "OPENAI_API_BASE": api_base.strip() or "https://api.openai.com/v1",
                "MODEL": model.strip() or "gpt-4o",
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
