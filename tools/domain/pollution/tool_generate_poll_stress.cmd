@echo off
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%tool_generate_poll_stress.py" %*
