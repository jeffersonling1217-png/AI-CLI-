# -*- mode: python ; coding: utf-8 -*-
# macOS .app 打包配置（仅用于 macOS）
import sys

block_cipher = None

hidden_imports = [
    'openai', 'python_dotenv', 'dotenv',
    'rich', 'rich.console', 'rich.panel', 'rich.prompt',
    'shellingham', 'prompt_toolkit', 'prompt_toolkit.history',
    'openpyxl', 'tkinter', 'user_config',
]

a = Analysis(
    ['gui_entry.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    [],
    exclude_binaries=True,
    name='AI CLI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # macOS 拖拽文件支持
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI CLI',
)

# macOS .app bundle
app = BUNDLE(
    coll,
    name='AI CLI.app',
    icon=None,
    bundle_identifier='com.aicli.gui',
    info_plist={
        'CFBundleName': 'AI CLI',
        'CFBundleDisplayName': 'AI CLI',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
    },
)
