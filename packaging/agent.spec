# PyInstaller spec for the AI Behavioral Guardian agent.
#
# MUST be built on Windows to produce a Windows .exe — PyInstaller does not
# cross-compile. Run build_agent.bat on a Windows machine (see that file).

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../behavioral_guardian/agent/agent_runner.py'],
    pathex=['..'],  # so `behavioral_guardian.*` absolute imports resolve
    binaries=[],
    datas=[],
    hiddenimports=[
        # pynput's Windows backend pulls these in dynamically, which
        # PyInstaller's static import scan can miss — spelling them out
        # here avoids a "no keyboard/mouse backend available" crash at
        # runtime that would otherwise only show up on someone else's
        # machine, not yours.
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'win32api',
        'win32con',
        'win32gui',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GuardianAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # keep a console window so the person can see the
                   # first-time login prompt (or the "already linked,
                   # sending data" log lines) — see build_agent.bat for
                   # the fully-silent alternative once it's trusted.
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
