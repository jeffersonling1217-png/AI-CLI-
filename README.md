# AI CLI 小工具

用自然语言生成并执行命令行，支持 GUI 和 CLI 两种模式。

## 项目结构

```
AI-CLI-/
├── 业务代码
│   ├── main.py          # CLI 入口
│   ├── gui.py           # GUI 主逻辑
│   ├── gui_entry.py     # GUI 入口（打包用）
│   ├── ai_engine.py     # AI 引擎
│   ├── config.py        # 配置加载
│   ├── user_config.py   # 用户配置（API Key 等）
│   ├── executor.py      # 命令执行
│   ├── intent_recognizer.py  # 意图识别
│   ├── command_parser.py     # 命令解析
│   └── logger.py        # 日志
├── 打包配置
│   └── package_config/
│       ├── ai_cli_gui.spec      # Windows GUI
│       ├── ai_cli_gui_mac.spec  # macOS .app
│       └── ai_cli_cli.spec      # CLI
├── 脚本
│   └── scripts/
│       ├── setup.bat        # 安装依赖
│       ├── push_to_github.bat
│       └── pull_from_github.bat
├── build.sh / build.bat     # 打包入口
├── pyproject.toml
├── requirements.txt
└── .env.example
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt
# 或 Windows: scripts\setup.bat

# 运行 GUI
python gui_entry.py

# 运行 CLI
python main.py
```

## 打包

```bash
./build.sh        # macOS
build.bat         # Windows
```

输出在 `dist/` 目录。
