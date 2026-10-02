"""Visible end-to-end integration check with real inference and export."""
import sys
from pathlib import Path
import tempfile
import time
import tkinter as tk

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from dev.broad_table.main import BroadTable
from table.core import export_tables, load_tables

root = tk.Tk()
root.geometry('1400x850')
app = BroadTable(root)
failures = []
started = time.monotonic()
heartbeats = []
app.start_image(ROOT / 'broad_dectector/test_img/1.jpg')


def check():
    try:
        heartbeats.append(1)
        if app.busy:
            if time.monotonic() - started > 90:
                raise AssertionError('Inference timed out')
            root.after(100, check)
            return
        assert len(heartbeats) > 1, 'Background detection blocked event loop'
        assert app.original is not None and app.preview_photo is not None
        assert len(app.wells) == 96
        assert len(app.editor.sheets) == 2
        app.editor.open_labels('row', 3)
        dialog = app.editor.label_dialog
        dialog.choose('fixed')
        dialog.values['text'].set('check')
        dialog.submit()
        assert app.editor.sheet.labels[3, 1] == ['check']
        app.editor.apply_change(lambda: app.editor.sheet.set_cell(3, 2, 'edited'))
        app.editor.resize_sheet('row', 3)
        app.editor.undo()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'out.xlsx'
            export_tables(output, app.editor.sheets)
            assert load_tables(output)[0].rows[2][1] == 'edited 【check】'
        app.show_boxes.set(False)
        app.render_image()
        app.editor.try_load(ROOT / 'table/examples/samples.csv', load_tables)
        assert app.original is None and not app.wells
        print('Real inference, responsive UI, image preview, labels/edit/undo and export: OK')
    except Exception as exc:
        failures.append(exc)
    finally:
        if not app.busy or failures:
            app.editor.dirty = False
            app.close()


root.after(100, check)
root.mainloop()
if failures:
    raise failures[0]
