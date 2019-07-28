# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

added_files = collect_data_files('tinycss2')
added_files += collect_data_files('reportlab')
extra_imports = ['tinycss2', 'reportlab']

a = Analysis(
    ['tekken_bot_prime.py'],
    binaries=[],
    datas=added_files,
    hiddenimports=extra_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(
    a.pure, a.zipped_data,
    cipher=block_cipher
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TekkenBotPrime',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False , icon='data\\tekken_bot_close.ico'
)
