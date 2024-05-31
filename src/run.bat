setlocal
pushd %~dp0
set PYTHONPATH=%~dp0python
set PATH=%PYTHONPATH%;%PYTHONPATH%\scripts;%PATH%
set VIPS_WARNING=0
start "" "python\pythonw.exe" main.py %*
popd
endlocal