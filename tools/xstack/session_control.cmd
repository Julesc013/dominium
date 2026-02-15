@echo off
setlocal
set "_DOM_TOOL_ID=%~n0"
python "%~dp0session_control.py" %*
set "_DOM_RC=%errorlevel%"
endlocal & exit /b %_DOM_RC%
