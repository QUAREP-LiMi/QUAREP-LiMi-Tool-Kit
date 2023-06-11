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
set wxsFileName=Product.wxs
set wixobjFileName=Product.wixobj
set msiFileName=%ProjectName%_%v%.msi
set binFolder=%ProjectName%_%v%
set pythonDir=py39
set pythonFiles=python_files
set iconsDir=icons
set iconsFiles=icons_files
set macrosDir=macros
set macrosFiles=macros_files
set wixext=-ext "%WIX%\bin\WixUtilExtension.dll" -ext "%WIX%\bin\WixDifxAppExtension.dll" -ext "%WIX%\bin\WixUIExtension.dll" 

for /d /r %pythonDir% %%d in ("__pycache__") do @if exist "%%d" rd /s /q "%%d"

md obj
md package
"%WIX%\bin\candle.exe" -arch x64 %wxsFileName%  -out obj\%wixobjFileName%
"%WIX%\bin\heat.exe" dir "%pythonDir%" -cg cgPythonFiles -gg -scom -sreg -sfrag -srd -dr pythonDir -var env.pythonDir -out "obj\%pythonFiles%.wxs"
"%WIX%\bin\candle.exe" -arch x64 obj\%pythonFiles%.wxs -out obj\%pythonFiles%.wixobj
"%WIX%\bin\heat.exe" dir "%iconsDir%" -cg cgIconsFiles -gg -scom -sreg -sfrag -srd -dr iconsDir -var env.iconsDir -out "obj\%iconsFiles%.wxs"
"%WIX%\bin\candle.exe" -arch x64 obj\%iconsFiles%.wxs -out obj\%iconsFiles%.wixobj
"%WIX%\bin\heat.exe" dir "%macrosDir%" -cg cgMacrosFiles -gg -scom -sreg -sfrag -srd -dr macrosDir -var env.macrosDir -out "obj\%macrosFiles%.wxs"
"%WIX%\bin\candle.exe" -arch x64 obj\%macrosFiles%.wxs -out obj\%macrosFiles%.wixobj
"%WIX%\bin\light.exe" %wixext% obj\%wixobjFileName% obj\%pythonFiles%.wixobj obj\%iconsFiles%.wixobj obj\%macrosFiles%.wixobj -out package\%msiFileName%

rd /S /Q "%binFolder%"
md "%binFolder%"
copy main.py "%binFolder%"
copy pageBrowse.py "%binFolder%"
copy pageMeasure.py "%binFolder%"
copy FolderWatch.py "%binFolder%"
copy CommandPipe.py "%binFolder%"
copy run.bat "%binFolder%"
robocopy "%pythonDir%" "%binFolder%\python" /s
robocopy "%iconsDir%" "%binFolder%\icons" /s
robocopy "%macrosDir%" "%binFolder%\macros" /s

"%ZIP%" a "package\%binFolder%.zip" "%binFolder%"

popd
endlocal
