"""Packaged smoke test: real model, imports, GUI, annotations and exports."""
import json
from pathlib import Path
import tempfile
import traceback


def run(image_path, report_path):
    root = None
    try:
        import tkinter as tk
        import xlrd
        from dev.broad_table.main import BroadTable
        from dev.broad_table.pipeline import DEFAULT_MODEL, extract_tables
        from table.core import export_tables, load_tables
        sheets, wells = extract_tables(image_path)
        root = tk.Tk()
        root.withdraw()
        app = BroadTable(root)
        app.editor.sheets = sheets
        app.editor.reset_choices()
        app.editor.apply_change(lambda: app.editor.sheet.annotate('row', 3, 2, 3, 'fixed', text='smoke'))
        root.update()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            export_tables(path / 'result.xlsx', sheets)
            assert '【smoke】' in load_tables(path / 'result.xlsx')[0].rows[2][1]
            export_tables(path / 'result.csv', [sheets[1]])
            assert load_tables(path / 'result.csv')[0].rows[0] == sheets[1].rows[0]
            (path / 'test.xml').write_text('<table><row><cell>ok</cell></row></table>', encoding='utf-8')
            assert load_tables(path / 'test.xml')[0].rows == [['ok']]
        result = {'ok': True, 'wells': len(wells), 'sheets': [s.name for s in sheets],
                  'bundled_model': DEFAULT_MODEL.is_file()}
    except Exception:
        result = {'ok': False, 'error': traceback.format_exc()}
    finally:
        if root is not None:
            root.destroy()
    Path(report_path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    if not result['ok']:
        raise SystemExit(1)
