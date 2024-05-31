setlocal
pushd %~dp0
set PYTHONPATH=%~dp0python
set PATH=%PYTHONPATH%;%PYTHONPATH%\scripts;%PATH%
set VIPS_WARNING=0
"python\python.exe" main.py %*
pause
popd
endlocal