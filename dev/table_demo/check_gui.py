"""Run manually with a desktop session: python dev/table_demo/check_gui.py."""
import tkinter as tk
from tkinter import ttk
from main import TableDemo


root = tk.Tk()
root.geometry('1000x600+40+40')
app = TableDemo(root)
root.update()
try:
    # Invoke the actual row/column buttons after the parent is visible.
    for position in ({'row': 0, 'column': 1}, {'row': 2, 'column': 0}):
        button = app.grid_frame.grid_slaves(**position)[0]
        assert isinstance(button, ttk.Button)
        button.invoke()
        root.update()
        dialog = app.label_dialog
        assert dialog.winfo_viewable()
        assert root.grab_current() is None
        heartbeat = []
        root.after(0, lambda: heartbeat.append(True))
        root.update()
        assert heartbeat
        dialog.choose('fixed')
        dialog.values['text'].set('test')
        dialog.submit()
        root.update()
        assert not dialog.winfo_exists()
    app.open_labels('row', 1)
    root.update()
    dialog = app.label_dialog
    dialog.tk.call(dialog.protocol('WM_DELETE_WINDOW'))
    root.update()
    assert not dialog.winfo_exists()
    app.open_labels('column', 1)
    root.update()
    # Parent must be closable even while the label editor is open.
    root.destroy()
    print('Visible row/column buttons, event loop, add, dialog close, parent close: OK')
finally:
    try:
        root.destroy()
    except tk.TclError:
        pass
