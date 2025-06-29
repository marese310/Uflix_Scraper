@echo off
echo Setting up your UFlix environment...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo.
echo ✅ All dependencies installed.
pause
