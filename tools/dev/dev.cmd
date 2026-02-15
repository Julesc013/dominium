@echo off
setlocal
python "%~dp0dev.py" %*
exit /b %errorlevel%
