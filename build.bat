@echo off
chcp 65001 >nul
echo ========== AI CLI 打包脚本 ==========
pip install pyinstaller -q
echo.
echo [1/2] 打包 GUI 版本 (AI-CLI-GUI.exe)...
pyinstaller -y package_config\ai_cli_gui.spec
echo.
echo [2/2] 打包 CLI 版本 (ai-cli.exe)...
pyinstaller -y package_config\ai_cli_cli.spec
echo.
echo ========== 完成 ==========
echo 输出目录: dist\
echo   - dist\AI-CLI-GUI.exe  (图形界面)
echo   - dist\ai-cli.exe      (命令行)
echo.
echo 使用前请将 .env.example 复制为 .env 并配置 OPENAI_API_KEY
pause
