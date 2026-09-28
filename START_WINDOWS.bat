@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 goto :run_py
where python >nul 2>nul
if not errorlevel 1 goto :run_python
echo Python was not found. Install Python 3.10+ with Tcl/Tk, then try again.
echo The application does not require pip or GitHub access.
pause
exit /b 1

:run_py
py -3 -X faulthandler studio.py
set "STUDIO_EXIT=%ERRORLEVEL%"
goto :finish

:run_python
python -X faulthandler studio.py
set "STUDIO_EXIT=%ERRORLEVEL%"
goto :finish

:finish
if "%STUDIO_EXIT%"=="0" exit /b 0
echo.
echo Behavior Studio exited with code %STUDIO_EXIT%.
echo Check Python and Tk: py -3 -m tkinter
echo Python error details: %USERPROFILE%\samcnpc-studio-error.log
echo Please keep this terminal output if you report a crash.
pause
exit /b %STUDIO_EXIT%
