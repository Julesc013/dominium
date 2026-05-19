@echo off
setlocal
py -3 "%~dp0tool_generate_factory_planet_scenario.py" %*
exit /b %errorlevel%
