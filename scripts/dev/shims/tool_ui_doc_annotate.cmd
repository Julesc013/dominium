@echo off
setlocal
set "_DOM_TOOL_ID=%~n0"
python "%~dp0scripts\dev\tool_shim.py" "%_DOM_TOOL_ID%" %*
set "_DOM_RC=%errorlevel%"
endlocal & exit /b %_DOM_RC%
