# Build from any working directory with PyInstaller.
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, copy_metadata

project = Path(SPECPATH).resolve()
root = project.parents[1]
datas, binaries, hiddenimports = collect_all('ultralytics')
datas += copy_metadata('ultralytics')
datas += [(str(root / 'broad_dectector/results/well_detection/weights/best.pt'),
           'broad_dectector/results/well_detection/weights')]
hiddenimports += ['xlrd', 'defusedxml.ElementTree', 'openpyxl', 'torchvision',
                  'table.core', 'table.main', 'dev.broad_table.pipeline',
                  'dev.broad_table.self_test', 'broad_dectector.scripts.process_wells']

a = Analysis([str(project / 'main.py')], pathex=[str(root)],
             binaries=binaries, datas=datas, hiddenimports=hiddenimports,
             hookspath=[], hooksconfig={}, runtime_hooks=[],
             excludes=['IPython', 'jupyter', 'notebook', 'pytest', 'tensorboard'],
             noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='broad_table',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=False)
