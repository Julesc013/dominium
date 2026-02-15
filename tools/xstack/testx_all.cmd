@echo off
setlocal
python "%~dp0testx_all.py" %*
exit /b %errorlevel%
