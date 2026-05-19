@echo off
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%tool_verify_explain_determinism.py" %*
