import os
import sys
from dotenv import load_dotenv
from logger import log_error

# 加载环境变量
load_dotenv()

def check_env():
    """检查必要的环境变量"""
    if not os.getenv("OPENAI_API_KEY"):
        log_error("未检测到 OPENAI_API_KEY。请在 .env 文件中配置。")
        sys.exit(1)

# 获取配置
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL = os.getenv("MODEL", "gpt-4o")
