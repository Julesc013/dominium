@echo off
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%tool_verify_poll_mass_balance.py" %*
