setlocal
pushd %~dp0
set ProjectDir=%~dp0
set ProjectName=QuaRepToolKit

for /f delims^=^"^ tokens^=2 %%A in ('findstr /r "^__version__" main.py') do set v=%%A
>.\ProductVersion.wxi (
echo ^<Include^>
echo  ^<?define ProductVersion=%v%?^>
echo ^</Include^> 
)

set msiFileName=%ProjectName%_%v%.msi
set binFolder=%ProjectName%_%v%
set wixext=-ext "%WIX%\bin\WixUtilExtension.dll" -ext "%WIX%\bin\WixDifxAppExtension.dll" -ext "%WIX%\bin\WixUIExtension.dll"

for /d /r python %%d in ("__pycache__") do @if exist "%%d" rd /s /q "%%d"
rd obj /S /Q
md obj
md package

"%WIX%\bin\candle.exe" -arch x64 Product.wxs  -out obj\Product.wixobj
set objs=obj\Product.wixobj
call :subdir python python
call :subdir icons icons
call :subdir macros macros
call :subdir vips vips
call :subdir lunasvg lunasvg
call :subdir caltool caltool

"%WIX%\bin\light.exe" -sice:ICE60 %wixext% %objs% -out package\%msiFileName%

rd /S /Q "%binFolder%"
md "%binFolder%"
copy cli_calibration_tool_help.txt "%binFolder%"
copy CommandPipe.py "%binFolder%"
copy DetectorPhotonCalibration.py "%binFolder%"
copy FolderWatch.py "%binFolder%"
copy pageDetectorResults.py "%binFolder%"
copy forms.py "%binFolder%"
copy main.py "%binFolder%"
copy pageBrowse.py "%binFolder%"
copy pageDetectorResults.py "%binFolder%"
copy pageHelp.py "%binFolder%"
copy pageLightSourceResults.py "%binFolder%"
copy pageMeasure.py "%binFolder%"
copy wxApp.py "%binFolder%"
copy run.bat "%binFolder%"
copy run_debug.bat "%binFolder%"
robocopy python "%binFolder%\python" /s
robocopy icons "%binFolder%\icons" /s
robocopy macros "%binFolder%\macros" /s
robocopy vipos "%binFolder%\vips" /s
robocopy lunasvg "%binFolder%\lunasvg" /s
robocopy caltool "%binFolder%\caltool" /s
"%ZIP%" a "package\%binFolder%.zip" "%binFolder%"

popd
endlocal
goto :eof

:subdir
set source=%1
set target=%2
set targetDir=%2
"%WIX%\bin\heat.exe" dir "%source%" -cg cg%target%Files -gg -scom -sreg -sfrag -srd -dr %target%Dir -var env.targetDir -out "obj\%target%Files.wxs"
"%WIX%\bin\candle.exe" -arch x64 obj\%target%Files.wxs -out obj\%target%Files.wixobj
set objs=%objs% obj\%target%Files.wixobj
goto :eof

