@echo off
chcp 65001 >nul
echo ==========================================
echo  正在将项目推送到 GitHub...
echo ==========================================
echo.

cd /d D:\PythonProject1

echo [1/6] 配置 Git 用户信息...
git config --global user.name "c"
git config --global user.email "2441273057@qq.com"
echo ✓ Git 配置完成
echo.

echo [2/6] 初始化 Git 仓库...
if not exist .git (
    git init
    echo ✓ Git 仓库初始化完成
) else (
    echo ✓ Git 仓库已存在
)
echo.

echo [3/6] 添加文件到暂存区...
git add .
echo ✓ 文件添加完成
echo.

echo [4/6] 提交更改...
git commit -m " 初始提交：个人全栈作品集网站 v2.0"
echo ✓ 提交完成
echo.

echo ==========================================
echo  准备工作已完成！
echo ==========================================
echo.
echo 接下来请执行以下步骤：
echo.
echo 1. 在 GitHub 创建新仓库：
echo    https://github.com/new
echo.
echo 2. 仓库名建议：portfolio 或 my-portfolio
echo.
echo 3. 选择 Public（公开）
echo.
echo 4. 不要勾选 "Add a README file"
echo.
echo 5. 创建完成后，复制提示命令并运行：
echo    git remote add origin https://github.com/你的用户名/仓库名.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo ==========================================
pause
