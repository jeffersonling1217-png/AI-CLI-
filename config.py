import os
import sys
from dotenv import load_dotenv
from logger import log_error

# 加载环境变量
load_dotenv()

# 从 user_config 覆盖（.env 优先，user_config 补充）
def _apply_user_config():
    try:
        from user_config import load_config
        cfg = load_config()
        if cfg:
            for k, v in cfg.items():
                if v:
                    os.environ.setdefault(k, v)
    except ImportError:
        pass

_apply_user_config()


def reload_config():
    """重新加载配置（用户修改后调用）"""
    try:
        from user_config import load_config
        cfg = load_config()
        if cfg:
            os.environ["OPENAI_API_KEY"] = cfg.get("OPENAI_API_KEY", "")
            os.environ["OPENAI_API_BASE"] = cfg.get("OPENAI_API_BASE", "https://api.openai.com/v1")
            os.environ["MODEL"] = cfg.get("MODEL", "gpt-4o")
    except ImportError:
        pass
    global API_KEY, API_BASE, MODEL
    API_KEY = os.getenv("OPENAI_API_KEY")
    API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    MODEL = os.getenv("MODEL", "gpt-4o")


def check_env():
    """检查必要的环境变量"""
    if not os.getenv("OPENAI_API_KEY"):
        log_error("未检测到 OPENAI_API_KEY。请在 .env 文件中配置，或通过 GUI 设置。")
        sys.exit(1)


# 获取配置
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL = os.getenv("MODEL", "gpt-4o")
