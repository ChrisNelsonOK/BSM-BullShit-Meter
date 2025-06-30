# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for BSM (BullShit Meter) application.
Builds platform-specific standalone executables.
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Determine platform-specific settings
if sys.platform == 'darwin':
    icon_file = 'assets/bsm.icns'
    bundle_name = 'BSM'
elif sys.platform == 'win32':
    icon_file = 'assets/bsm.ico'
    bundle_name = 'BSM.exe'
else:
    icon_file = 'assets/bsm.png'
    bundle_name = 'bsm'

# Collect all data files
datas = []
datas += collect_data_files('bsm')
datas += [('assets', 'assets')]
datas += [('README.md', '.')]
datas += [('LICENSE', '.')]

# Collect hidden imports
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'pynput',
    'pynput.keyboard',
    'pynput.mouse',
    'PIL',
    'PIL.Image',
    'PIL.ImageGrab',
    'cv2',
    'numpy',
    'pytesseract',
    'openai',
    'anthropic',
    'cryptography',
    'aiosqlite',
    'aiofiles',
    'markdown',
    'yaml',
]

# Add AI provider submodules
hiddenimports += collect_submodules('bsm.core.ai_providers')

a = Analysis(
    ['bsm/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'tkinter',
    ],
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
    name=bundle_name.replace('.exe', ''),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

# macOS specific bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name=f'{bundle_name}.app',
        icon=icon_file,
        bundle_identifier='com.bsm.app',
        info_plist={
            'CFBundleName': 'BSM - BullShit Meter',
            'CFBundleDisplayName': 'BSM',
            'CFBundleGetInfoString': "AI-powered fact checker and counter-argument generator",
            'CFBundleIdentifier': 'com.bsm.app',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSUIElement': False,  # Show in dock
            'NSAppleEventsUsageDescription': 'BSM needs to monitor keyboard events for hotkey functionality.',
            'NSSystemAdministrationUsageDescription': 'BSM needs accessibility permissions for global hotkeys.',
        },
    )
