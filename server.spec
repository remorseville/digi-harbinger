# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_dynamic_libs, copy_metadata, collect_data_files, collect_submodules
import os

block_cipher = None

added_files = [
    ('conftest.py', '.'),
    ('pytest.ini', '.'),
    ('tests/*', 'tests'),
    ('templates/*', 'templates'),
    ('templates/reports', 'templates/reports'),
    ('static/*', 'static'),
    ('static/css/*', 'static/css'),
]

hidden_imports = [
    'pytest',
    '_pytest',
    'pytest_html',
    'pluggy',
    'jinja2',
    'jinja2.ext',
    'pytest_asyncio',
]

hidden_imports += collect_submodules('pytest_metadata')
hidden_imports += collect_submodules('pytest_html')
hidden_imports += collect_submodules('pytest_timeout')
hidden_imports += collect_submodules('pyi_splash')

collected_data = []

collected_data += collect_data_files('pytest_metadata')
collected_data += collect_data_files('pytest_html')
collected_data += collect_data_files('pytest_timeout')

collected_data += copy_metadata('pytest_metadata')
collected_data += copy_metadata('pytest_html')
collected_data += copy_metadata('pytest_timeout')
collected_data += added_files




a = Analysis(
    ['server.py'],
    pathex=['.'],
    binaries=[],
    datas=collected_data,
    hiddenimports=hidden_imports,
    hookspath=['.'],
    hooksconfig={}, 
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

splash = Splash('logo.png',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(10, 0),
                text_size=8,
                text_color='black')

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,  
    [],
    #exclude_binaries=True,
    name='digi-harbinger',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='dh.ico'
)


#import shutil

#shutil.copyfile('conftest.py', '{0}/server/conftest.py'.format(DISTPATH))


