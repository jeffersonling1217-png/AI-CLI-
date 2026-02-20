# -*- mode: python ; coding: utf-8 -*-
# GUI 版本打包配置（无控制台窗口）
import sys

block_cipher = None

# 收集所有依赖的隐藏导入
hidden_imports = [
    'openai', 'python_dotenv', 'dotenv',
    'rich', 'rich.console', 'rich.panel', 'rich.prompt',
    'shellingham', 'prompt_toolkit', 'prompt_toolkit.history',
    'openpyxl', 'tkinter', 'user_config',
]

# 数据文件：.env.example 可打包进去作为配置模板
datas = []

a = Analysis(
    ['gui_entry.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI-CLI-GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 无控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
