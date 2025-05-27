setlocal
pushd %~dp0SmartLPM
set PYTHONPATH=%~dp0SMARTLPM;%~dp0python
set PATH=%~dp0SmartLPM;%PYTHONPATH%;%PYTHONPATH%\scripts;
if not exist C:\ProgramData\SmartLPM\Config\defaultProcess.tsv (
  md C:\ProgramData\SmartLPM
  md C:\ProgramData\SmartLPM\Config
  copy .\Config\defaultProcess.tsv C:\ProgramData\SmartLPM\Config\defaultProcess.tsv
)
"..\python\python.exe" SmartLPM.py %*
popd
endlocal