#!/bin/bash
set -e
echo "========== AI CLI 打包脚本 =========="
pip install pyinstaller -q
echo ""

if [[ "$(uname)" == "Darwin" ]]; then
  echo "[macOS] 打包 GUI 为 .app..."
  python -m PyInstaller -y package_config/ai_cli_gui_mac.spec
  echo ""
  echo "[2/2] 打包 CLI 版本..."
  python -m PyInstaller -y package_config/ai_cli_cli.spec
  echo ""
  echo "========== 完成 =========="
  echo "输出目录: dist/"
  echo "  - dist/AI CLI.app   (图形界面，双击运行)"
  echo "  - dist/ai-cli       (命令行)"
else
  echo "[1/2] 打包 GUI 版本..."
  python -m PyInstaller -y package_config/ai_cli_gui.spec
  echo ""
  echo "[2/2] 打包 CLI 版本..."
  python -m PyInstaller -y package_config/ai_cli_cli.spec
  echo ""
  echo "========== 完成 =========="
  echo "输出目录: dist/"
  echo "  - dist/AI-CLI-GUI.exe  (图形界面)"
  echo "  - dist/ai-cli.exe      (命令行)"
fi
echo ""
echo "首次使用请在 GUI 设置中配置 API Key"
