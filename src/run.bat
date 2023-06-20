setlocal
pushd %~dp0
start "" "python\pythonw.exe" main.py %*
popd
endlocal