"C:\Windows\System32\NET" FILE 1>NUL 2>NUL
IF '%ERRORLEVEL%' == '0'  GOTO :elevated
SETLOCAL ENABLEEXTENSIONS
SET args=%*
IF DEFINED args (
    set args=%args:"=^\^^^"%
)
"C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell" saps -verb runas -filepath 'cmd.exe' -argumentList '/S /C \^"\^"%~f0\^" %args%\^"'
ENDLOCAL
EXIT /b
:elevated

SET PYTHONPATH=%~dp0
SET PATH=%~dp0python;%~dp0python\scripts;C:\Windows\system32

python -m pip install --upgrade pip

:: 0.2.26: latests module versions on 30-05-2025, except for wxmplot
:: wxmplot > 0.9.59 breaks compatibility (right <= left exception)

pip install -U cffi==1.17.1
pip install -U charset-normalizer==3.4.2
pip install -U contourpy==1.3.0
pip install -U cycler==0.12.1
pip install -U darkdetect==0.8.0
pip install -U fonttools==4.58.1
pip install -U importlib-resources==6.5.2
pip install -U kiwisolver==1.4.7
pip install -U matplotlib==3.9.4
pip install -U numpy==2.0.2
pip install -U packaging==25.0
pip install -U Pillow==11.2.1
pip install -U pycparser==2.22
pip install -U pyparsing==3.2.3
pip install -U pyshortcuts==1.9.5
pip install -U PySide6==6.9.0
pip install -U PySide6_Addons==6.9.0
pip install -U PySide6_Essentials==6.9.0
pip install -U python-dateutil==2.9.0.post0
pip install -U pytz==2025.2
pip install -U pyvips==3.0.0
pip install -U pywin32==310
pip install -U PyYAML==6.0.2
pip install -U setuptools==80.9.0
pip install -U shiboken6==6.9.0
pip install -U six==1.17.0
pip install -U webcolors==24.11.1
pip install -U wheel==0.45.1
pip install -U wxmplot==0.9.59
pip install -U wxPython==4.2.3
pip install -U wxutils==0.3.5
pip install -U wxwidgets==1.0.5
pip install -U zipp==3.22.0

ENDLOCAL

