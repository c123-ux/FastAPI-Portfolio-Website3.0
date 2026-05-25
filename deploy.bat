@echo off
chcp 65001 >nul
echo ========================================
echo   Portfolio 项目一键部署脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装，请先安装 Python 3.9+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM 安装依赖
echo.
echo 📦 正在安装 Python 依赖...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

REM 检查 .env
if not exist ".env" (
    echo.
    echo ⚠️  .env 文件不存在，正在创建...
    if exist ".env.example" (
        copy .env.example .env
    ) else (
        echo SECRET_KEY=your-secret-key-here > .env
        echo ADMIN_USERNAME=admin >> .env
        echo ADMIN_PASSWORD=admin123 >> .env
    )
    echo ✏️  请编辑 .env 文件配置您的参数
    pause
)

echo.
echo ========================================
echo   🎯 启动后端服务
echo ========================================
echo.
echo 📍 API 文档: http://localhost:8000/docs
echo 📍 管理后台: 打开 index.html 后通过 API 访问
echo.
echo ⚠️  按 Ctrl+C 停止服务
echo.

python main_backend.py
pause
