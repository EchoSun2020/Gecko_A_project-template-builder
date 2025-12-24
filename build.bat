@echo off
chcp 65001 >nul

echo ========================================
echo   Project Template Builder - Build
echo ========================================
echo.

set PYTHON_PATH=D:\py\python3.10.11\python.exe

echo [INFO] Checking pyinstaller...
%PYTHON_PATH% -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing pyinstaller...
    %PYTHON_PATH% -m pip install pyinstaller
)

echo.
echo [INFO] Cleaning old build files...
if exist build rd /s /q build
if exist dist rd /s /q dist

echo.
echo [INFO] Building EXE...
echo.

%PYTHON_PATH% -m PyInstaller --noconfirm --onefile --windowed --name "ProjectTemplateBuilder" --collect-all customtkinter project_template_builder.py

echo.
echo ========================================
if exist "dist\ProjectTemplateBuilder.exe" (
    copy /Y config.json dist\config.json >nul 2>&1
    echo [SUCCESS] Build complete!
    echo.
    echo EXE: dist\ProjectTemplateBuilder.exe
    echo Config: dist\config.json
    echo.
    echo Keep EXE and config.json in the same folder!
) else (
    echo [ERROR] Build failed!
)
echo ========================================
pause
