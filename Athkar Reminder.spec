# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['athkar_reminder.py'],
    pathex=[],
    binaries=[],
    datas=[('duaas.json', '.'), ('settings.json', '.'), ('languages.py', '.'), ('version.py', '.')],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL.ImageDraw', 'pystray', 'win10toast', 'winreg', 'win32api', 'win32gui', 'win32con', 'pystray._win32'],
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
    a.binaries,
    a.datas,
    [],
    name='Athkar Reminder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
