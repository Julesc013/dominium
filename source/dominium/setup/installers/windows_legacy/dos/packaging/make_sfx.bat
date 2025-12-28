@echo off
setlocal

if "%~1"=="" goto usage
if "%~2"=="" goto usage
if "%~3"=="" goto usage

set EXE_IN=%~1
set ARCHIVE_IN=%~2
set EXE_OUT=%~3

python -c "import struct,sys; exe,arc,out=sys.argv[1:4]; d=open(exe,'rb').read(); a=open(arc,'rb').read(); f=b'DSUX'+struct.pack('<II',len(d),len(a)); open(out,'wb').write(d+a+f)" "%EXE_IN%" "%ARCHIVE_IN%" "%EXE_OUT%"
if errorlevel 1 goto fail

echo SFX built: %EXE_OUT%
exit /b 0

:usage
echo Usage: make_sfx.bat ^<installer.exe^> ^<payload.dsuarch^> ^<out.exe^>
exit /b 1

:fail
echo Failed to build SFX (python required).
exit /b 1
