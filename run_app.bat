@echo off
setlocal
echo ===================================================
echo   MRIGANK AI CHATBOT LAUNCHER
echo ===================================================
echo.
echo 1. Checking for Python 3.11 Virtual Environment...
if not exist ".venv_py311\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv_py311.
    echo Please run the installation steps again.
    pause
    exit /b
)

echo [OK] Found .venv_py311.
echo.
echo 2. Launching Streamlit App...
echo    Command: .venv_py311\Scripts\python -m streamlit run app.py
echo.

:: This is the key line that fixes the "Fatal error in launcher"
:: We use the specific python.exe in the venv, and run streamlit as a module (-m)
.venv_py311\Scripts\python -m streamlit run app.py --server.port 8524

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The app crashed or failed to launch.
    echo Please check the error message above.
    pause
)
