@echo off
setlocal
py -3 "%~dp0tool_verify_numeric_stability.py" %*
