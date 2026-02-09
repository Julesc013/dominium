@echo off
setlocal
set "_DOM_SCRIPT_DIR=%~dp0"
for %%I in ("%_DOM_SCRIPT_DIR%..\..") do set "_DOM_REPO_ROOT=%%~fI"
set "_DOM_PATCH_FILE=%TEMP%\dominium_env_tools_%RANDOM%_%RANDOM%.cmd"

python "%_DOM_SCRIPT_DIR%env_tools.py" --repo-root "%_DOM_REPO_ROOT%" export --shell cmd > "%_DOM_PATCH_FILE%"
if errorlevel 1 (
    type "%_DOM_PATCH_FILE%"
    del /q "%_DOM_PATCH_FILE%" >nul 2>nul
    exit /b 2
)

for %%I in ("%_DOM_PATCH_FILE%") do set "_DOM_PATCH_FILE_ABS=%%~fI"
for %%I in ("%_DOM_REPO_ROOT%") do set "_DOM_REPO_ROOT_ABS=%%~fI"
endlocal & set "_DOM_PATCH_FILE_ABS=%_DOM_PATCH_FILE_ABS%" & set "_DOM_REPO_ROOT_ABS=%_DOM_REPO_ROOT_ABS%"
call "%_DOM_PATCH_FILE_ABS%"
del /q "%_DOM_PATCH_FILE_ABS%" >nul 2>nul

python "%~dp0env_tools.py" --repo-root "%_DOM_REPO_ROOT_ABS%" doctor --require-path
if errorlevel 1 exit /b 2
exit /b 0
