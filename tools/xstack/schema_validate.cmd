@echo off
setlocal EnableExtensions

if "%~1"=="" goto usage
if "%~2"=="" goto usage

python tools\xstack\compatx\schema_validate.py --repo-root . "%~1" "%~2"
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

:usage
echo Usage: tools\xstack\schema_validate ^<schema_name^> ^<file_path^>
echo Example: tools\xstack\schema_validate session_spec schemas\examples\session_spec.example.json
endlocal & exit /b 2

