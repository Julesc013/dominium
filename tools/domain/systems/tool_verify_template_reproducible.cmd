@echo off
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%tool_verify_template_reproducible.py" %*

