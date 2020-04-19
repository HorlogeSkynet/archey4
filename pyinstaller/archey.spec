# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

# build a list of `archey.entries` modules to tell PyInstaller to import
from glob import iglob
archey_entry_imports = ['archey.entries']
for path in iglob('archey/entries/*.py'):
    if not path.split('/')[-1].startswith('_'):
        archey_entry_imports.append(
            'archey.entries.{0}'.format(path.split('/')[-1][:-3])
        )

a = Analysis(['../archey/__main__.py'],
             pathex=['dist'],
             binaries=[],
             datas=[],
             hiddenimports=archey_entry_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='archey',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
