@echo off
set "PATH=%PATH%;C:\Program Files\Git\bin"
cd /d "%~dp0.."

echo 检查 Git 状态...
git status

echo.
echo 添加所有文件...
git add .

git diff --cached --quiet
if %errorlevel% neq 0 (
    echo.
    echo 提交更改...
    set /p msg=请输入提交信息: 
    git commit -m "%msg%"
)

echo.
echo 检查分支...
git branch -M main

echo.
echo 推送到 GitHub...
git push -u origin main

echo.
echo 完成！
pause
