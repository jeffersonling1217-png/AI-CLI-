# -*- coding: utf-8 -*-
"""GUI 入口：捕获所有异常并写入日志，便于双击启动时排查"""
import traceback
from pathlib import Path

if __name__ == "__main__":
    log_path = Path.home() / ".ai-cli" / "crash.log"
    try:
        from gui import run_app
        run_app()
    except Exception:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
