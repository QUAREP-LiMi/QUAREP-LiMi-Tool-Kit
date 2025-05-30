# -*- mode: python ; coding: utf-8 -*-

# main.spec
# version 0.2.26
# this file can be used to pack the Quarep-Limi Tool Kit in a PyInstaller package
# usage: PyInstaller main.spec
# it was created by running PyInstaller once with the argument 'main.py'
# next the Analysis arguments were modified/added:
# - the list of the .py modules to include
# - the list of the extra data files (datas)
# - the list of the modules that were not detected automatically (hiddenimports)

#  the versions of the python modules are listed in python_upgrade.bat

a = Analysis(
    ['main.py', 'CommandPipe.py', 'DetectorPhotonCalibration.py', 'FolderWatch.py', 'forms.py', 'pageBrowse.py', 'pageDetectorResults.py', 'pageFeedback.py', 'pageHelp.py', 'pageLightSourceResults.py', 'pageMeasure.py', 'pageNoPage.py',  'wxApp.py' ],
    pathex=[],
    binaries=[],
    datas=[ ('icons', 'icons'), 
            ('macros', 'macros'), 
            ('vips', 'vips'), 
            ('lunasvg', 'lunasvg'), 
            ('caltool', 'caltool'), 
            ('nknd2info', 'nknd2info'), 
            ('SmartLPM', 'SmartLPM'), 
            ('cli_calibration_tool_help.txt', '.'), 
            ('*.html', '.'),
            ('Product.ico', '.'),
            ],
    hiddenimports=['pyvips','matplotlib.backends.backend_wxagg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QLTK',
)
