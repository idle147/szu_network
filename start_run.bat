@echo off
REM 检查 Python 是否安装
where python >nul 2>nul
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH!
    pause
    exit /b 1
)

REM 检查文件是否存在
if not exist "%~dp0auto_connect.py" (
    echo Error: auto_connect.py not found!
    pause
    exit /b 1
)

REM 启动程序并隐藏窗口
start "" /min cmd /c "python %~dp0auto_connect.py"
timeout /t 1 /nobreak >nul

REM 检查进程
tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH | find /I "python.exe" >nul
if errorlevel 1 (
    echo [ERROR] Python program failed to start, please check the error
    pause
    exit /b 1
) else (
    echo [SUCCESS] Start python.exe successfully
    echo [INFO] You can close this window now
    pause
)