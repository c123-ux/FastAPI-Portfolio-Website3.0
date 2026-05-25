@echo off
cd /d D:\PythonProject1

echo [Step 1/4] Configuring Git...
git config --global user.name "c"
git config --global user.email "2441273057@qq.com"
echo Done!

echo [Step 2/4] Initializing Git repository...
if not exist .git (
    git init
    echo Git repository initialized!
) else (
    echo Git repository already exists!
)

echo [Step 3/4] Adding files...
git add .
echo All files added!

echo [Step 4/4] Creating commit...
git commit -m "Initial commit: Full-stack portfolio website v2.0"
echo Commit created!

echo.
echo ==========================================
echo  PREPARATION COMPLETE!
echo ==========================================
echo.
echo Now please:
echo 1. Open: https://github.com/new
echo 2. Create a new repository (name: portfolio)
echo 3. Select "Public"
echo 4. DO NOT check "Add a README file"
echo.
echo After creating the repository, run:
echo    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo    git branch -M main
echo    git push -u origin main
echo.
pause
