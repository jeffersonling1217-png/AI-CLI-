@echo off
REM 添加 Git 到 PATH
set "PATH=%PATH%;C:\Program Files\Git\bin"

REM 切换到项目目录
cd /d "%~dp0"

echo 正在从 GitHub 拉取最新代码...
git pull origin main

if %errorlevel% equ 0 (
    echo.
    echo 同步完成！
) else (
    echo.
    echo 拉取失败，请检查网络或冲突后重试。
)

pause
