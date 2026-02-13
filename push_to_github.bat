@echo off
REM 添加 Git 到 PATH
set "PATH=%PATH%;C:\Program Files\Git\bin"

REM 切换到项目目录
cd /d "C:\Users\User\OneDrive - Up Way Holdings Group Limited\文件\curosr\curosr\AI CLI小工具"

REM 检查 Git 状态
echo 检查 Git 状态...
git status

REM 确保所有文件已添加
echo.
echo 添加所有文件...
git add .

REM 检查是否有未提交的更改
git diff --cached --quiet
if %errorlevel% neq 0 (
    echo.
    echo 提交更改...
    git commit -m "Initial commit: AI CLI tool"
)

REM 确保分支名是 main
echo.
echo 检查分支...
git branch -M main

REM 验证远程仓库
echo.
echo 验证远程仓库配置...
git remote -v

REM 推送到 GitHub
echo.
echo 推送到 GitHub...
git push -u origin main

echo.
echo 完成！
pause
